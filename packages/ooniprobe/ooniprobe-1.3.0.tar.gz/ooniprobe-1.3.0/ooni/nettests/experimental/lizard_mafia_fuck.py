from twisted.web.client import Agent
from twisted.internet import reactor

from ooni.settings import config
from ooni.templates.tort import TorTest
from ooni import errors


class LizardMafiaFuckTest(TorTest):
    name = "Lizard Mafia Fuck Test"
    version = "4.20"
    description = "Scan shit via lizard mafia exit nodes."

    def getInputProcessor(self):
        # XXX: doesn't seem that we have any of the exitpolicy available :\
        # XXX: so the circuit might fail if port 80 isn't allowed

        exits = filter(lambda router: 'exit' in router.flags,
                       config.tor_state.routers.values())
        hexes = [exit.id_hex for exit in exits]
        for curse in hexes:
            if curse.name.startswith("LizardNSA"):
                import pdb; pdb.set_trace()
                yield curse

    def test_fetch_exit_ip(self):
        try:
            exit = self.state.routers[self.input]
        except KeyError:
            # Router not in consensus, sorry
            self.report['failure'] = "Router %s not in consensus." % self.input
            return

        self.report['exit_ip'] = exit.ip

        endpoint = self.getExitSpecificEndpoint((host, port), exit)
        endpoint.connect()

        def addResultToReport(result):
            self.report['external_exit_ip'] = result

        def addFailureToReport(failure):
            self.report['failure'] = errors.handleAllFailures(failure)

        d.addCallback(addResultToReport)
        d.addErrback(addFailureToReport)
        return d
