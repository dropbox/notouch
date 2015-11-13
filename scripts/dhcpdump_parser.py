"""
DHCP Dump Parser - Parse the dhcpdump output into json and sent to the notouch server or stdout.

dhcpdump is a command line utility that uses libpcap to
listen for dhcp packets and then outputs the packet in a
textual format. The purpose of this program is to parse
the text output into structured data (json) and then send
it to off to an http api endpoint so it can be logged into
a database.

DHCP Dump Sample Output:

> dhcpdump -i eth0

---------------------------------------------------------------------------

  TIME: 2015-01-01 00:00:00.000000
    IP: 10.X.X.X (00:00:00:00:00:00) > 10.X.X.X (00:00:00:00:00:00)
    OP: 1 (BOOTPREQUEST)
 HTYPE: 1 (Ethernet)
  HLEN: 6
  HOPS: 1
   XID: 01a3cbe5
  SECS: 0
 FLAGS: 7f80
CIADDR: 0.0.0.0
YIADDR: 0.0.0.0
SIADDR: 0.0.0.0
GIADDR: 10.X.X.X
CHADDR: 00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00
 SNAME: .
 FNAME: .
OPTION:  53 (  1) DHCP message type         1 (DHCPDISCOVER)
OPTION:  57 (  2) Maximum DHCP message size 1152
OPTION:  61 ( 25) Client-identifier         00:00:00:00:00:00
OPTION:  55 ( 11) Parameter Request List      1 (Subnet mask)
                         66 (TFTP server name)
                          6 (DNS server)
                         15 (Domainname)
                         44 (NetBIOS name server)
                          3 (Routers)
                         67 (Bootfile name)
                         12 (Host name)
                         33 (Static route)
                        150 (???)
                         43 (Vendor specific info)

---------------------------------------------------------------------------

DHCP acks and DHCP server stats will be sent up to the notouch server or sent to stdout.

The dhcpdump output is parsed into the following JSON form:

{
        "ip_dst": "10.X.X.X",
        "mac_dst": "00:00:00:00:00:00",
        "giaddr": "10.X.X.X",
        "htype": 1,
        "file": "",
        "opname": "dhcpack",
        "ip_src": "10.X.X.X",
        "xid": "0cd0ac2c",
        "ciaddr": "0.0.0.0",
        "hops": 2,
        "ts": "2015-01-01 00:00:00.000000",
        "yiaddr": "10.X.X.X",
        "fname": "/<filename>",
        "siaddr": "10.X.X.X",
        "sname": ".",
        "hlen": 6,
        "chaddr": "00:00:00:00:00:00",
        "mac_src": "00:00:00:00:00:00",
        "secs": 0,
        "flags": "7f80",
        "options": [
            {
                "data": "dhcpack",
                "name": "dhcp_message_type",
                "op": 53
            },
            {
                "data": "10.X.X.X",
                "name": "server_identifier",
                "op": 54
            },
            {
                "data": "7d",
                "name": "ip_address_leasetime",
                "op": 51
            },
            {
                "data": "255.255.255.255",
                "name": "subnet_mask",
                "op": 1
            },
            {
                "data": "10.X.X.X",
                "name": "routers",
                "op": 3
            },
            {
                "data": "10.X.X.X",
                "name": "dns_server",
                "op": 6
            },
            {
                "data": "<hostname>",
                "name": "host_name",
                "op": 12
            },
            {
                "data": "<domainname>",
                "name": "domainname",
                "op": 15
            },
            {
                "data": "10.X.X.X",
                "name": "broadcast_address",
                "op": 28
            },
            {
                "data": "10.X.X.X",
                "name": "ntp_servers",
                "op": 42
            },
            {
                "data": "3d12h",
                "name": "t1",
                "op": 58
            },
            {
                "data": "6d3h",
                "name": "t2",
                "op": 59
            }
        ],
        "op": 2
    }
]

Additionally server stats will be generated in the following form:

{
    "server_hostname": "<hostname>",
    "dhcpack_count": 17,
    "timestamp_start": "2015-01-01 00:00:00.000000",
    "clients": {
        "00:00:00:00:00:00": {
            "dhcpoffer": 0,
            "dhcpdiscover": 0,
            "dhcprequest": 1,
            "dhcpack": 1
        },
        "00:00:00:00:00:00": {
            "dhcpoffer": 0,
            "dhcpdiscover": 2,
            "dhcprequest": 0,
            "dhcpack": 0
        },
        ...
        ...
        ...
    },
    "server_ip": "10.X.X.X",
    "dhcpoffer_count": 26,
    "dhcpdiscover_count": 48,
    "timestamp_end": "2015-01-01 00:00:00.000000",
    "dhcprequest_count": 17
}
"""
import subprocess
import sys
import json
import socket
import collections
import time
import datetime
import argparse
import requests

