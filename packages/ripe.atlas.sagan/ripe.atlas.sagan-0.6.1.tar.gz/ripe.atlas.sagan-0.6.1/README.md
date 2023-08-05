# RIPE Atlas Sagan [![Build Status](https://travis-ci.org/RIPE-NCC/ripe.atlas.sagan.png?branch=master)](https://travis-ci.org/RIPE-NCC/ripe.atlas.sagan)

A parsing library for RIPE Atlas measurement results 


## Why this exists

RIPE Atlas generates a **lot** of data, and the format of that data changes over
time.  Often you want to do something simple like fetch the median RTT for each
measurement result between date `X` and date `Y`.  Unfortunately, there are are
dozens of edge cases to account for while parsing the JSON, like the format of
errors and firmware upgrades that changed the format entirely.

To make this easier for our users (and for ourselves), we wrote an easy to use
parser that's smart enough to figure out the best course of action for each
result, and return to you a useful, native Python object.


## How to install

The stable version should always be in PyPi, so you can install it with `pip`:

```bash
$ pip install ripe.atlas.sagan
```

Better yet, make sure you get ujson and sphinx installed with it:

```bash
$ pip install ripe.atlas.sagan[fast,doc]
```


### Troubleshooting

Some setups (like MacOS) have trouble with building the dependencies required
for reading SSL certificates.  If you don't care about SSL stuff and only want
to use sagan to say, parse traceroute or DNS results, then you can tell the
installer to skip building ``pyOpenSSL`` by doing the following:

```bash
$ SAGAN_WITHOUT_SSL=1 pip install ripe.atlas.sagan
```


## Quickstart: How To Use It

You can parse a result in a few ways.  You can just pass the JSON-encoded
string:

```python
from ripe.atlas.sagan import PingResult

my_result = PingResult("<result string from RIPE Atlas ping measurement>")

print(my_result.rtt_median)
123.456

print(my_result.af)
6
```

You can do the JSON-decoding yourself:

```python
from ripe.atlas.sagan import PingResult

my_result = PingResult(
    json.loads("<result string from RIPE Atlas ping measurement>")
)

print(my_result.rtt_median)
123.456

print(my_result.af)
6
```

You can let the parser guess the right type for you, though this incurs a
small performance penalty:

```python
from ripe.atlas.sagan import Result

my_result = Result.get("<result string from RIPE Atlas ping measurement>")

print(my_result.rtt_median)
123.456

print(my_result.af)
6
```


## What it supports

Essentially, we tried to support everything.  If you pass in a DNS result
string, the parser will return a `DNSResult` object, which contains a list of
`Response`s, each with an `abuf` property, as well as all of the information in
that abuf: header, question, answer, etc.

```python
from ripe.atlas.sagan import DnsResult

my_dns_result = DnsResult("<result string from a RIPE Atlas DNS measurement>")
my_dns_result.responses[0].abuf  # The entire string
my_dns_result.responses[0].abuf.header.arcount  # Decoded from the abuf
```

We do the same sort of thing for SSL measurements, traceroutes, everything.  We
try to save you the effort of sorting through whatever is in the result.


### Which attributes are supported?

Every result type has its own properties, with a few common between all types.

Specifically, these attributes exist on all `*Result` objects:

* `created`  An arrow object (like datetime, but better) of the `timestamp` field
* `measurement_id`
* `probe_id`
* `firmware` An integer representing the firmware version
* `origin`  The `from` attribute in the result
* `is_error` Set to `True` if an error was found

Additionally, each of the result types have their own properties, like
`packet_size`, `responses`, `certificates`, etc.  You can take a look at the
classes themselves, or just look at the tests if you're curious.  But to get you
started, here are some examples:

```python
# Ping
ping_result.packets_sent  # Int
ping_result.rtt_median    # Float, rounded to 3 decimal places
ping_result.rtt_average   # Float, rounded to 3 decimal places

# Traceroute
traceroute_result.af                   # 4 or 6
traceroute_result.total_hops           # Int
traceroute_result.destination_address  # An IP address string

# DNS
dns_result.responses                        # A list of Response objects
dns_result.responses[0].response_time       # Float, rounded to 3 decimal places
dns_result.responses[0].headers             # A list of Header objects
dns_result.responses[0].headers[0].nscount  # The NSCOUNT value for the first header
dns_result.responses[0].questions           # A list of Question objects
dns_result.responses[0].questions[0].type   # The TYPE value for the first question
dns_result.responses[0].abuf                # The raw, unparsed abuf string

# SSL Certificates
ssl_result.af                        # 4 or 6
ssl_result.certificates              # A list of Certificate objects
ssl_result.certificates[0].checksum  # The checksum for the first certificate

# HTTP
http_result.af                      # 4 or 6
http_result.uri                     # A URL string
http_result.responses               # A list of Response objects
http_result.responses[0].body_size  # The size of the body of the first response

# NTP
ntp_result.af                          # 4 or 6
ntp_result.stratum                     # Statum id
ntp_result.version                     # Version number
ntp_result.packets[0].final_timestamp  # A float representing a high-precision NTP timestamp
ntp_result.rtt_median                  # Median value for packets sent & received
```


## What it requires

As you might have guessed, with all of this magic going on under the hood, there
are a few dependencies:

* [arrow](https://pypi.python.org/pypi/arrow)
* [pyOpenSSL](https://pypi.python.org/pypi/pyOpenSSL) (Optional: see "Troubleshooting" above)
* [python-dateutil](https://pypi.python.org/pypi/python-dateutil)
* [pytz](https://pypi.python.org/pypi/pytz)
* [IPy](https://pypi.python.org/pypi/IPy/)

Additionally, we recommend that you also install
[ujson](https://pypi.python.org/pypi/ujson) as it will speed up the
JSON-decoding step considerably, and
[sphinx](https://pypi.python.org/pypi/Sphinx) if you intend to build the
documentation files for offline use.


## Running Tests

There's a full battery of tests for all measurement types, so if you've made
changes and would like to submit a pull request, please run them (and update
them!) before sending your request:

```bash
$ python setup.py test
```

You can also install `tox` to test everything in all of the supported Python
versions:

```bash
$ pip install tox
$ tox
```


## Further Documentation

Complete documentation can always be found on
[the RIPE Atlas project page](https://atlas.ripe.net/docs/sagan/), and if you're
not online, the project itself contains a `docs` directory -- everything you
should need is in there.


## Who's Responsible for This?

Sagan is actively maintained by the RIPE NCC and primarily developed by
[Daniel Quinn](https://github.com/danielquinn), while the abuf parser is mostly
the responsibility of [Philip Homburg](https://github.com/philiphomburg) with an
assist from Bert Wijnen and Rene Wilhelm who contributed to the original script.
[Andreas Stirkos](https://github.com/astrikos) did the bulk of the work on NTP
measurements and fixt a few bugs, and big thanks go to
[Chris Amin](https://github.com/chrisamin) and
[John Bond](https://github.com/b4ldr) for finding and fixing stuff where they've
run into problems.


## Colophon

But why [*Sagan*](https://en.wikipedia.org/wiki/Carl_Sagan)?  The RIPE Atlas team decided to name all of its modules after
explorers, and what better name for a parser than that of the man who spent
decades reaching out to the public about the wonders of the cosmos?
