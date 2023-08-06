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
        self.cancel_cmd = "bkill"
        self._checkjob_cmd = "bjobs "
        self._checkhost_cmd = "echo 1"
        self._submit_cmd = "bsub -cwd " + self.remote_log_dir + " < " + self.remote_log_dir + "/"
        self.put_cmd = "scp"
        self.get_cmd = "scp"
        self.mkdir_cmd = "mkdir -p " + self.remote_log_dir

    def get_checkhost_cmd(self):
        return self._checkhost_cmd

    def get_mkdir_cmd(self):
        return self.mkdir_cmd

    def get_remote_log_dir(self):
        return self.remote_log_dir

    def parse_job_output(self, output):
        job_state = output.split('\n')
        if len(job_state) > 1:
            job_state = job_state[1].split()
            if len(job_state) > 2:
                return job_state[2]
        # If we can not process output, assuming completed. Then we will look for completed files and status will
        # change to failed if COMPLETED file is not present.
        return 'DONE'

    def get_submitted_job_id(self, output):
        return output.split('<')[1].split('>')[0]

    def jobs_in_queue(self):
        return zip(*[line.split() for line in ''.split('\n')])[0][1:]

    def get_checkjob_cmd(self, job_id):
        return self._checkjob_cmd + str(job_id)

    def get_submit_cmd(self, job_script):
        return self._submit_cmd + job_script


class LsfHeader:
    """Class to handle the MareNostrum3 headers of a job"""

    SERIAL = textwrap.dedent("""
            #!/bin/sh
            ###############################################################################
            #                   %TASKTYPE% %EXPID% EXPERIMENT
            ###############################################################################
            #
            #BSUB -J %JOBNAME%
            #BSUB -oo %SCRATCH_DIR%/%HPCPROJ%/%HPCUSER%/%EXPID%/LOG_%EXPID%/%JOBNAME%_%J.out
            #BSUB -eo %SCRATCH_DIR%/%HPCPROJ%/%HPCUSER%/%EXPID%/LOG_%EXPID%/%JOBNAME%_%J.err
            #BSUB -W %WALLCLOCK%
            #BSUB -n %NUMPROC%
            #BSUB -R "span[ptile=16]"
            #
            ###############################################################################
            """)

    PARALLEL = textwrap.dedent("""
            #!/bin/sh
            ###############################################################################
            #                   %TASKTYPE% %EXPID% EXPERIMENT
            ###############################################################################
            #
            #BSUB -J %JOBNAME%
            #BSUB -oo %SCRATCH_DIR%/%HPCPROJ%/%HPCUSER%/%EXPID%/LOG_%EXPID%/%JOBNAME%_%J.out
            #BSUB -eo %SCRATCH_DIR%/%HPCPROJ%/%HPCUSER%/%EXPID%/LOG_%EXPID%/%JOBNAME%_%J.err
            #BSUB -W %WALLCLOCK%
            #BSUB -n %NUMPROC%
            #BSUB -R "span[ptile=16]"
            #
            ###############################################################################
            """)