def parse_entry(entry):
    packet = {
        "ts": "",
        "ip_src": "",
        "mac_src": "",
        "ip_dst": "",
        "mac_dst": "",
        "op": -1,
        "opname": "",
        "htype": -1,
        "hlen" : -1,
        "hops": -1,
        "xid": "",
        "secs": "",
        "flags": -1,
        "ciaddr": "",
        "yiaddr": "",
        "siaddr": "",
        "giaddr": "",
        "chaddr": "",
        "sname": "",
        "file": "",
        "options": [],
    }
    for line in entry:
        if line.startswith("TIME:"):
            packet["ts"] = line.split(":", 1)[-1].strip()
        elif line.startswith("IP:"):
            line = line.split(":", 1)[-1].strip()
            src, dst = line.split(">")
            packet["ip_src"] = src.split("(")[0].strip()
            packet["ip_dst"] = dst.split("(")[0].strip()
            packet["mac_src"] = src.split("(")[1].strip(' )')
            packet["mac_dst"] = dst.split("(")[1].strip(')')
        elif line.startswith("OP:"):
            packet["op"] = int(line.split(":")[1].split("(")[0].strip())
        elif line.startswith("HTYPE:"):
            packet["htype"] = int(line.split(":")[1].split("(")[0].strip())
        elif line.startswith("HLEN:"):
            packet["hlen"] = int(line.split(":")[-1].strip())
        elif line.startswith("HOPS:"):
            packet["hops"] = int(line.split(":")[-1].strip())
        elif line.startswith("SECS:"):
            packet["secs"] = int(line.split(":")[-1].strip())
        elif line.startswith("FLAGS:"):
            packet["flags"] = line.split(":")[-1].strip()
        elif line.startswith("XID:"):
            packet["xid"] = line.split(":")[-1].strip()
        elif line.startswith("CIADDR:"):
            packet["ciaddr"] = line.split(":", 1)[-1].strip()
        elif line.startswith("YIADDR:"):
            packet["yiaddr"] = line.split(":", 1)[-1].strip()
        elif line.startswith("SIADDR:"):
            packet["siaddr"] = line.split(":", 1)[-1].strip()
        elif line.startswith("GIADDR:"):
            packet["giaddr"] = line.split(":", 1)[-1].strip()
        elif line.startswith("SNAME:"):
            packet["sname"] = line.split(":", 1)[-1].strip()
        elif line.startswith("FNAME:"):
            packet["fname"] = line.split(":", 1)[-1].strip()
        elif line.startswith("CHADDR:"):
            packet["chaddr"] = line.split(":", 1)[-1].strip()[0:17]
        elif line.startswith("OPTION:"):
            line = line.split(":", 1)[-1].strip()
            op = int(line.split("(", 1)[0].strip())
            if op in [55, 57, 93, 94, 97]:
                continue
            rest = line.split(")", 1)[-1].strip()
            name = rest.split("  ")[0].strip()
            data = rest.split("  ")[-1].strip()
            if data.endswith(")"):
                data = data.split("(")[-1].strip(" )").lower()
            key = name.lower().replace(" ", "_")
            packet["options"].append({
                "name": key,
                "data": data,
                "op": op,
            })
            if op == 53:
                packet["opname"] = data
    return packet


def reset(my_ip, my_hostname):
    server_stats = {
        "dhcpack_count": 0,
        "dhcpdiscover_count": 0,
        "dhcpoffer_count": 0,
        "dhcprequest_count": 0,
        "server_ip": my_ip,
        "server_hostname": my_hostname,
        "timestamp_start": str(datetime.datetime.utcnow()),
        "timestamp_end": str(datetime.datetime.utcnow()),
        "clients": {}
    }
    return server_stats


def send(nosend, ack_endpoint, stats_endpoint,  packets, server_stats):
    """
    Send data to notouch or stdout.
    """
    acks = [packet for packet in packets if packet["opname"] == "dhcpack"]
    server_stats["timestamp_end"] = str(datetime.datetime.utcnow())
    if nosend:
        print json.dumps(acks, indent=4)
        print "-" * 75
        print json.dumps(server_stats, indent=4)
    else:
        requests.post(ack_endpoint, data=json.dumps(acks))
        requests.post(stats_endpoint, data=json.dumps(server_stats))


def main(nosend, server, send_interval):

    # Line seperator for each entry is 75 '-' characters.
    sep = "-" * 75
    try:
        proc = subprocess.Popen(["dhcpdump", "-i", "eth0"], stdout=subprocess.PIPE)
    except Exception as e:
        print "Exception running dhcpdump. %s" % e
        sys.exit(1)
    my_ip = socket.gethostbyname(socket.getfqdn())
    my_hostname = socket.gethostname()
    start = time.time()
    server_stats = reset(my_ip, my_hostname)
    lines = []
    packets = []
    ack_endpoint = "%s/api/v1/dhcp/ack" % (server,)
    stats_endpoint = "%s/api/v1/dhcp/server_stats" % (server,)

    # Main 'event loop' operating on dhcpdump output.
    while True:
        line = proc.stdout.readline().strip()
        if line == sep:
            packet = parse_entry(lines)
            lines = []
            # Don't record packets where this server is not the client or the server.
            if packet["ip_src"] == my_ip or packet["ip_dst"] == my_ip:
                packets.append(packet)
                if packet["opname"] in ["dhcpack", "dhcpdiscover", "dhcpoffer", "dhcprequest"]:
                    server_stats[packet["opname"] + "_count"] += 1
                    if packet["chaddr"] not in server_stats["clients"].keys():
                        server_stats["clients"][packet["chaddr"]] = {
                            "dhcpack": 0,
                            "dhcpoffer": 0,
                            "dhcprequest": 0,
                            "dhcpdiscover": 0,
                        }
                    server_stats["clients"][packet["chaddr"]][packet["opname"]] += 1
            offset = time.time() - start
            if offset >= send_interval:
                start = time.time()
                send(nosend, ack_endpoint, stats_endpoint, packets, server_stats)
                server_stats = reset(my_ip, my_hostname)
                packets = []
        elif line != '':
            lines.append(line)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DHCPDump Logger")
    parser.add_argument("--server", dest="server", type=str, help="Notouch web server to log to.")
    parser.add_argument("--send_interval", dest="send_interval", type=int,
        help="Send statistics to the server on this interval.", default=10)
    parser.add_argument("--nosend", action="store_true", dest="nosend", default=False,
        help="Don't send data to the notouch server, output to stdout.")
    args = parser.parse_args()
    main(args.nosend, args.server, args.send_interval)
