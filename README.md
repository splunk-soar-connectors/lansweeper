# Lansweeper

Publisher: Lansweeper \
Connector Version: 1.0.2 \
Product Vendor: Lansweeper \
Product Name: Lansweeper \
Minimum Product Version: 5.0.0

This app integrates with Lansweeper to perform investigative actions

### Configuration variables

This table lists the configuration variables required to operate Lansweeper. These variables are specified when configuring a Lansweeper asset in Splunk SOAR.

VARIABLE | REQUIRED | TYPE | DESCRIPTION
-------- | -------- | ---- | -----------
**identity_code** | required | password | Application Identity Code |

### Supported Actions

[test connectivity](#action-test-connectivity) - Validate the asset configuration for connectivity using supplied configuration \
[list authorized sites](#action-list-authorized-sites) - Retrieve authorized sites from Lansweeper with their ID(s) and names \
[hunt ip](#action-hunt-ip) - Fetch the details of the asset from the Lansweeper platform for the given site ID and IP address \
[hunt mac](#action-hunt-mac) - Fetch the details of the asset from the Lansweeper platform for the given site ID and MAC address

## action: 'test connectivity'

Validate the asset configuration for connectivity using supplied configuration

Type: **test** \
Read only: **True**

#### Action Parameters

No parameters are required for this action

#### Action Output

No Output

## action: 'list authorized sites'

Retrieve authorized sites from Lansweeper with their ID(s) and names

Type: **investigate** \
Read only: **True**

#### Action Parameters

No parameters are required for this action

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.data.\*.id | string | `lansweeper site id` | 56d4ed4f-b2ad-4587-91b5-07bd453c5a12 |
action_result.data.\*.name | string | | api-demo-data-v2 |
action_result.status | string | | success failed |
action_result.message | string | | Total sites: 1 |
action_result.summary.total_sites | numeric | | 1 |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'hunt ip'

Fetch the details of the asset from the Lansweeper platform for the given site ID and IP address

Type: **investigate** \
Read only: **True**

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**site_id** | optional | Site ID (allows comma-separated string) | string | `lansweeper site id` |
**ip** | required | IP address (allows comma-separated string) | string | `lansweeper ip` |
**max_results_per_site** | optional | Maximum number of assets to fetch per site. The default value is 50 | numeric | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.parameter.ip | string | `lansweeper ip` | 192.168.36.10 |
action_result.parameter.max_results_per_site | numeric | | 50 |
action_result.parameter.site_id | string | `lansweeper site id` | 56d4ed4f-b2ad-4587-91b5-06bd453c5c32 |
action_result.data.\*.\_id | string | | |
action_result.data.\*.assetBasicInfo.description | string | | Laptop |
action_result.data.\*.assetBasicInfo.domain | string | | WORKGROUP |
action_result.data.\*.assetBasicInfo.firstSeen | string | | 2019-01-31T11:40:22.187Z |
action_result.data.\*.assetBasicInfo.fqdn | string | | HYPERV2012E2.LAB02.test |
action_result.data.\*.assetBasicInfo.ipAddress | string | `lansweeper ip` | 10.0.1.72 |
action_result.data.\*.assetBasicInfo.lastSeen | string | | 2019-02-15T11:40:22.187Z |
action_result.data.\*.assetBasicInfo.mac | string | `lansweeper mac` | 00:0C:29:0A:3D:5F |
action_result.data.\*.assetBasicInfo.name | string | | Lansweeper2 iPhone iOS 12.1.0 FFG9 |
action_result.data.\*.assetBasicInfo.type | string | | Windows |
action_result.data.\*.assetBasicInfo.userDomain | string | | Lansweeper |
action_result.data.\*.assetBasicInfo.userName | string | | Administrator |
action_result.data.\*.assetCustom.manufacturer | string | | Dell Inc. |
action_result.data.\*.assetCustom.model | string | | VMware Virtual Platform |
action_result.data.\*.assetCustom.serialNumber | string | | 7LDDH2J |
action_result.data.\*.assetCustom.sku | string | | 16.04-LTS |
action_result.data.\*.site_name | string | | api-demo-data-v2 |
action_result.data.\*.url | string | `url` | https://app.lansweeper.com/api-demo-data-v2/asset/MTQ3My1Bc3NldC1mODdkZjg5MS1kNmVkLTQyYzgtYThmMS1jZDJmMTBlYmE1ZGU=/summary |
action_result.status | string | | success failed |
action_result.message | string | | Total assets: 2, Total sites: 2. Please refer the summary section in action result dictionary for more information. |
action_result.summary.authorized_site_ids | string | `lansweeper site id` | 56d4ed4f-b2ad-4587-91b5-06bd453c5c32 |
action_result.summary.invalid_ips | string | | 192..12.13 |
action_result.summary.total_assets | numeric | | 1 |
action_result.summary.unauthorized_site_ids | string | | 56d4ed4f-b2ad-4587-91b5-07bd453c5a12 |
action_result.summary.valid_ips | string | `lansweeper ip` | 10.0.1.72 |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'hunt mac'

Fetch the details of the asset from the Lansweeper platform for the given site ID and MAC address

Type: **investigate** \
Read only: **True**

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**site_id** | optional | Site ID (allows comma-separated string) | string | `lansweeper site id` |
**mac** | required | MAC address (allows comma-separated string) | string | `lansweeper mac` |
**max_results_per_site** | optional | Maximum number of assets to fetch per site. The default value is 50 | numeric | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.parameter.mac | string | `lansweeper mac` | 00:0C:29:0A:3D:5F |
action_result.parameter.max_results_per_site | numeric | | 50 |
action_result.parameter.site_id | string | `lansweeper site id` | 56d4ed4f-b2ad-4587-91b5-06bd453c5c32 |
action_result.data.\*.\_id | string | | |
action_result.data.\*.assetBasicInfo.description | string | | Laptop |
action_result.data.\*.assetBasicInfo.domain | string | | WORKGROUP |
action_result.data.\*.assetBasicInfo.firstSeen | string | | 2019-08-13T08:04:25.510Z |
action_result.data.\*.assetBasicInfo.fqdn | string | | HYPERV2012T3.LAB02.test |
action_result.data.\*.assetBasicInfo.ipAddress | string | `lansweeper ip` | 10.0.1.72 |
action_result.data.\*.assetBasicInfo.lastSeen | string | | 2019-11-04T09:59:05.080Z |
action_result.data.\*.assetBasicInfo.mac | string | `lansweeper mac` | 00:0C:29:0A:3D:5F |
action_result.data.\*.assetBasicInfo.name | string | | Lansweeper2 iPhone iOS 12.1.0 FFG9 |
action_result.data.\*.assetBasicInfo.type | string | | Windows |
action_result.data.\*.assetBasicInfo.userDomain | string | | Lansweeper |
action_result.data.\*.assetBasicInfo.userName | string | | Administrator |
action_result.data.\*.assetCustom.manufacturer | string | | Dell Inc. |
action_result.data.\*.assetCustom.model | string | | PowerEdge 2950 |
action_result.data.\*.assetCustom.serialNumber | string | | 7LDDH2J |
action_result.data.\*.assetCustom.sku | string | | 16.04-LTS |
action_result.data.\*.site_name | string | | api-demo-data-v2 |
action_result.data.\*.url | string | `url` | https://app.lansweeper.com/api-demo-data-v2/asset/MTQ5Mi1Bc3NldC1mODdkZjg5MS1kNmVkLTQyYzgtYThmMS1jZDJmMTBlYmE1ZGU=/summary |
action_result.status | string | | success failed |
action_result.message | string | | Total assets: 2, Total sites: 2. Please refer the summary section in action result dictionary for more information. |
action_result.summary.authorized_site_ids | string | `lansweeper site id` | 56d4ed4f-b2ad-4587-91b5-06bd453c5c32 |
action_result.summary.invalid_macs | string | | 00:0C:29:0A:3D |
action_result.summary.total_assets | numeric | | 1 |
action_result.summary.unauthorized_site_ids | string | | 56d4ed4f-b2ad-4587-91b5-07bd453c5a12 |
action_result.summary.valid_macs | string | `lansweeper mac` | 00:0C:29:0A:3D:5F |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

______________________________________________________________________

Auto-generated Splunk SOAR Connector documentation.

Copyright 2025 Splunk Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
