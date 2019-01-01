# fritz-dsl-mon

**A simple DSL monitoring tool for Fritz!Box 7430 written in Python 3.**

## A a glance

[Fritz!Box 7430](https://en.avm.de/products/fritzbox/fritzbox-7430/) is a residential gateway device including a VDSL modem and a LAN-WAN router. Its web interface offers a variety of functionalities and exposes data relevant to the power user.
While detailed information on the DSL status and health are available, there is no built-in mechanism to record them. The box appliance does not offer any API to access data in a programatic way.

fritz-dsl-mon:
* Simulates login
* Retrieves data from the DSL information page (using HTML scraping)
* Stores them in CSV files

This is a "scratch your own itch project". I wanted to able to detect internet connectivity issues early on in order to report them to my ISP without delay. It is therefore a mixed bag of data scraping, data collection and, hopefully at a later stage, of data aggragation, reporting and alerting.

## Installation


## Usage

1. Clone this repository
2. Run `fritzbox.py` and/or `store_info.py` with Python 3
3. Analyse the collected data

### One time info

`fritzbox.py` will give you an insight on your DSL connection.

```
$  python3 fritzbox.py -H 192.168.1.1 -p mypassword
max_dslam_throughput_down: 70000
max_dslam_throughput_up: 20000
attainable_throughput_down: 128843
attainable_throughput_up: 27568
current_throughput_down: 69997
current_throughput_up: 19999
seamless_rate_adaptation_down: off
seamless_rate_adaptation_up: off
latency_down: fast
latency_up: fast
impulse_noise_protection_down: 41
impulse_noise_protection_up: 42
g_inp_down: on
g_inp_up: on
signal_to_noise_ratio_down: 23
signal_to_noise_ratio_up: 10
bitswap_down: on
bitswap_up: on
line_attenuation_down: 7
line_attenuation_up: 5
approximate_line_length: 163
profile: 17a
g_vector_down: full
g_vector_up: full
carrier_record_down: A43
carrier_record_up: A43
fritzbox_seconds_with_errors: 0
fritzbox_seconds_with_many_errors: 0
fritzbox_crc_errors_per_minute: 0
fritzbox_crc_errors_last_15_m: 0
central_exchange_seconds_with_errors: 1
central_exchange_seconds_with_many_errors: 0
central_exchange_crc_errors_per_minute: 0.02
central_exchange_crc_errors_last_15_m: 0
```

### Store connection data

`store_info.py` stores the DSL info in a CSV file.
It is intended to be executed on a regular basis, typically several times per day with a crontab:

``` 
$  python3 store_info.py -H 192.168.1.1 -p mypassword -d data
```

The destination directory `data` must exist. One file will be created per day, for instance:

```
$ head -3 data/20190101.csv
timestamp,max_dslam_throughput_down,max_dslam_throughput_up,attainable_throughput_down,attainable_throughput_up,current_throughput_down,current_throughput_up,seamless_rate_adaptation_down,seamless_rate_adaptation_up,latency_down,latency_up,impulse_noise_protection_down,impulse_noise_protection_up,g_inp_down,g_inp_up,signal_to_noise_ratio_down,signal_to_noise_ratio_up,bitswap_down,bitswap_up,line_attenuation_down,line_attenuation_up,approximate_line_length,profile,g_vector_down,g_vector_up,carrier_record_down,carrier_record_up,fritzbox_seconds_with_errors,fritzbox_seconds_with_many_errors,fritzbox_crc_errors_per_minute,fritzbox_crc_errors_last_15_m,central_exchange_seconds_with_errors,central_exchange_seconds_with_many_errors,central_exchange_crc_errors_per_minute,central_exchange_crc_errors_last_15_m
20190101105541,70000,20000,129204,27364,69997,19999,off,off,fast,fast,41,42,on,on,23,10,on,on,7,5,163,17a,full,full,A43,A43,0,0,0,0,1,0,0.02,0
20190101110511,70000,20000,129204,27575,69997,19999,off,off,fast,fast,41,42,on,on,23,10,on,on,7,5,163,17a,full,full,A43,A43,0,0,0,0,1,0,0.02,0
```

### Analyse, alert and report

It is all very good to hoard data, but how do you act on them? If the connection drops to a clearly unacceptable levelm for instance less than 1Mbps up, an alert would be in order. But should you send an alert as soon as the bandwith drops, even if the modem was acquiring a new IP? It's probably ok if it happens once a day but not ok if the connection fails several times. How do you tell the two apart? How do you interpret the CRC errors? Here, the download Bandwith is 70Mbps, although not long ago, it was 85Mps. How should this be highlighted in a report, should and alert be sent? Should I complain to my ISP?

This part is a TODO.

## Technical information

### Login

fritz-dsl-mon first simulates a login on the web interface. This part is a bit tricky as the web page relies on Javascript to `md5` encode a challenge. From there, a `POST` can be executed to receive a `sid`. The reason why the box works this way is unknown.

### HTML scraping

Although some pages receive pure JSON from the applicance, the interessting bits on the DSL information page are only available in HMTL. The content is therefore scraped, old school, with all the associated risks and fragility. See some examples in the [samples](/samples) directory.

## Known issues and limitations

* Errors are logged in `error.log` but an empty entry should be added to the CSV file.

## Credits

For `sid` with `md5` encoded challenge:
[fritzswitch - Switch your Fritz!DECT200 via command line](https://github.com/shred/fritzswitch).  Copyright (C) 2014 Richard "Shred" Körber and released under GNU GPL license

## License

Licensed under the GNU GPL license. See [LICENSE.md](LICENSE.txt).
Copyright (C) 2019 Youri Ackx unless stated otherwise.
