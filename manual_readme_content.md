[comment]: # " File: README.md"
[comment]: # ""
[comment]: # "    Copyright (c) Lansweeper, 2022"
[comment]: # ""
[comment]: # "    This unpublished material is proprietary to Lansweeper."
[comment]: # "    All rights reserved. The methods and"
[comment]: # "    techniques described herein are considered trade secrets"
[comment]: # "    and/or confidential. Reproduction or distribution, in whole"
[comment]: # "    or in part, is forbidden except by express written permission"
[comment]: # "    of Lansweeper."
[comment]: # ""
[comment]: # "    Licensed under the Apache License, Version 2.0 (the 'License');"
[comment]: # "    you may not use this file except in compliance with the License."
[comment]: # "    You may obtain a copy of the License at"
[comment]: # ""
[comment]: # "        http://www.apache.org/licenses/LICENSE-2.0"
[comment]: # ""
[comment]: # "    Unless required by applicable law or agreed to in writing, software distributed under"
[comment]: # "    the License is distributed on an 'AS IS' BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,"
[comment]: # "    either express or implied. See the License for the specific language governing permissions"
[comment]: # "    and limitations under the License."
[comment]: # ""
It is recommended to read the documentation for the app to understand the functioning of the actions
and the asset configuration or the action parameters associated with it. For further details, refer
to [Lansweeper Docs](https://docs.lansweeper.com/docs) .

## Port Details

The app uses HTTP/ HTTPS protocol for communicating with the Lansweeper server. Below are the
default ports used by the Splunk SOAR Connector.

| SERVICE NAME | TRANSPORT PROTOCOL | PORT |
|--------------|--------------------|------|
| http         | tcp                | 80   |
| https        | tcp                | 443  |

## Steps to Configure the Lansweeper Phantom app's asset

Follow these steps to configure the Lansweeper Phantom app's asset:

-   Log in to the Lansweeper platform.

      

    -   Once logged in, all available sites for your account are shown.
    -   Please select the sites for which you need to fetch the asset details.
    -   Go to **Developers tools** by clicking the user's profile logo (Settings).
    -   Click on **All applications** .
    -   Select the application type as **Personal Application**
    -   Enter the application name and click **ADD APPLICATION** .
    -   Now, Navigate to the created application from **All applications** .
    -   Click on the **Authorize** button and select the sites which you want to authorize.
    -   Copy the generated Application Identity Code.

-   Now, Log in to your Phantom instance.

      

    -   Navigate to the **Home** dropdown and select **Apps** .
    -   Search the Lansweeper App from the search box.
    -   Click on the **CONFIGURE NEW ASSET** button.
    -   Navigate to the **Asset Info** tab and enter the Asset name and Asset description.
    -   Navigate to the **Asset Settings** .
    -   Paste the generated **Application Identity Code** from Lansweeper UI to its respective
        configuration parameter.
    -   Save the asset.
    -   Now, test the connectivity of the Phantom server to the Lansweeper instance by clicking the
        **TEST CONNECTIVITY** button.

**Note:**

-   Please make sure to select the application type as **Personal Application** . The current
    integration will only support the Personal Application type.
-   Keep your 'Application Identity Code' secure.
-   API clients can use your 'Application Identity Code' to gain access to the APIs as your user.
    Keep this value somewhere safe and secure. Never share them with anyone.

## Explanation of the Asset Configuration Parameters

The asset configuration parameters affect 'test connectivity' and some other actions of the
application. The parameters related to test connectivity action is Application Identity Code.

-   **Application Identity Code:** Identity code for site data asset authorization.

## Explanation of the Lansweeper Actions' Parameters

-   ### Test Connectivity (Action Workflow Details)

    -   This action will test the connectivity of the Phantom server to the Lansweeper instance by
        making an initial API call using the provided asset configuration parameters.
    -   The action will internally store the details of the authorized sites (provided by the user
        in the authorization flow) in the state file. These sites will be used for fetching the
        asset details in other actions.
    -   The action validates the provided asset configuration parameters. Based on the API call
        response, the appropriate success and failure message will be displayed when the action gets
        executed.

-   ### List Authorized Sites

    In order to retrieve information from a specific site, the application has to have permission to
    access the information from such site. The goal of this action is to retrieve the list of the
    authorized sites with their names and ID(s), which the application has access to. The user can
    use the Site ID from the output response as an input to the Hunt MAC or the Hunt IP actions.
    This action also stores/updates the authorized sites stored in the state file.

    -   **Action Parameter** : No action parameters are required.
    -   **Examples:**
        -   Get the Authorized Site ID(s) with their names.
            -   No action parameters are required.

-   ### Hunt IP

    Fetch the details of the asset from the Lansweeper platform for the given Site ID and IP
    address. The Site ID can be retrieved from the output of the List Authorized Sites action. If
    the user leaves the Site ID field empty, the action will consider all the authorized sites as
    input which were stored in the state file during the test connectivity or list authorized sites
    action run. The paginator is implemented internally in this action which will paginate through
    the responses based on the assetPagination field. The max results per site parameter can be used
    to limit the output responses.

    -   **Action Parameter: Site ID**

          

        -   This parameter is the unique key for a particular site. A site is like a workspace
            inside Lansweeper. Users can create and join several sites, within the same account.
            This is an optional parameter in order to get the asset details for a particular site.
            The action will consider the authorized sites as input if the user leaves the Site ID
            field empty. It expects a comma-separated string as an input parameter. If any one of
            the Site IDs is invalid in the comma-separated string, the action will skip that Site ID
            and continue with the valid ones. An error message will be shown if all the Site IDs are
            invalid. The Site ID can be retrieved from the output of the List Authorized Sites
            action.

        **Note:**

        -   The user can only provide the sites that were authorized during the Test Connectivity
            flow, as an input parameter to Site ID.

    -   **Action Parameter: IP**

          

        -   This parameter is basically an IP address of the assets. While passing this parameter we
            expect to get the details of the asset which are associated with this IP address. It
            expects a comma-separated string as an input parameter. If any one of the IPs is invalid
            in the comma-separated string, the action will skip that IP address and continue with
            the valid ones. An error message will be shown if all the IP addresses are invalid. This
            is a required parameter.

    -   **Action Parameter: Max Results Per Site**

          

        -   This parameter allows the user to limit the number of results per site. It expects a
            numeric value as an input. The default value is 50 for which it will fetch the first 50
            assets from a particular site.

    -   **Examples:**
        -   List the asset details with the IP address '10.0.1.3' and consider all the authorized
            sites as input for the Site ID parameter.
            -   Site ID = ""
            -   IP = "10.0.1.3"

        <!-- -->

        -   List the asset details with the IP address '10.0.1.3' and Site ID
            '00d4ed4f-b2ad-4587-91b5-07bd453c5c76'.
            -   Site ID = "00d4ed4f-b2ad-4587-91b5-07bd453c5c76"
            -   IP = "10.0.1.3"

        <!-- -->

        -   List the asset details with the IP address '10.0.1.3' and Site ID
            '00d4ed4f-b2ad-4587-91b5-07bd453c5c76'. The results should also be limited to 15.

            -   Site ID = "00d4ed4f-b2ad-4587-91b5-07bd453c5c76"
            -   IP = "10.0.1.3"
            -   Max Results Per Site = 15

              
            **Note:** Max Results Per Site value will be handled internally, which will paginate
            through the assets for a particular site.

        <!-- -->

        -   List the asset details with the IP address '10.0.1.3' or '10.0.1.4' and Site ID
            '00d4ed4f-b2ad-4587-91b5-07bd453c5c76'. The results should also be limited to 50.

            -   Site ID = "00d4ed4f-b2ad-4587-91b5-07bd453c5c76"
            -   IP = "10.0.1.3, 10.0.1.4"
            -   Max Results Per Site = 50

              
            **Note:** Max Results Per Site value will be handled internally, which will paginate
            through the assets for a particular site.

        <!-- -->

        -   List the asset details with the IP address '10.0.1.3' and Site ID
            '00d4ed4f-b2ad-4587-91b5-07bd453c5c76' or '00d4ed4f-b2ad-4587-91b5-07bd453c5d23'. The
            results should also be limited to 50 for a particular site.

            -   Site ID = "00d4ed4f-b2ad-4587-91b5-07bd453c5c76,
                00d4ed4f-b2ad-4587-91b5-07bd453c5d23"
            -   IP = "10.0.1.3"
            -   Max Results Per Site = 50

              
            **Note:** Max Results Per Site value will be handled internally, which will paginate
            through the assets for a particular site.

-   ### Hunt MAC

    Fetch the details of the asset from the Lansweeper platform for the given Site ID and MAC
    address. The Site ID can be retrieved from the output of the List Authorized Sites action. If
    the user leaves the Site ID field empty, the action will consider all the authorized sites as
    input which were stored in the state file during the test connectivity or list authorized sites
    action run. The paginator is implemented internally in this action which will paginate through
    the responses based on the assetPagination field. The max results per site parameter can be used
    to limit the output responses.

    -   **Action Parameter: Site ID**

          

        -   This parameter is the unique key for a particular site. A site is like a workspace
            inside Lansweeper. Users can create and join several sites, within the same account.
            This is an optional parameter in order to get the asset details for a particular site.
            The action will consider the authorized sites as input if the user leaves the Site ID
            field empty. It expects a comma-separated string as an input parameter. If any one of
            the Site IDs is invalid in the comma-separated string, the action will skip that Site ID
            and continue with the valid ones. An error message will be shown if all the Site IDs are
            invalid. The Site ID can be retrieved from the output of the List Authorized Sites
            action.

        **Note:**

        -   The user can only provide the sites that were authorized during the Test Connectivity
            flow, as an input parameter to Site ID.

    -   **Action Parameter: MAC**

          

        -   This parameter is basically a MAC address of the assets. While passing this parameter we
            expect to get the details of the asset which are associated with this MAC address. It
            expects a comma-separated string as an input parameter. If any one of the MAC addresses
            is invalid in the comma-separated string, the action will skip that MAC address and
            continue with the valid ones. An error message will be shown if all the MAC addresses
            are invalid. This is a required parameter.

    -   **Action Parameter: Max Results Per Site**

          

        -   This parameter allows the user to limit the number of results. It expects a numeric
            value as an input. The default value is 50 for which it will fetch the first 50 assets
            from a particular site.

    -   **Examples:**
        -   List the asset details with the MAC address '68:FB:7E:71:00:00' and consider all the
            authorized sites as input for the Site ID parameter.
            -   Site ID = ""
            -   MAC = "68:FB:7E:71:00:00"

        <!-- -->

        -   List the asset details with the MAC address '68:FB:7E:71:00:00' and Site ID
            '00d4ed4f-b2ad-4587-91b5-07bd453c5c76'.
            -   Site ID = "00d4ed4f-b2ad-4587-91b5-07bd453c5c76"
            -   MAC = "68:FB:7E:71:00:00"

        <!-- -->

        -   List the asset details with the MAC address '68:FB:7E:71:00:00' and Site ID
            '00d4ed4f-b2ad-4587-91b5-07bd453c5c76'. The results should also be limited to 15.

            -   Site ID = "00d4ed4f-b2ad-4587-91b5-07bd453c5c76"
            -   MAC = "68:FB:7E:71:00:00"
            -   Max Results Per Site = 15

              
            **Note:** Max Results Per Site value will be handled internally, which will paginate
            through the assets for a particular site.

        <!-- -->

        -   List the asset details with the MAC address '68:FB:7E:71:00:00' or '68:FB:7E:71:00:01'
            and Site ID '00d4ed4f-b2ad-4587-91b5-07bd453c5c76'. The results should also be limited
            to 50.

            -   Site ID = "00d4ed4f-b2ad-4587-91b5-07bd453c5c76"
            -   MAC = "68:FB:7E:71:00:00, 68:FB:7E:71:00:01"
            -   Max Results Per Site = 50

              
            **Note:** Max Results Per Site value will be handled internally, which will paginate
            through the assets for a particular site.

        <!-- -->

        -   List the asset details with the MAC address '68:FB:7E:71:00:00' and Site ID
            '00d4ed4f-b2ad-4587-91b5-07bd453c5c76' or '00d4ed4f-b2ad-4587-91b5-07bd453c5d23'. The
            results should also be limited to 50 for a particular site.

            -   Site ID = "00d4ed4f-b2ad-4587-91b5-07bd453c5c76,
                00d4ed4f-b2ad-4587-91b5-07bd453c5d23"
            -   MAC = "68:FB:7E:71:00:00"
            -   Max Results Per Site = 50

              
            **Note:** Max Results Per Site value will be handled internally, which will paginate
            through the assets for a particular site.
