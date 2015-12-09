import json

from .fixtures import tornado_server
from .util import Client

TEST_DHCP_ACK_JSON = """
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
"""

def test_dhcp_ack_insert(tornado_server):
    c = Client(tornado_server)
    data = []
    for i in range(0, 100):
        data.append(json.loads(TEST_DHCP_ACK_JSON))
    resp = c.request("post", "/dhcp/ack", data=json.dumps(data))
    assert resp.ok