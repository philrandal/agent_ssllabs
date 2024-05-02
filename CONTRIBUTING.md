# Contributing

If you have any issues or ideas for improvement you can contact me in the [CMK forum](https://forum.checkmk.com/) by sending me a direct message to `@thl-cmk` (this is the prefered way) or send an email to _thl-cmk[at]outlook[dot]com_.

Please include:
- your CMK version/edition
- your environment (stand alone or distributed)
- the OS of your CMK server(s)
- the version of the plugin
- the crash report (if any)

For agent based plugins I might need also the agent output of the plugin.
```
OMD[build]:~$ /omd/sites/build/local/share/check_mk/agents/special/agent_ssllabs --ssl-hosts thl-cmk.hopto.org,checkmk.com
<<<check_mk>>>
Version: 2.0.2
AgentOS: linux

<<<ssllabs_grade:sep(0)>>>
[{"host": "thl-cmk.hopto.org", "port": 443, "protocol": "http", "isPublic": true, "status": "READY", "startTime": 1714652035625, "testTime": 1714652126958, "engineVersion": "2.3.0", "criteriaVersion": "2009q", "endpoints": [{"ipAddress": "79.242.117.133", "serverName": "p4ff27585.dip0.t-ipconnect.de", "statusMessage": "Ready", "grade": "A+", "gradeTrustIgnored": "A+", "hasWarnings": false, "isExceptional": true, "progress": 100, "duration": 90894, "delegation": 1}], "from_agent_cache": true}, {"host": "checkmk.com", "port": 443, "protocol": "http", "isPublic": false, "status": "READY", "startTime": 1714649754235, "testTime": 1714649899247, "engineVersion": "2.3.0", "criteriaVersion": "2009q", "endpoints": [{"ipAddress": "2a0a:51c1:0:5:0:0:0:4", "serverName": "www.checkmk.com", "statusMessage": "Ready", "grade": "A+", "gradeTrustIgnored": "A+", "hasWarnings": false, "isExceptional": true, "progress": 100, "duration": 72455, "delegation": 1}, {"ipAddress": "45.133.11.28", "serverName": "www.checkmk.com", "statusMessage": "Ready", "grade": "A+", "gradeTrustIgnored": "A+", "hasWarnings": false, "isExceptional": true, "progress": 100, "duration": 72067, "delegation": 1}], "from_agent_cache": true}]
<<<>>>

```
