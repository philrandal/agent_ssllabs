[PACKAGE]: ../../raw/master/mkp/agent_ssllabs-2.0.3-20240516.mkp "agent_ssllabs-2.0.3-20240516.mkp"
# Qualys SSL Labs REST API special agent

This Agent uses die Qualys SSL Labs REST API to scan a list of servers for there SSL status. The plugin will check the given server and all end points reported by the SSL Labs scan.

For details about the API [see ssllabs/ssllabs-scan on GitHub](https://github.com/ssllabs/ssllabs-scan/blob/master/ssllabs-api-docs-v3.md).
 
To check a server manually go to [SSL Server Test](https://www.ssllabs.com/ssltest/index.html).

---
### Acnowlegement

This plugin is based based on the ssllabs plugin from Karsten Schoeke (karsten[dot]schoeke[at]geobasis-bb[dot]de) see [ssllabs api check](https://exchange.checkmk.com/p/ssllabs) on the CheckMK exchange.

---
### Check Info:

This check creates the service _**SSL Labs**_ with the checked server name as item. 

<details><summary>Montoring states</summary>

| State | condition | WATO | 
| ------ | ------ | ------ |
| WARN/CRIT | depending on grade reported | yes |
| WARN/CRIT | on old resulats | yes |
| WARN | no grade reported | yes |
| WARN | has warnings ws reported | yes |
| WARN | is not exceptional was reported | yes |
| OK | DNS resolfing was reported | yes |
| WARN | ERROR was reported | yes | 
| OK | IN_PROGRESS was reported | yes |

</details>

<details><summary>Perfdata</summary>

There are nor perfdata.

</details>

---
### WATO

<details><summary>Special agent rule</summary>

| Section | Rule name |
| ------ | ------ |
| Other integrations -> Applications | Qualys SSL Labs scan |

| Option | Defailt value | Comment |
| ------ | ------ | --- |
| SSL hosts to check | none | List of servers to scan |
| Connect Timeout | 30 | Time for the SSL Labs API to respond |
| proxy server, if required | none | Proxy server URL | 
| Publish results | off | SSL Labs results are public or not |
| Max Age for ssllbas.com cache | 1 Day | How long will the agent cache the results from SSL Labs |

</details> 

<details><summary>Service monitoring rules</summary>

| Section | Rule name |
| ------ | ------ |
| Networking | Qualys SSL Labs scan |


| Option | Defailt value | Comment |
| ------ | ------ | ---- | 
| Maximum age of ssllabs scan | 2/3 | Upper levels |
| grade level for ssllabs scan | none |  |
| Monitoring state if no grade was found | WARN |  |
| Monitoring state if host has warnings | WARN |  |
| Monitoring state if host is not exceptional | WARN | |
| Monitoring state if the check is in "DNS resolving" state | OK |
| Monitoring state if the check is in "ERROR" state | WARN | |
| Monitoring state if the check is in "IN_PROGRESS" state | OK | |
| Show result detail in the service details | Off | |

</details> 

<details><summary>Discovery rule</summary>
There is no discovery rule.
</details> 

<details><summary>HW/SW inventory rules</summary>
There is no inventory rule.
</details>

<details><summary>Special agent CLI usage</summary>

```
~$ ~/local/share/check_mk/agents/special/agent_ssllabs -h
usage: agent_ssllabs [-h] [--debug] [--verbose] [--vcrtrace TRACEFILE] --ssl-hosts SSL_HOSTS [--proxy PROXY] [--timeout TIMEOUT] [--publish {on,off}] [--max-age MAX_AGE]

This is a CKK special agent for the Qualys SSL Labs API to monitor SSL Certificate status

options:
  -h, --help            show this help message and exit
  --debug, -d           Enable debug mode (keep some exceptions unhandled)
  --verbose, -v
  --vcrtrace TRACEFILE, --tracefile TRACEFILE
                            If this flag is set to a TRACEFILE that does not exist yet, it will be created and
                            all requests the program sends and their corresponding answers will be recorded in said file.
                            If the file already exists, no requests are sent to the server, but the responses will be
                            replayed from the tracefile. 
  --ssl-hosts SSL_HOSTS
                        Comma separated list of FQDNs to test for
  --proxy PROXY         URL to HTTPS Proxy i.e.: https://192.168.1.1:3128
  --timeout TIMEOUT, -t TIMEOUT
                        API call timeout in seconds
  --publish {on,off}    Publish test results on ssllabs.com
  --max-age MAX_AGE     Maximum report age, in hours, if retrieving from "ssllabs.com" cache

Acnowlegement:
 This agent is based on the work by Karsten Schoeke karsten[dot]schoeke[at]geobasis-bb[dot]de
 see https://exchange.checkmk.com/p/ssllabs

```

</details>

---
### Download

* [Download latest mkp file][PACKAGE]

**Note**: before you update to a newer version, always check the [CHANGELOG](CHANGELOG). There might be incompatible changes.

---                   
### Installation

You can install the package by uploading it to your CheckMK site and as site user run 
```
mkp install PACKAGENAME-VERSION.mkp
```
or beginning with CMK2.2.x
```
mkp add PACKAGENAME-VERSION.mkp
mkp enable PACKAGENAME VERSION
```
In the non RAW editions of CheckMK you can use the GUI to install the package (_Setup_ -> _Extension Packages_ -> _Upload package_)

---
### Want to contribute?

Nice ;-) Have a look at the [contribution guidelines](CONTRIBUTING.md "Contributing")

---
### Sample output

![Sample](img/sample.png?raw=true "sample output")

![Sample details](img/sample-details.png?raw=true "sample details output")
