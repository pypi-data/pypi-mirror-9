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


class LsfQueue(HPCQueue):
    def __init__(self, expid):
        HPCQueue.__init__(self)
        self._host = "mn-ecm86"
        self.scratch = ""
        self.project = ""
        self.user = ""
        self._header = LsfHeader()
        self.expid = expid
        self.job_status = dict()
        self.job_status['COMPLETED'] = ['DONE']
        self.job_status['RUNNING'] = ['RUN']
        self.job_status['QUEUING'] = ['PEND', 'FW_PEND']
        self.job_status['FAILED'] = ['SSUSP', 'USUSP', 'EXIT']
        self.update_cmds()

    def update_cmds(self):
        self.remote_log_dir = (self.scratch + "/" + self.project + "/" + self.user + "/" + self.expid + "/LOG_"
                               + self.expid)
        self.cancel_cmd = "ssh " + self._host + " bkill"
        self._checkjob_cmd = "ssh " + self._host + " bjobs "
        self._checkhost_cmd = "ssh " + self._host + " echo 1"
        self._submit_cmd = "ssh " + self._host + " bsub \< " + self.remote_log_dir + "/"
        self.put_cmd = "scp"
        self.get_cmd = "scp"
        self.mkdir_cmd = "ssh " + self._host + " mkdir -p " + self.remote_log_dir

    def get_checkhost_cmd(self):
        return self._checkhost_cmd

    def get_mkdir_cmd(self):
        return self.mkdir_cmd

    def get_remote_log_dir(self):
        return self.remote_log_dir

    def parse_job_output(self, output):
        job_state = output.split('\n')[1].split()[2]
        return job_state

    def get_submitted_job_id(self, output):
        return output.split('<')[1].split('>')[0]

    def jobs_in_queue(self, output):
        return zip(*[line.split() for line in output.split('\n')])[0][1:]

    def get_checkjob_cmd(self, job_id):
        return self._checkjob_cmd + str(job_id)

    def get_submit_cmd(self, job_script):
        return self._submit_cmd + job_script


class LsfHeader:
    """Class to handle the BSC headers of a job"""

    SERIAL = textwrap.dedent("""
            #!/bin/ksh
            ###############################################################################
            #                     %TASKTYPE% %EXPID% EXPERIMENT
            ###############################################################################
            #
            #@ job_name         = %JOBNAME%
            #@ wall_clock_limit = %WALLCLOCK%
            #@ output           = %SCRATCH_DIR%/%HPCUSER%/%EXPID%/LOG_%EXPID%/%JOBNAME%_%j.out
            #@ error            = %SCRATCH_DIR%/%HPCUSER%/%EXPID%/LOG_%EXPID%/%JOBNAME%_%j.err
            #@ total_tasks      = %NUMTASK%
            #@ initialdir       = %SCRATCH_DIR%/%HPCUSER%/%EXPID%/
            #@ class            = %CLASS%
            #@ partition        = %PARTITION%
            #@ features         = %FEATURES%
            #
            ###############################################################################
            """)

    PARALLEL = textwrap.dedent("""
            #!/bin/ksh
            ###############################################################################
            #                     %TASKTYPE% %EXPID% EXPERIMENT
            ###############################################################################
            #
            #@ job_name         = %JOBNAME%
            #@ wall_clock_limit = %WALLCLOCK%
            #@ output           = %SCRATCH_DIR%/%HPCUSER%/%EXPID%/LOG_%EXPID%/%JOBNAME%_%j.out
            #@ error            = %SCRATCH_DIR%/%HPCUSER%/%EXPID%/LOG_%EXPID%/%JOBNAME%_%j.err
            #@ total_tasks      = %NUMTASK%
            #@ initialdir       = %SCRATCH_DIR%/%HPCUSER%/%EXPID%/
            #@ tasks_per_node   = %TASKSNODE%
            #@ tracing          = %TRACING%
            #
            ###############################################################################
            """)