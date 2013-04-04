import os
import osgtest.library.core as core
import osgtest.library.osgunittest as osgunittest
import unittest

class TestStartCondor(osgunittest.OSGTestCase):

    def test_01_start_condor(self):
        core.config['condor.lockfile'] = '/var/lock/subsys/condor_master'
        core.state['condor.started-service'] = False
        core.state['condor.running-service'] = False

        core.skip_ok_unless_installed('condor')
        if os.path.exists(core.config['condor.lockfile']):
            core.state['condor.running-service'] = True
            self.skip_ok('already running')
            
        command = ('service', 'condor', 'start')
        stdout, _, fail = core.check_system(command, 'Start Condor')
        self.assert_(stdout.find('error') == -1, fail)
        self.assert_(os.path.exists(core.config['condor.lockfile']),
                     'Condor run lock file missing')
        core.state['condor.started-service'] = True
        core.state['condor.running-service'] = True
