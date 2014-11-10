from twisted.internet import defer
from nav.mibs import mibretriever


class DlinkGenmgmtMib(mibretriever.MibRetriever):
    @defer.inlineCallbacks
    def get_cpu_utilization(self):
        util = yield self.get_next('agentCPUutilizationIn1min')
        if util is not None:
            defer.returnValue(dict(cpu=util))

    def get_cpu_loadavg(self):
        return defer.succeed(None)
