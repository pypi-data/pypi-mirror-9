multidns will relay your DNS requsts to several DNS servers and
returns the first answer.

You can also specify an invalid address e.g. 10.10.34.34. If the
answer was 10.10.34.34 the program will continue to try other DNS
servers to find an answer that is not 10.10.34.34.

If you put an `x' character before the address of a DNS server
e.g. `x8.8.8.8:53' the request and its response will be encrypted with
a symmetrical encyption algorithm--that applying the same encryption
algorithm twice will decode to the first input. So if you relay your
DNS requst twice through two instances of this program with `x'
prefixes, the result will be a normal DNS server. But the traffic
between the two program instances will be encrypted. The encryption
algorithm is not secure at all but it is highly possible that it can
fool your government censorship devices.


