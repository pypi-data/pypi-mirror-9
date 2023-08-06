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

"""
Main module for autosubmit. Only contains an interface class to all functionality implemented on autosubmit
"""

import os
import re

from autosubmit.job.job_common import Status
from autosubmit.job.job_common import StatisticsSnippet
from autosubmit.config.basicConfig import BasicConfig
from autosubmit.date.chunk_date_lib import *
from autosubmit.queue.localqueue import LocalQueue


class Job:
    """
    Class to handle all the tasks with Jobs at HPC.
    A job is created by default with a name, a jobid, a status and a type.
    It can have children and parents. The inheritance reflects the dependency between jobs.
    If Job2 must wait until Job1 is completed then Job2 is a child of Job1. Inversely Job1 is a parent of Job2
    """

    def __init__(self, name, jobid, status, priority):
        self._queue = None
        self.queue_name = None
        self.section = None
        self.wallclock = None
        self.tasks = None
        self.threads = None
        self.processors = None
        self.chunk = None
        self.member = None
        self.date = None
        self.name = name
        self._long_name = None
        self.long_name = name
        self._short_name = None
        self.short_name = name

        self.id = jobid
        self.file = None
        self.status = status
        self.priority = priority
        self._parents = set()
        self._children = set()
        self.fail_count = 0
        self.expid = name.split('_')[0]
        self._complete = True
        self.parameters = dict()
        self._tmp_path = BasicConfig.LOCAL_ROOT_DIR + "/" + self.expid + "/" + BasicConfig.LOCAL_TMP_DIR + "/"
        self._ancestors = None

    def __getstate__(self):
        odict = self.__dict__
        if '_queue' in odict:
            odict = odict.copy()    # copy the dict since we change it
            del odict['_queue']              # remove filehandle entry
        return odict

    def delete(self):
        """

        """
        del self.name
        del self._long_name
        del self._short_name
        del self.id
        del self.status
        del self.priority
        del self._parents
        del self._children
        del self.fail_count
        del self.expid
        del self._complete
        del self.parameters
        del self._tmp_path
        del self

    def print_job(self):
        """
        Prints debug information about the job
        :return None
        """
        Log.debug('NAME: {0}', self.name)
        Log.debug('JOBID: {0}', self.id)
        Log.debug('STATUS: {0}', self.status)
        Log.debug('TYPE: {0}', self.priority)
        Log.debug('PARENTS: {0}', [p.name for p in self.parents])
        Log.debug('CHILDREN: {0}', [c.name for c in self.children])
        Log.debug('FAIL_COUNT: {0}', self.fail_count)
        Log.debug('EXPID: {0}', self.expid)

    # Properties
    @property
    def parents(self):
        """
        Return parent jobs list

        :return: list of parent jobs
        """
        return self._parents

    def get_queue(self):
        """
        Returns the queue to be used by the job. Chooses between serial and parallel queue

        :return hpcqueue object for the job to use
        """
        if self.processors > 1:
            return self._queue
        else:
            return self._queue.get_serial_queue()

    def set_queue(self, value):
        """
        Sets the HPCqueue to be used by the job.

        :return: None
        """
        self._queue = value

    @property
    def ancestors(self):
        """
        Returns all job's ancestors

        :return: job ancestors' list
        """
        if self._ancestors is None:
            self._ancestors = set()
            if self.has_parents():
                for parent in self.parents:
                    self._ancestors.add(parent)
                    for ancestor in parent.ancestors:
                        self._ancestors.add(ancestor)
        return self._ancestors

    @property
    def children(self):
        """
        Returns a list containing all children of the job

        :return: list of children jobs
        """
        return self._children

    @property
    def long_name(self):
        """
        Job's long name
        """
        if hasattr(self, '_long_name'):
            return self._long_name
        else:
            return self.name

    @long_name.setter
    def long_name(self, value):
        self._long_name = value

    @property
    def short_name(self):
        """
        Job short name
        """
        return self._short_name

    @short_name.setter
    def short_name(self, value):
        n = value.split('_')
        if len(n) == 5:
            self._short_name = n[1][:6] + "_" + n[2][2:] + "_" + n[3] + n[4][:1]
        elif len(n) == 4:
            self._short_name = n[1][:6] + "_" + n[2][2:] + "_" + n[3][:1]
        elif len(n) == 2:
            self._short_name = n[1]
        else:
            self._short_name = n[0][:15]

    def log_job(self):
        """
        Prints job information in log
        """
        Log.info("{0}\t{1}\t{2}", "Job Name", "Job Id", "Job Status")
        Log.info("{0}\t\t{1}\t{2}", self.name, self.id, self.status)

    def get_all_children(self):
        """
        Returns a list with all job's children and all it's descendants
        """
        job_list = list()
        for job in self.children:
            job_list.append(job)
            job_list += job.get_all_children()
        # convert the list into a Set to remove duplicates and the again to a list
        return list(set(job_list))

    def print_parameters(self):
        """
        Print job parameters in log
        :return:
        """
        Log.info(self.parameters)

    def inc_fail_count(self):
        """
        Increments fail count
        """
        self.fail_count += 1

    def add_parent(self, *new_parent):
        """
        Add parents for the job. It also adds current job as a child for all the new parents

        :param new_parent: job parent
        """
        self._ancestors = None
        for parent in new_parent:
            self._parents.add(parent)
            parent.__add_child(self)

    def __add_child(self, new_child):
        """
        Adds a new child to the job

        :param new_child: new child to add
        """
        self.children.add(new_child)

    def delete_parent(self, parent):
        """
        Remove a parent from the job

        :param parent: parent to remove
        """
        self._ancestors = None
        # careful, it is only possible to remove one parent at a time
        self.parents.remove(parent)

    def delete_child(self, child):
        """
        Removes a child from the job

        :param child: child to remove
        """
        # careful it is only possible to remove one child at a time
        self.children.remove(child)

    def has_children(self):
        """
        Returns true if job has any children, else return false

        :return: bool
        """
        return self.children.__len__()

    def has_parents(self):
        """
        Returns true if job has any parents, else return false

        :return:
        """
        return self.parents.__len__()

    def compare_by_status(self, other):
        """
        Compare jobs by status value

        :param other: job to compare
        :return: comparison result
        """
        return cmp(self.status(), other.status)

    def compare_by_type(self, other):
        """
        Compare jobs by priority

        :param other: job to compare
        :return: comparison result
        """
        return cmp(self.priority(), other.type)

    def compare_by_id(self, other):
        """
        Compare jobs by ID

        :param other: job to compare
        :return: comparison result
        """
        return cmp(self.id(), other.id)

    def compare_by_name(self, other):
        """
        Compare jobs by name

        :param other: job to compare
        :return: comparison result
        """
        return cmp(self.name, other.name)

    def _get_from_completed(self, index):
        """
        Returns value from given index position in completed file asociated to job

        :param index: position to retrieve
        :return: value in index position
        """
        logname = self._tmp_path + self.name + '_COMPLETED'
        if os.path.exists(logname):
            split_line = open(logname).readline().split()
            if len(split_line) >= index + 1:
                return split_line[index]
            else:
                return 0
        else:
            return 0

    def check_end_time(self):
        """
        Returns end time from completed file

        :return: completed date and time
        """
        return self._get_from_completed(0)

    def check_queued_time(self):
        """
        Returns job's waiting time in HPC

        :return: total time waiting in HPC queue
        """
        return self._get_from_completed(1)

    def check_run_time(self):
        """
        Returns job's running time

        :return: total time running
        """
        return self._get_from_completed(2)

    def check_failed_times(self):
        """
        Returns number of failed attempts before completing the job

        :return: failed attempts to run
        """
        return self._get_from_completed(3)

    def check_fail_queued_time(self):
        """
        Returns total time spent waiting for failed jobs

        :return: total time waiting in HPC queue for failed jobs
        """
        return self._get_from_completed(4)

    def check_fail_run_time(self):
        """
        Returns total time running for failed jobs

        :return: total time running in HPC  for failed jobs
        """
        return self._get_from_completed(5)

    def check_completion(self):
        """
        Check the presence of *COMPLETED* file and touch a Checked or failed file
        """
        logname = self._tmp_path + self.name + '_COMPLETED'
        if os.path.exists(logname):
            self._complete = True
            os.system('touch ' + self._tmp_path + self.name + 'Checked')
            self.status = Status.COMPLETED
        else:
            os.system('touch ' + self._tmp_path + self.name + 'Failed')
            self.status = Status.FAILED

    def remove_dependencies(self):
        """
        Checks if job is completed and then remove dependencies for childs
        """
        if self._complete:
            self.status = Status.COMPLETED
            # job_logger.info("Job is completed, we are now removing the dependency in"
            # " his %s child/children:" % self.has_children())
            for child in self.children:
                # job_logger.debug("number of Parents:",child.has_parents())
                if child.get_parents().__contains__(self):
                    child.delete_parent(self)
        else:
            # job_logger.info("The checking in check_completion tell us that job %s has failed" % self.name)
            self.status = Status.FAILED

    def update_parameters(self):
        """
        Refresh parameters value
        """
        parameters = self.parameters
        parameters['JOBNAME'] = self.name
        parameters['FAIL_COUNT'] = str(self.fail_count)

        parameters['SDATE'] = self.date
        parameters['MEMBER'] = self.member
        if self.chunk is None:
            parameters['CHUNK'] = '1'
        else:
            parameters['CHUNK'] = self.chunk
            chunk = self.chunk
            total_chunk = int(parameters['NUMCHUNKS'])
            chunk_length = int(parameters['CHUNKSIZE'])
            chunk_unit = parameters['CHUNKSIZEUNIT'].lower()
            cal = parameters['CALENDAR'].lower()
            chunk_start = chunk_start_date(self.date, chunk, chunk_length, chunk_unit, cal)
            chunk_end = chunk_end_date(chunk_start, chunk_length, chunk_unit, cal)
            run_days = running_days(chunk_start, chunk_end, cal)
            chunk_end_days = previous_days(self.date, chunk_end, cal)
            day_before = previous_day(self.date, cal)
            chunk_end_1 = previous_day(chunk_end, cal)
            parameters['DAY_BEFORE'] = day_before
            parameters['Chunk_START_DATE'] = chunk_start
            parameters['Chunk_END_DATE'] = chunk_end_1
            parameters['RUN_DAYS'] = str(run_days)
            parameters['Chunk_End_IN_DAYS'] = str(chunk_end_days)

            chunk_start_m = get_month(chunk_start)
            chunk_start_y = get_year(chunk_start)

            parameters['Chunk_START_YEAR'] = str(chunk_start_y)
            parameters['Chunk_START_MONTH'] = str(chunk_start_m)
            if total_chunk == chunk:
                parameters['Chunk_LAST'] = 'TRUE'
            else:
                parameters['Chunk_LAST'] = 'FALSE'

        parameters['NUMPROC'] = self.processors
        parameters['NUMTHREADS'] = self.threads
        parameters['NUMTASK'] = self.tasks
        parameters['WALLCLOCK'] = self.wallclock
        parameters['TASKTYPE'] = self.section

        queue = self.get_queue()
        parameters['HPCUSER'] = queue.user
        parameters['HPCPROJ'] = queue.project
        parameters['HPCTYPE'] = queue.type
        parameters['HPCVERSION'] = queue.version
        parameters['SCRATCH_DIR'] = queue.scratch

        self.parameters = parameters

        return parameters

    def update_content(self, project_dir):
        """
        Create the script content to be run for the job

        :param project_dir: project directory
        :return: script code
        """
        if self.parameters['PROJECT_TYPE'].lower() != "none":
            template = file(os.path.join(project_dir, self.file), 'r').read()
        else:
            template = ''
        queue = self.get_queue()
        if isinstance(queue, LocalQueue):
            stats_header = StatisticsSnippet.AS_HEADER_LOC
            stats_tailer = StatisticsSnippet.AS_TAILER_LOC
        else:
            stats_header = StatisticsSnippet.AS_HEADER_REM
            stats_tailer = StatisticsSnippet.AS_TAILER_REM

        template_content = ''.join([queue.get_header(self),
                                   stats_header,
                                   template,
                                   stats_tailer])

        return template_content

    def create_script(self, as_conf):
        """
        Creates script file to be run for the job

        :param as_conf: configuration object
        :return: script's filename
        """
        parameters = self.update_parameters()
        template_content = self.update_content(as_conf.get_project_dir())
        # print "jobType: %s" % self._type
        # print template_content

        for key, value in parameters.items():
            # print "%s:\t%s" % (key,parameters[key])
            template_content = template_content.replace("%" + key + "%", str(parameters[key]))

        scriptname = self.name + '.cmd'
        file(self._tmp_path + scriptname, 'w').write(template_content)

        return scriptname

    def check_script(self, as_conf):
        """
        Checks if script is well formed

        :param as_conf: configuration file
        :return: true if not problem has been detected, false otherwise
        """
        parameters = self.update_parameters()
        template_content = self.update_content(as_conf.get_project_dir())

        variables = re.findall('%' + '(\w+)' + '%', template_content)
        # variables += re.findall('%%'+'(.+?)'+'%%', template_content)
        out = set(parameters).issuperset(set(variables))

        if not out:
            Log.warning("The following set of variables to be substituted in template script is not part of "
                        "parameters set: ")
            Log.warning(set(variables) - set(parameters))
        else:
            self.create_script(as_conf)

        return out


if __name__ == "__main__":
    mainJob = Job('uno', '1', Status.READY, 0)
    job1 = Job('uno', '1', Status.READY, 0)
    job2 = Job('dos', '2', Status.READY, 0)
    job3 = Job('tres', '3', Status.READY, 0)
    jobs = [job1, job2, job3]
    mainJob.add_parent(*jobs)
    Log.info(mainJob.parents)
    # mainJob.set_children(jobs)
    # job1.__add_child(mainJob)
    # job2.__add_child(mainJob)
    # job3.__add_child(mainJob)
    Log.info(mainJob.get_all_children())
    Log.info(mainJob.children)
    job3.check_completion()
    Log.info("Number of Parents: ", mainJob.has_parents())
    Log.info("number of children : ", mainJob.has_children())
    mainJob.print_job()
    mainJob.delete()
#
