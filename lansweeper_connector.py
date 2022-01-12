# File: lansweeper_connector.py
#
# Copyright (c) 2022 Splunk Inc., Lansweeper
#
# This unpublished material is proprietary to Lansweeper.
# All rights reserved. The methods and
# techniques described herein are considered trade secrets
# and/or confidential. Reproduction or distribution, in whole
# or in part, is forbidden except by express written permission
# of Lansweeper.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions
# and limitations under the License.
#

import ipaddress
import json
import sys

import macaddress
import phantom.app as phantom
import requests
from bs4 import BeautifulSoup
from phantom.action_result import ActionResult
from phantom.base_connector import BaseConnector

# Local Imports
from lansweeper_consts import *


class RetVal(tuple):
    """Represent a class to create a tuple."""

    def __new__(cls, val1, val2=None):
        """Create a tuple from the provided values."""
        return tuple.__new__(RetVal, (val1, val2))


class MACAllowsTrailingDelimiters(macaddress.MAC):
    """Represent a subclass to define additional valid MAC formats."""

    other_valid_formats_allowed = (
        "xx xx xx xx xx xx",
        "xxx:xxx:xxx:xxx"
    )
    formats = macaddress.MAC.formats + other_valid_formats_allowed


class LansweeperConnector(BaseConnector):
    """
    Represent a connector module that implements the actions that are provided by the app.

    LansweeperConnector is a class that is derived from the BaseConnector class.
    """

    def __init__(self):
        """Initialize global variables."""
        # Call the BaseConnectors init first
        super(LansweeperConnector, self).__init__()

        self._state = {}
        self._authorized_sites = {}
        self._identity_code = None
        self._headers = {}

    def _get_error_message_from_exception(self, e):
        """
        Get appropriate error message from the exception.

        :param e: Exception object
        :return: error message
        """
        error_code = None
        error_msg = ERR_MSG_UNAVAILABLE

        try:
            if hasattr(e, "args"):
                if len(e.args) > 1:
                    error_code = e.args[0]
                    error_msg = e.args[1]
                elif len(e.args) == 1:
                    error_msg = e.args[0]
        except Exception:
            pass

        if not error_code:
            error_text = "Error Message: {}".format(error_msg)
        else:
            error_text = "Error Code: {}. Error Message: {}".format(error_code, error_msg)

        return error_text

    def _validate_integer(self, action_result, parameter, key, allow_zero=False):
        """
        Validate an integer.

        :param action_result: Action result or BaseConnector object
        :param parameter: input parameter
        :param key: input parameter message key
        :allow_zero: whether zero should be considered as valid value or not
        :return: status phantom.APP_ERROR/phantom.APP_SUCCESS, integer value of the parameter or None in case of failure
        """
        if parameter is not None:
            try:
                if not float(parameter).is_integer():
                    return (
                        action_result.set_status(phantom.APP_ERROR, LANSWEEPER_VALID_INT_MSG.format(param=key)),
                        None,
                    )

                parameter = int(parameter)
            except Exception:
                return action_result.set_status(phantom.APP_ERROR, LANSWEEPER_VALID_INT_MSG.format(param=key)), None

            # Negative value validation
            if parameter < 0:
                return action_result.set_status(phantom.APP_ERROR, LANSWEEPER_NON_NEG_INT_MSG.format(param=key)), None

            # Zero value validation
            if not allow_zero and parameter == 0:
                return (
                    action_result.set_status(phantom.APP_ERROR, LANSWEEPER_NON_NEG_NON_ZERO_INT_MSG.format(param=key)),
                    None,
                )

        return phantom.APP_SUCCESS, parameter

    def _is_ip(self, input_ip_address):
        """
        Validate given IP address and return True if address is valid IPv4 address.

        :param input_ip_address: IP address
        :return: True/False
        """
        try:
            # Validate IPv4 Address
            ipaddress.IPv4Address(input_ip_address)
        except Exception:
            return False
        return True

    def _is_mac(self, input_mac_address):
        """
        Validate given MAC address and return True if address is valid MAC address.

        :param input_mac_address: MAC address
        :return: True/False
        """
        try:
            # Validate MAC Address
            MACAllowsTrailingDelimiters(input_mac_address)
        except Exception:
            return False
        return True

    def _filter_comma_seperated_fields(self, action_result, field, key):
        """
        Filter the comma seperated values in the field. This method operates in 2 steps:

        1. Get list with comma as the seperator
        2. Filter empty values from the list

        :param action_result: Action result object
        :param field: input parameter
        :param key: input parameter message key
        :return: status phantom.APP_ERROR/phantom.APP_SUCCESS, filtered list or None in case of failure
        """
        fields_list = [value.strip() for value in field.split(",") if value.strip()]
        if not fields_list:
            return action_result.set_status(phantom.APP_ERROR, LANSWEEPER_ERR_INVALID_FIELDS.format(key=key)), None
        return phantom.APP_SUCCESS, fields_list

    def _process_empty_response(self, response, action_result):
        """
        Process empty response.

        :param response: response object
        :param action_result: object of Action Result
        :return: status phantom.APP_ERROR/phantom.APP_SUCCESS(along with appropriate message)
        """
        if response.status_code == 200 or response.status_code == 204:
            return RetVal(phantom.APP_SUCCESS, {})

        return RetVal(
            action_result.set_status(
                phantom.APP_ERROR, LANSWEEPER_ERR_EMPTY_RESPONSE.format(code=response.status_code)
            ),
            None,
        )

    def _process_html_response(self, response, action_result):
        """
        Process html response.

        :param response: response object
        :param action_result: object of Action Result
        :return: status phantom.APP_ERROR/phantom.APP_SUCCESS(along with appropriate message)
        """
        # An html response, treat it like an error
        status_code = response.status_code

        try:
            soup = BeautifulSoup(response.text, "html.parser")
            # Remove the script, style, footer and navigation part from the HTML message
            for element in soup(["script", "style", "footer", "nav"]):
                element.extract()
            error_text = soup.text
            split_lines = error_text.split("\n")
            split_lines = [x.strip() for x in split_lines if x.strip()]
            error_text = "\n".join(split_lines)
        except Exception:
            error_text = LANSWEEPER_UNABLE_TO_PARSE_ERR_DETAIL

        if not error_text:
            error_text = "Empty response and no information received"
        message = "Status Code: {}. Data from server: {}".format(status_code, error_text)

        message = message.replace("{", "{{").replace("}", "}}")
        return RetVal(action_result.set_status(phantom.APP_ERROR, message), None)

    def _process_json_response(self, r, action_result):
        """
        Process json response.

        :param r: response object
        :param action_result: object of Action Result
        :return: status phantom.APP_ERROR/phantom.APP_SUCCESS(along with appropriate message)
        """
        status_code = r.status_code
        # Try a json parse
        try:
            resp_json = r.json()
        except Exception as e:
            error_msg = self._get_error_message_from_exception(e)
            return RetVal(
                action_result.set_status(
                    phantom.APP_ERROR, LANSWEEPER_ERR_UNABLE_TO_PARSE_JSON_RESPONSE.format(error=error_msg)
                ),
                None,
            )

        errors = resp_json.get("errors", [])
        if errors and isinstance(errors, list):
            try:
                error_msg = ". ".join([error.get("message") for error in errors if error.get("message")])
                if error_msg:
                    message = "Error from server. Status Code: {}. Error Details: {}".format(status_code, error_msg)
                    return RetVal(action_result.set_status(phantom.APP_ERROR, message), None)
            except Exception:
                pass

        # Please specify the status codes here
        if 200 <= r.status_code < 399:
            return RetVal(phantom.APP_SUCCESS, resp_json)

        if resp_json.get("name") and resp_json.get("message"):
            message = "Error from server. Error Code: {}. Error Message: {}".format(
                resp_json["name"], resp_json["message"]
            )
            return RetVal(action_result.set_status(phantom.APP_ERROR, message), None)

        # You should process the error returned in the json
        error_text = r.text.replace("{", "{{").replace("}", "}}")
        message = "Error from server. Status Code: {}. Data from server: {}".format(status_code, error_text)

        return RetVal(action_result.set_status(phantom.APP_ERROR, message), None)

    def _process_response(self, r, action_result):
        """
        Process API response.

        :param r: response object
        :param action_result: object of Action Result
        :return: status phantom.APP_ERROR/phantom.APP_SUCCESS(along with appropriate message)
        """
        # store the r_text in debug data, it will get dumped in the logs if the action fails
        if hasattr(action_result, "add_debug_data"):
            action_result.add_debug_data({"r_status_code": r.status_code})
            action_result.add_debug_data({"r_text": r.text})
            action_result.add_debug_data({"r_headers": r.headers})

        # Process each 'Content-Type' of response separately

        # Process a json response
        if "json" in r.headers.get("Content-Type", ""):
            return self._process_json_response(r, action_result)

        # Process an HTML response, Do this no matter what the api talks.
        # There is a high chance of a PROXY in between phantom and the rest of
        # world, in case of errors, PROXY's return HTML, this function parses
        # the error and adds it to the action_result.
        if "html" in r.headers.get("Content-Type", ""):
            return self._process_html_response(r, action_result)

        # it's not content-type that is to be parsed, handle an empty response
        if not r.text:
            return self._process_empty_response(r, action_result)

        # everything else is actually an error at this point
        error_text = r.text.replace("{", "{{").replace("}", "}}")
        message = "Can't process response from server. Status Code: {} Data from server: {}".format(
            r.status_code, error_text
        )

        return RetVal(action_result.set_status(phantom.APP_ERROR, message), None)

    def _save_authorized_sites(self, action_result):
        """
        Save authorized sites.

        :param action_result: Object of ActionResult class
        :return: status(phantom.APP_SUCCESS/phantom.APP_ERROR)
        """
        # Retreive the list of authorized sites from action result
        authorized_sites = action_result.get_data()

        # Saving the authorized sites data in the state file
        authorized_sites_dict = {}
        try:
            for site in authorized_sites:
                authorized_sites_dict[site["id"]] = site["name"]
        except Exception:
            return action_result.set_status(phantom.APP_ERROR, LANSWEEPER_ERR_PROCESSING_AUTH_SITE_RESPONSE)

        self._state[LANSWEEPER_AUTH_SITES_STRING] = authorized_sites_dict

        # Save state
        self.save_state(self._state)

        self._state = self.load_state()

        # If the corresponding state file does not have the correct owner, owner group or permissions,
        # the authorized sites is not saved in the state file. So, we need to verify the sites list from
        # action result and site list from the saved state file are same or not.

        if authorized_sites_dict != self._state.get(LANSWEEPER_AUTH_SITES_STRING, {}):
            error_msg = LANSWEEPER_ERR_INVALID_PERMISSION_STATE_FILE.format(data="authorized sites")
            return action_result.set_status(phantom.APP_ERROR, error_msg)

        return action_result.set_status(phantom.APP_SUCCESS)

    def _make_rest_call(
        self, url, action_result, headers=None, params=None, data=None, json=None, method="get", verify=True
    ):
        """
        Make the REST call to the app.

        :param url: URL of the resource
        :param action_result: object of ActionResult class
        :param headers: request headers
        :param params: request parameters
        :param data: request body
        :param json: JSON object
        :param method: GET/POST/PUT/DELETE/PATCH (Default will be GET)
        :param verify: Verify server certificate
        :return: status phantom.APP_ERROR/phantom.APP_SUCCESS(along with appropriate message),
        response obtained by making an API call
        """
        if not headers:
            headers = self._headers
        resp_json = None

        try:
            request_func = getattr(requests, method)
        except AttributeError:
            return RetVal(action_result.set_status(phantom.APP_ERROR, "Invalid method: {}".format(method)), resp_json)

        try:
            r = request_func(url, verify=verify, data=data, json=json, headers=headers, params=params, timeout=60)
        except requests.exceptions.InvalidURL as e:
            self.debug_print(self._get_error_message_from_exception(e))
            return RetVal(
                action_result.set_status(phantom.APP_ERROR, LANSWEEPER_ERR_INVALID_URL.format(url=url)), resp_json
            )
        except requests.exceptions.InvalidSchema as e:
            self.debug_print(self._get_error_message_from_exception(e))
            return RetVal(
                action_result.set_status(phantom.APP_ERROR, LANSWEEPER_ERR_INVALID_SCHEMA.format(url=url)), resp_json
            )
        except Exception as e:
            error_msg = self._get_error_message_from_exception(e)
            return RetVal(
                action_result.set_status(
                    phantom.APP_ERROR, LANSWEEPER_ERR_CONNECTING_TO_SERVER.format(error=error_msg)
                ),
                resp_json,
            )

        return self._process_response(r, action_result)

    def _handle_test_connectivity(self, param):
        """
        Validate the asset configuration for connectivity using supplied configuration.

        :param param: dictionary of input parameters
        :return: status(phantom.APP_SUCCESS/phantom.APP_ERROR)
        """
        action_result = self.add_action_result(ActionResult(dict(param)))

        self.save_progress("Retrieving authorized sites...")
        ret_val = self._handle_list_authorized_sites(param, action_result)
        if phantom.is_fail(ret_val):
            self.save_progress(LANSWEEPER_ERR_TEST_CONN_FAILED)
            return action_result.get_status()

        self.save_progress("Sites retrieved successfully")
        self.save_progress(LANSWEEPER_SUCC_TEST_CONN_PASSED)
        return action_result.set_status(phantom.APP_SUCCESS)

    def _handle_list_authorized_sites(self, param, action_result=None):
        """
        List authorized sites.

        :param param: dictionary of input parameters
        :param action_result: Object of ActionResult class
        :return: status(phantom.APP_SUCCESS/phantom.APP_ERROR)
        """
        if not action_result:
            action_result = self.add_action_result(ActionResult(dict(param)))

        query = """query {
            authorizedSites {
                sites {
                    id
                    name
                }
            }
        }"""

        ret_val, response = self._make_rest_call(
            action_result=action_result, url=LANSWEEPER_QUERY_ENDPOINT, json={"query": query}, method="post"
        )
        if phantom.is_fail(ret_val):
            self._state.pop(LANSWEEPER_AUTH_SITES_STRING, None)
            return action_result.get_status()

        total = 0
        for site in response.get("data", {}).get("authorizedSites", {}).get("sites", []):
            total += 1
            action_result.add_data(site)

        # Save authorized sites in the state file
        ret_val = self._save_authorized_sites(action_result)
        if phantom.is_fail(ret_val):
            self._state.pop(LANSWEEPER_AUTH_SITES_STRING, None)
            return action_result.get_status()

        if total == 0:
            self.save_progress("No authorized sites found")
            return action_result.set_status(phantom.APP_SUCCESS, "No authorized sites found")
        action_result.update_summary({"total_sites": total})

        return action_result.set_status(phantom.APP_SUCCESS)

    def _paginator(self, action_result, endpoint, query, variables, max_results):
        """
        Fetch all the assets using pagination logic.

        :param action_result: object of ActionResult class
        :param endpoint: REST endpoint that needs to appended to the service address
        :param query: query to be passed while calling the API
        :param variables: variables to be considered while calling the API
        :param max_results: maximum number of results to be fetched
        :return: status phantom.APP_ERROR/phantom.APP_SUCCESS, successfully fetched results or None in case of failure
        """
        items_list = list()
        while True:
            # Make rest call
            ret_val, response = self._make_rest_call(
                action_result=action_result,
                url=LANSWEEPER_QUERY_ENDPOINT,
                json={"query": query, "variables": variables},
                method="post"
            )
            if phantom.is_fail(ret_val):
                return action_result.get_status(), []

            items = response.get("data", {}).get("site", {}).get("assetResources", {}).get("items", [])
            # No more items to be fetched. Hence, exit the paginator.
            if not items:
                break

            # Extending the items list
            items_list.extend(items)

            # Max results fetched. Hence, exit the paginator.
            if len(items_list) >= max_results:
                return phantom.APP_SUCCESS, items_list[:max_results]

            # Items fetched is less than the default limit, which means there is no more data to be processed
            if len(items) < LANSWEEPER_DEFAULT_PAGE_LIMIT:
                break

            # If cursor for next page is not available, exit the paginator.
            cursor = (
                response.get("data", {}).get("site", {}).get("assetResources", {}).get("pagination", {}).get("next")
            )
            if not cursor:
                break

            # Create pagination variables for next call
            variables = {
                "pagination": {
                    "limit": LANSWEEPER_DEFAULT_PAGE_LIMIT,
                    "cursor": cursor,
                    "page": "NEXT",
                }
            }

        return phantom.APP_SUCCESS, items_list

    def _get_sites(self, action_result, site_id):
        """
        Fetch authorized sites.

        :param action_result: object of ActionResult class
        :param site_id: Site ID
        :return: status(phantom.APP_SUCCESS/phantom.APP_ERROR), sites, authorized_site_ids, unauthorized_site_ids
        """
        authorized_site_ids = []
        unauthorized_site_ids = []
        sites = {}
        if not self._authorized_sites:
            return (
                action_result.set_status(phantom.APP_ERROR, LANSWEEPER_ERR_NO_AUTHORIZED_SITES_FOUND),
                sites,
                authorized_site_ids,
                unauthorized_site_ids,
            )

        if not site_id:
            sites = self._authorized_sites
            authorized_site_ids.extend(list(self._authorized_sites.keys()))
        else:
            ret_val, site_id_list = self._filter_comma_seperated_fields(action_result, site_id, "site_id")
            if phantom.is_fail(ret_val):
                return action_result.get_status(), sites, authorized_site_ids, unauthorized_site_ids

            for site_id in site_id_list:
                if site_id in self._authorized_sites:
                    sites[site_id] = self._authorized_sites.get(site_id)
                    authorized_site_ids.append(site_id)
                else:
                    unauthorized_site_ids.append(site_id)
                    self.debug_print("Site ID '{}' is not authorized".format(site_id))

            if not sites:
                return (
                    action_result.set_status(phantom.APP_ERROR, LANSWEEPER_ERR_INVALID_SITE_IDS),
                    sites,
                    authorized_site_ids,
                    unauthorized_site_ids,
                )

        return phantom.APP_SUCCESS, sites, authorized_site_ids, unauthorized_site_ids

    def _handle_hunt_ip(self, param):
        """
        Fetch asset details based on the IP address.

        :param param: dictionary of input parameters
        :return: status(phantom.APP_SUCCESS/phantom.APP_ERROR)
        """
        action_result = self.add_action_result(ActionResult(dict(param)))

        site_ids = param.get("site_id")
        # Get sites
        ret_val, sites, authorized_site_ids, unauthorized_site_ids = self._get_sites(action_result, site_ids)
        if phantom.is_fail(ret_val):
            return action_result.get_status()

        # Integer validation for 'max_results_per_site' action parameter
        max_results_per_site = param.get("max_results_per_site", LANSWEEPER_DEFAULT_LIMIT)
        ret_val, max_results_per_site = self._validate_integer(
            action_result, max_results_per_site, "max_results_per_site"
        )
        if phantom.is_fail(ret_val):
            return action_result.get_status()

        # Convert the comma separated IP(s) into list
        comma_separated_ips = param["ip"]
        ret_val, ip_list = self._filter_comma_seperated_fields(action_result, comma_separated_ips, "ip")
        if phantom.is_fail(ret_val):
            return action_result.get_status()

        # Validate and filter IP addresses
        valid_ips = []
        invalid_ips = []
        ip_condition_string = ""
        for ip in ip_list:
            if self._is_ip(ip):
                valid_ips.append(ip)
                ip_condition_string += (
                    """{
                    operator: EQUAL,
                    path: "assetBasicInfo.ipAddress",
                    value: "%s"
                },"""
                    % ip
                )
            else:
                invalid_ips.append(ip)
                self.debug_print(LANSWEEPER_ERR_INVALID_IP.format(ip=ip))

        # If all IP(s) are invalid, exit the code
        if not ip_condition_string:
            return action_result.set_status(phantom.APP_ERROR, LANSWEEPER_ERR_INVALID_FIELDS.format(key="ip"))

        # Remove the comma from the last condition
        ip_condition_string = ip_condition_string.rstrip(",")
        total_items = 0

        for site_id, site_name in sites.items():

            # Create query
            query = """query getAssetResources($pagination: AssetsPaginationInputValidated) {
                site(id: "%s") {
                    assetResources (
                        assetPagination: $pagination,
                        fields: [
                            "assetBasicInfo.name",
                            "assetBasicInfo.domain",
                            "assetBasicInfo.userName",
                            "assetBasicInfo.userDomain",
                            "assetBasicInfo.fqdn",
                            "assetBasicInfo.description",
                            "assetBasicInfo.type",
                            "assetBasicInfo.mac",
                            "assetBasicInfo.ipAddress",
                            "assetBasicInfo.firstSeen"
                            "assetBasicInfo.lastSeen"
                            "assetCustom.model",
                            "assetCustom.serialNumber",
                            "assetCustom.manufacturer",
                            "assetCustom.sku",
                            "url"
                        ],
                        filters: {
                            conjunction: OR,
                            conditions: [%s]
                        }
                    ) {
                        total
                        pagination {
                            limit
                            current
                            next
                            page
                        }
                        items
                    }
                }
            }""" % (
                site_id,
                ip_condition_string
            )

            variables = {
                "pagination": {
                    "limit": min(max_results_per_site, LANSWEEPER_DEFAULT_PAGE_LIMIT),
                    "page": "FIRST"
                }
            }

            # make rest call
            ret_val, items = self._paginator(
                action_result=action_result,
                endpoint=LANSWEEPER_QUERY_ENDPOINT,
                query=query,
                variables=variables,
                max_results=max_results_per_site,
            )

            if phantom.is_fail(ret_val):
                return action_result.get_status()

            for item in items:
                item["site_name"] = site_name
                action_result.add_data(item)
            total_items += len(items)

        action_result.update_summary(
            {
                "total_assets": total_items,
                "authorized_site_ids": authorized_site_ids,
                "unauthorized_site_ids": unauthorized_site_ids,
                "valid_ips": valid_ips,
                "invalid_ips": invalid_ips
            }
        )
        if total_items == 0:
            return action_result.set_status(phantom.APP_SUCCESS, "No assets found for the given IP address")

        message = "Total assets: {}, Total sites: {}.".format(
            total_items,
            len(authorized_site_ids) + len(unauthorized_site_ids)
        )
        message += " Please refer to the summary in the action result dictionary for more information."

        return action_result.set_status(phantom.APP_SUCCESS, message)

    def _handle_hunt_mac(self, param):
        """
        Fetch asset details based on the MAC address.

        :param param: dictionary of input parameters
        :return: status(phantom.APP_SUCCESS/phantom.APP_ERROR)
        """
        action_result = self.add_action_result(ActionResult(dict(param)))

        site_ids = param.get("site_id")
        # Get sites
        ret_val, sites, authorized_site_ids, unauthorized_site_ids = self._get_sites(action_result, site_ids)
        if phantom.is_fail(ret_val):
            return action_result.get_status()

        # Integer validation for 'max_results_per_site' action parameter
        max_results_per_site = param.get("max_results_per_site", LANSWEEPER_DEFAULT_LIMIT)
        ret_val, max_results_per_site = self._validate_integer(
            action_result, max_results_per_site, "max_results_per_site"
        )
        if phantom.is_fail(ret_val):
            return action_result.get_status()

        # Convert the comma separated MAC(s) into list
        comma_separated_macs = param["mac"]
        ret_val, mac_list = self._filter_comma_seperated_fields(action_result, comma_separated_macs, "mac")
        if phantom.is_fail(ret_val):
            return action_result.get_status()

        # Validate and filter MAC addresses
        valid_macs = []
        invalid_macs = []
        mac_condition_string = ""
        for mac in mac_list:
            if self._is_mac(mac):
                valid_macs.append(mac)
                mac_condition_string += (
                    """{
                    operator: EQUAL,
                    path: "assetBasicInfo.mac",
                    value: "%s"
                },"""
                    % mac
                )
            else:
                invalid_macs.append(mac)
                self.debug_print(LANSWEEPER_ERR_INVALID_MAC.format(mac=mac))

        # If all MAC(s) are invalid, exit the code
        if not mac_condition_string:
            return action_result.set_status(phantom.APP_ERROR, LANSWEEPER_ERR_INVALID_FIELDS.format(key="mac"))

        # Remove the comma from the last condition
        mac_condition_string = mac_condition_string.rstrip(",")

        total_items = 0

        for site_id, site_name in sites.items():

            # Create query
            query = """query getAssetResources($pagination: AssetsPaginationInputValidated) {
                site(id: "%s") {
                    assetResources (
                        assetPagination: $pagination,
                        fields: [
                            "assetBasicInfo.name",
                            "assetBasicInfo.domain",
                            "assetBasicInfo.userName",
                            "assetBasicInfo.userDomain",
                            "assetBasicInfo.fqdn",
                            "assetBasicInfo.description",
                            "assetBasicInfo.type",
                            "assetBasicInfo.mac",
                            "assetBasicInfo.ipAddress",
                            "assetBasicInfo.firstSeen"
                            "assetBasicInfo.lastSeen"
                            "assetCustom.model",
                            "assetCustom.serialNumber",
                            "assetCustom.manufacturer",
                            "assetCustom.sku",
                            "url"
                        ],
                        filters: {
                            conjunction: OR,
                            conditions: [%s]
                        }
                    ) {
                        total
                        pagination {
                            limit
                            current
                            next
                            page
                        }
                        items
                    }
                }
            }""" % (
                site_id,
                mac_condition_string
            )

            variables = {
                "pagination": {
                    "limit": min(max_results_per_site, LANSWEEPER_DEFAULT_PAGE_LIMIT),
                    "page": "FIRST"
                }
            }

            # make rest call
            ret_val, items = self._paginator(
                action_result=action_result,
                endpoint=LANSWEEPER_QUERY_ENDPOINT,
                query=query,
                variables=variables,
                max_results=max_results_per_site,
            )

            if phantom.is_fail(ret_val):
                return action_result.get_status()

            for item in items:
                item["site_name"] = site_name
                action_result.add_data(item)
            total_items += len(items)

        action_result.update_summary(
            {
                "total_assets": total_items,
                "authorized_site_ids": authorized_site_ids,
                "unauthorized_site_ids": unauthorized_site_ids,
                "valid_macs": valid_macs,
                "invalid_macs": invalid_macs
            }
        )
        if total_items == 0:
            return action_result.set_status(phantom.APP_SUCCESS, "No assets found for the given MAC address")

        message = "Total assets: {}, Total sites: {}.".format(
            total_items,
            len(authorized_site_ids) + len(unauthorized_site_ids)
        )
        message += " Please refer to the summary in the action result dictionary for more information."

        return action_result.set_status(phantom.APP_SUCCESS, message)

    def handle_action(self, param):
        """
        Get current action identifier and call member function of its own to handle the action.

        :param param: dictionary which contains information about the actions to be executed
        :return: status success/failure
        """
        # Get the action that we are supposed to execute for this App Run
        action = self.get_action_identifier()
        ret_val = phantom.APP_SUCCESS

        self.debug_print("action_id: {}".format(self.get_action_identifier()))

        # Dictionary mapping each action with its corresponding actions
        action_mapping = {
            "test_connectivity": self._handle_test_connectivity,
            "list_authorized_sites": self._handle_list_authorized_sites,
            "hunt_ip": self._handle_hunt_ip,
            "hunt_mac": self._handle_hunt_mac,
        }

        if action in action_mapping.keys():
            action_function = action_mapping[action]
            ret_val = action_function(param)

        return ret_val

    def initialize(self):
        """
        Initialize the global variables with its value and validate it.

        This is an optional function that can be implemented by the AppConnector derived class. Since the
        configuration dictionary is already validated by the time this function is called, it's a good place to do any
        extra initialization of any internal modules. This function MUST return a value of either phantom.APP_SUCCESS or
        phantom.APP_ERROR. If this function returns phantom.APP_ERROR, then AppConnector::handle_action will not get
        called.

        :return: status (success/failure)
        """
        # Load the state in initialize, use it to store data
        # that needs to be accessed across actions
        self._state = self.load_state()

        if not isinstance(self._state, dict):
            self.debug_print("Resetting the state file with the default format")
            self._state = {"app_version": self.get_app_json().get("app_version")}
            return self.set_status(phantom.APP_ERROR, LANSWEEPER_STATE_FILE_CORRUPT_ERR)

        # get the asset config
        config = self.get_config()
        self._identity_code = config['identity_code']

        # Get the list of stored authorized sites in the state file
        self._authorized_sites = self._state.get(LANSWEEPER_AUTH_SITES_STRING, {})

        # Initialize headers
        self._headers = {
            "Content-Type": "application/json",
            "Authorization": LANSWEEPER_AUTHORIZATION_HEADER.format(identity_code=self._identity_code)
        }

        return phantom.APP_SUCCESS

    def finalize(self):
        """
        Perform some final operations or clean up operations.

        This function gets called once all the param dictionary elements are looped over and no more handle_action
        calls are left to be made. It gives the AppConnector a chance to loop through all the results that were
        accumulated by multiple handle_action function calls and create any summary if required. Another usage is
        cleanup, disconnect from remote devices etc.

        :return: status (success/failure)
        """
        # Save the state, this data is saved across actions and app upgrades
        self.save_state(self._state)

        return phantom.APP_SUCCESS


