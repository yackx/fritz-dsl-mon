
uiPass

response=d6bbffa4-e5c47474bcc32ad59266ab8ef3c63c24
lp=dslOv
username


Host: 192.168.1.1
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:64.0) Gecko/20100101 Firefox/64.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Referer: http://192.168.1.1/
Content-Type: application/x-www-form-urlencoded
Content-Length: 69
DNT: 1
Connection: keep-alive
Upgrade-Insecure-Requests: 1



JSON with general info (not all)
curl 'http://192.168.1.1/data.lua' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:64.0) Gecko/20100101 Firefox/64.0' -H 'Accept: */*' -H 'Accept-Language: en-US,en;q=0.5' --compressed -H 'Referer: http://192.168.1.1/' -H 'Content-Type: application/x-www-form-urlencoded' -H 'DNT: 1' -H 'Connection: keep-alive' --data 'xhr=1&sid=e8f7c80b709ff3e3&lang=en&page=overview&xhrId=all&useajax=1&no_sidrenew='

08dc2038a4cddc35



http://192.168.1.1/data.lua avec page=dslStat


<form id="main_form" method="POST" action="/internet/dsl_stats_tab.lua?sid=08dc2038a4cddc35">
...
<tr><td class="c1">Max. DSLAM throughput</td><td class="c2">kbit/s</td><td class="c3">70000</td>



curl 'http://192.168.1.1/index.lua' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:64.0) Gecko/20100101 Firefox/64.0' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' -H 'Accept-Language: en-US,en;q=0.5' --compressed -H 'Referer: http://192.168.1.1/' -H 'Content-Type: application/x-www-form-urlencoded' -H 'DNT: 1' -H 'Connection: keep-alive' -H 'Upgrade-Insecure-Requests: 1' --data 'response=e25c3772-4b27ed5ebdc4e3f3819190d834576f33&lp=&username='



LOGOUT
http://192.168.1.1/index.lua
xhr	1
sid	8ef0366cc29866e5
logout	1
no_sidrenew	
