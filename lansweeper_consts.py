# File: lansweeper_consts.py
#
# Copyright (c) Lansweeper, 2022
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

LANSWEEPER_AUTH_SITES_STRING = "authorized_sites"
LANSWEEPER_AUTHORIZATION_HEADER = "Token {identity_code}"
LANSWEEPER_DEFAULT_PAGE_LIMIT = 500
LANSWEEPER_DEFAULT_LIMIT = 50

# Endpoints
LANSWEEPER_QUERY_ENDPOINT = "https://api.lansweeper.com/api/v2/graphql"

# Constants relating to 'get_error_message_from_exception'
ERR_MSG_UNAVAILABLE = "Error message unavailable. Please check the asset configuration and|or action parameters."

# Constants relating to 'validate_integer'
LANSWEEPER_VALID_INT_MSG = "Please provide a valid integer value in the '{param}' action parameter"
LANSWEEPER_NON_NEG_NON_ZERO_INT_MSG = (
    "Please provide a valid non-zero positive integer value in the '{param}' action parameter"
)
LANSWEEPER_NON_NEG_INT_MSG = "Please provide a valid non-negative integer value in the '{param}' action parameter"

# Constants relating to success messages
LANSWEEPER_SUCC_TEST_CONN_PASSED = "Test Connectivity Passed"

# Constants relating to error messages
LANSWEEPER_ERR_EMPTY_RESPONSE = "Status Code {code}. Empty response and no information in the header."
LANSWEEPER_UNABLE_TO_PARSE_ERR_DETAIL = "Cannot parse error details"
LANSWEEPER_ERR_UNABLE_TO_PARSE_JSON_RESPONSE = "Unable to parse response as JSON. {error}"
LANSWEEPER_ERR_INVALID_URL = "Error connecting to server. Invalid URL: '{url}'"
LANSWEEPER_ERR_INVALID_SCHEMA = "Error connecting to server. No connection adapters were found for '{url}' URL."
LANSWEEPER_ERR_CONNECTING_TO_SERVER = "Error connecting to server. Details: {error}"
LANSWEEPER_ERR_TEST_CONN_FAILED = "Test Connectivity Failed"
LANSWEEPER_ERR_NO_AUTHORIZED_SITES_FOUND = (
    "No authorized sites found. "
    "Please run test connectivity or list authorized sites action first."
)
LANSWEEPER_ERR_INVALID_SITE_IDS = (
    "No authorized sites found for the given 'site_id' action parameter. "
    "Please run list authorized sites action to check the valid inputs for this parameter."
)
LANSWEEPER_ERR_PROCESSING_AUTH_SITE_RESPONSE = (
    "Error occurred while processing the authorized sites response from the server"
)
LANSWEEPER_ERR_INVALID_FIELDS = "Please provide a valid value in the '{key}' action parameter"
LANSWEEPER_ERR_INVALID_IP = (
    "IP validation failed for '{ip}'. Hence, skipping this IP address from being added to the conditions string."
)
LANSWEEPER_ERR_INVALID_MAC = (
    "MAC validation failed for '{mac}'. Hence, skipping this MAC address from being added to the conditions string."
)

# State file error messages
LANSWEEPER_ERR_INVALID_PERMISSION_STATE_FILE = (
    "Error occurred while saving the {data} in the state file. "
    "Please check the permissions of the state file. "
    "The Phantom user should have the correct access rights and ownership for the corresponding state file."
)
LANSWEEPER_STATE_FILE_CORRUPT_ERR = (
    "Error occurred while loading the state file due to its unexpected format. "
    "Resetting the state file with the default format. Please try again."
)
