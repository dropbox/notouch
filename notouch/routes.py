from .handlers import api
from .handlers import main

HANDLERS = [
    (r"/", main.MainHandler),

    # v1 API Handlers
    (r"/api/v1/dhcp/ack", api.DHCPAckApiV1Handler),
    (r"/api/v1/dhcp/server_stats", api.DHCPServerStatsApiV1Handler),
]