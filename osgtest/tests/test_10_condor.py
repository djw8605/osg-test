import os
import osgtest.library.core as core
import unittest

class TestStartCondor(unittest.TestCase):

    def test_01_start_condor(self):
        core.config['condor.lockfile'] = '/var/lock/subsys/condor_master'
        core.state['condor.started-master'] = False

        if not core.rpm_is_installed('condor'):
            core.skip('not installed')
            return
        if os.path.exists(core.config['condor.lockfile']):
            core.skip('apparently running')
            return

        command = ('service', 'condor', 'start')
        status, stdout, stderr = core.syspipe(command)
        fail = core.diagnose('Start Condor', status, stdout, stderr)
        self.assertEqual(status, 0, fail)
        self.assert_(stdout.find('error') == -1,
                     "Starting Condor reported 'error'")
        self.assert_(os.path.exists(core.config['condor.lockfile']),
                     'Condor run lock file missing')
        core.state['condor.started-master'] = True
