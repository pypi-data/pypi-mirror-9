#!/usr/bin/env python

# Copyright 2014 Climate Forecasting Unit, IC3

# This file is part of Autosubmit.

# Autosubmit is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Autosubmit is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Autosubmit.  If not, see <http://www.gnu.org/licenses/>.
import textwrap

from autosubmit.queue.hpcqueue import HPCQueue
from autosubmit.config.log import Log


class PBSQueue(HPCQueue):

    def __init__(self, expid, version):
        HPCQueue.__init__(self)
        self._host = ""
        self._version = version
        self.scratch = ""
        self.project = ""
        self.user = ""

        if str.startswith(version, '10'):
            self._header = Pbs10Header()
        elif str.startswith(version, '11'):
            self._header = Pbs11Header()
        elif str.startswith(version, '12'):
            self._header = Pbs12Header()
        else:
            Log.error('PBS version {0} not supported'.format(version))
            exit(1)

        self.expid = expid
        self.job_status = dict()
        self.job_status['COMPLETED'] = ['F', 'E', 'c', 'C']
        self.job_status['RUNNING'] = ['R']
        self.job_status['QUEUING'] = ['Q', 'H', 'S', 'T', 'W', 'U', 'M']
        self.job_status['FAILED'] = ['Failed', 'Node_fail', 'Timeout']
        self.update_cmds()

    def update_cmds(self):
        self.remote_log_dir = (self.scratch + "/" + self.project + "/" + self.user + "/" +
                               self.expid + "/LOG_" + self.expid)
        self.cancel_cmd = "ssh " + self._host + " qdel"
        self._checkhost_cmd = "ssh " + self._host + " echo 1"
        self.put_cmd = "scp"
        self.get_cmd = "scp"
        self.mkdir_cmd = "ssh " + self._host + " mkdir -p " + self.remote_log_dir
        self._submit_cmd = "ssh " + self._host + " qsub -d " + self.remote_log_dir + " " + self.remote_log_dir + "/ "

        if str.startswith(self._version, '11'):
            self._checkjob_cmd = "ssh " + self._host + " qstat"

    def get_checkhost_cmd(self):
        return self._checkhost_cmd

    def get_remote_log_dir(self):
        return self.remote_log_dir

    def get_mkdir_cmd(self):
        return self.mkdir_cmd

    def parse_job_output(self, output):
        # job_state = output.split('\n')[2].split()[4]
        # return job_state
        return output

    def get_submitted_job_id(self, output):
        return output.split('.')[0]

    def jobs_in_queue(self):
        return ''.split()

    def get_submit_cmd(self, job_script):
        return self._submit_cmd + job_script

    def get_checkjob_cmd(self, job_id):
        if str.startswith(self._version, '11'):
            return self._checkjob_cmd + str(job_id)
        else:
            return "ssh " + self._host + " " + self.get_qstatjob(job_id)


class Pbs12Header:
    """Class to handle the Archer headers of a job"""

    SERIAL = textwrap.dedent("""
            #!/bin/sh
            ###############################################################################
            #                   %TASKTYPE% %EXPID% EXPERIMENT
            ###############################################################################
            #
            #PBS -N %JOBNAME%
            #PBS -l select=serial=true:ncpus=1
            #PBS -l walltime=%WALLCLOCK%:00
            #PBS -A %HPCPROJ%
            #
            ###############################################################################
            """)

    PARALLEL = textwrap.dedent("""
            #!/bin/sh
            ###############################################################################
            #                   %TASKTYPE% %EXPID% EXPERIMENT
            ###############################################################################
            #
            #PBS -N %JOBNAME%
            #PBS -l select=%NUMPROC%
            #PBS -l walltime=%WALLCLOCK%:00
            #PBS -A %HPCPROJ%
            #
            ###############################################################################
            """)


class Pbs10Header:
    """Class to handle the Hector headers of a job"""

    SERIAL = textwrap.dedent("""
            #!/bin/sh
            ###############################################################################
            #                   %TASKTYPE% %EXPID% EXPERIMENT
            ###############################################################################
            #
            #PBS -N %JOBNAME%
            #PBS -q serial
            #PBS -l cput=%WALLCLOCK%:00
            #PBS -A %HPCPROJ%
            #
            ###############################################################################
            """)

    PARALLEL = textwrap.dedent("""
            #!/bin/sh
            ###############################################################################
            #                   %TASKTYPE% %EXPID% EXPERIMENT
            ###############################################################################
            #
            #PBS -N %JOBNAME%
            #PBS -l mppwidth=%NUMPROC%
            #PBS -l mppnppn=32
            #PBS -l walltime=%WALLCLOCK%:00
            #PBS -A %HPCPROJ%
            #
            ###############################################################################
            """)


class Pbs11Header:
    """Class to handle the Lindgren headers of a job"""

    SERIAL = textwrap.dedent("""\
            #!/bin/sh
            ###############################################################################
            #                         %TASKTYPE% %EXPID% EXPERIMENT
            ###############################################################################
            #
            #!/bin/sh --login
            #PBS -N %JOBNAME%
            #PBS -l mppwidth=%NUMPROC%
            #PBS -l mppnppn=%NUMTASK%
            #PBS -l walltime=%WALLCLOCK%
            #PBS -e %SCRATCH_DIR%/%HPCPROJ%/%HPCUSER%/%EXPID%/LOG_%EXPID%
            #PBS -o %SCRATCH_DIR%/%HPCPROJ%/%HPCUSER%/%EXPID%/LOG_%EXPID%
            #
            ###############################################################################
            """)

    PARALLEL = textwrap.dedent("""\
            #!/bin/sh
            ###############################################################################
            #                         %TASKTYPE% %EXPID% EXPERIMENT
            ###############################################################################
            #
            #!/bin/sh --login
            #PBS -N %JOBNAME%
            #PBS -l mppwidth=%NUMPROC%
            #PBS -l mppnppn=%NUMTASK%
            #PBS -l walltime=%WALLCLOCK%
            #PBS -e %SCRATCH_DIR%/%HPCPROJ%/%HPCUSER%/%EXPID%/LOG_%EXPID%
            #PBS -o %SCRATCH_DIR%/%HPCPROJ%/%HPCUSER%/%EXPID%/LOG_%EXPID%
            #
            ###############################################################################
            """)