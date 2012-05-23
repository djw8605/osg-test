import os
import unittest
import re

import osgtest.library.core as core
import osgtest.library.files as files

class TestStartPBS(unittest.TestCase):

    pbs_config = """
create queue batch queue_type=execution
set queue batch started=true
set queue batch enabled=true
set queue batch resources_default.nodes=1
set queue batch resources_default.walltime=3600
set server default_queue=batch
set server keep_completed = 600
set server job_nanny = True
set server scheduling=true
"""
    required_rpms = ['torque-mom',
                     'torque-server', 
                     'torque-scheduler',
                     'torque-client']

    def __get_release(self):
        """
        Get release information
        """
        release = file('/etc/redhat-release').read()
        matches = re.match('.*release (\d)\.\d', release)
        if matches is None:
            return None
        else:
            return matches.group(1)

    def test_01_start_mom(self):
        core.config['torque.mom-lockfile'] = '/var/lock/subsys/pbs_mom'
        core.state['torque.pbs-mom-running'] = False

        if core.missing_rpm(*self.required_rpms):
            return
        if os.path.exists(core.config['torque.mom-lockfile']):
            core.skip('pbs mom apparently running')
            return

        command = ('service', 'pbs_mom', 'start')
        stdout, _, fail = core.check_system(command, 'Start pbs mom daemon')
        self.assert_(stdout.find('error') == -1, fail)
        self.assert_(os.path.exists(core.config['torque.mom-lockfile']),
                     'PBS mom run lock file missing')
        core.state['torque.pbs-mom-running'] = True


    def test_02_start_pbs_sched(self):
        core.config['torque.sched-lockfile'] = '/var/lock/subsys/pbs_sched'
        core.state['torque.pbs-sched-running'] = False

        if core.missing_rpm(*self.required_rpms):
            return
        if os.path.exists(core.config['torque.sched-lockfile']):
          core.skip('pbs scheduler apparently running')
          return
    
        command = ('service', 'pbs_sched', 'start')
        stdout, _, fail = core.check_system(command, 'Start pbs scheduler daemon')
        self.assert_(stdout.find('error') == -1, fail)
        self.assert_(os.path.exists(core.config['torque.sched-lockfile']),
                     'pbs sched run lock file missing')
        core.state['torque.pbs-sched-running'] = True

    def test_03_start_pbs(self):
        core.config['torque.pbs-lockfile'] = '/var/lock/subsys/pbs_server'
        core.state['torque.pbs-server-running'] = False
        core.state['torque.pbs-configured'] = False
        if self.__get_release() == '5':
            core.config['torque.pbs-nodes-file'] = '/var/torque/server_priv/nodes'
        elif self.__get_release() == '6':
            core.config['torque.pbs-nodes-file'] = '/var/lib/torque/server_priv/nodes'
        else:
            core.skip('Distribution version not supported')

        if core.missing_rpm(*self.required_rpms):
            return
        if os.path.exists(core.config['torque.pbs-lockfile']):
            core.skip('pbs server apparently running')
            return
    
        # add the local node as a compute node
        files.write(core.config['torque.pbs-nodes-file'],
                    "localhost np=1\n",
                    backup=True) 
        command = ('service', 'pbs_server', 'start')
        stdout, _, fail = core.check_system(command, 'Start pbs server daemon')
        self.assert_(stdout.find('error') == -1, fail)
        self.assert_(os.path.exists(core.config['torque.pbs-lockfile']),
                     'pbs server run lock file missing')
        core.state['torque.pbs-server'] = True
        core.state['torque.pbs-server-running'] = True

        core.check_system("echo '%s' | qmgr" % self.pbs_config, 
                          "Configuring pbs server",
                          shell = True)
        core.state['torque.pbs-configured'] = True