def main():
    import argparse

    import pudb

    pudb.set_trace()

    argparser = argparse.ArgumentParser()

    argparser.add_argument("input_test_json", help="Input Test JSON file")
    argparser.add_argument("-u", "--username", help="username", required=False)
    argparser.add_argument("-p", "--password", help="password", required=False)

    args = argparser.parse_args()
    session_id = None

    username = args.username
    password = args.password

    if username is not None and password is None:

        # User specified a username but not a password, so ask
        import getpass

        password = getpass.getpass("Password: ")

    if username and password:
        try:
            login_url = LansweeperConnector._get_phantom_base_url() + "/login"

            print("Accessing the Login page")
            r = requests.get(login_url, verify=False, timeout=60)  # nosemgrep
            csrftoken = r.cookies["csrftoken"]

            data = dict()
            data["username"] = username
            data["password"] = password
            data["csrfmiddlewaretoken"] = csrftoken

            headers = dict()
            headers["Cookie"] = "csrftoken=" + csrftoken
            headers["Referer"] = login_url

            print("Logging into Platform to get the session id")
            r2 = requests.post(login_url, verify=False, data=data, headers=headers, timeout=60)  # nosemgrep
            session_id = r2.cookies["sessionid"]
        except Exception as e:
            print("Unable to get session id from the platform. Error: " + str(e))
            sys.exit(1)

    with open(args.input_test_json) as f:
        in_json = f.read()
        in_json = json.loads(in_json)
        print(json.dumps(in_json, indent=4))

        connector = LansweeperConnector()
        connector.print_progress_message = True

        if session_id is not None:
            in_json["user_session_token"] = session_id
            connector._set_csrf_info(csrftoken, headers["Referer"])

        ret_val = connector._handle_action(json.dumps(in_json), None)
        print(json.dumps(json.loads(ret_val), indent=4))

    sys.exit(0)


if __name__ == "__main__":
    main()
