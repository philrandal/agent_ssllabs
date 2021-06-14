# Qualys SSL Labs REST API special agent

**Note: this package is for CheckMK version 2.x.**

This Agent uses die Qualys SSL Lab REST API.  For details about the API see https://github.com/ssllabs/ssllabs-scan/blob/master/ssllabs-api-docs-v3.md. To check a server manually go to https://www.ssllabs.com/ssltest/index.html.



Check Info:

* *services*: this check creates on service for each SSL server to check
* *state*: 
    * the check will go 'warn', 'crit' or 'ok' depending on the SSL server overall rating
    * the check will go 'warn', 'crit' or 'ok' depending on the laste time the SSL server check was running
    * the check will go 'warn' if the SSL server test is running
    * the check will go 'crit' on API errors
    * the check will go 'unknown' if the SSL server check has an unknown outcome.

* *wato*:
    * Overall rating and last run can be configured

* *perfdata*: none 

Sample output
![Sample](/doc/sample.png?raw=true "sample [SHORT TITLE]")

Sample wato
![wato](/doc/wato.png?raw=true "wato [SHORT TITLE]")


Sample agent output
