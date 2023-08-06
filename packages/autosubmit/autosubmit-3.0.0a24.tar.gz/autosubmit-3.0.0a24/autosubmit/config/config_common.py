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
from ConfigParser import SafeConfigParser
import os
import platform
import re
from os import listdir
from commands import getstatusoutput

from autosubmit.config.log import Log
from autosubmit.config.config_parser import config_parser
from autosubmit.config.config_parser import expdef_parser
from autosubmit.config.config_parser import projdef_parser
from autosubmit.config.basicConfig import BasicConfig

from autosubmit.queue.psqueue import PsQueue
from autosubmit.queue.lsfqueue import LsfQueue
from autosubmit.queue.pbsqueue import PBSQueue
from autosubmit.queue.sgequeue import SgeQueue
from autosubmit.queue.ecqueue import EcQueue


class AutosubmitConfig:
    """Class to handle experiment configuration coming from file or database"""

    def __init__(self, expid):
        self._conf_parser_file = BasicConfig.LOCAL_ROOT_DIR + "/" + expid + "/conf/" + "autosubmit_" + expid + ".conf"
        self._exp_parser_file = BasicConfig.LOCAL_ROOT_DIR + "/" + expid + "/conf/" + "expdef_" + expid + ".conf"

    @property
    def experiment_file(self):
        return self._exp_parser_file

    def get_project_dir(self):
        dir_templates = os.path.join(BasicConfig.LOCAL_ROOT_DIR, self.get_expid(), BasicConfig.LOCAL_PROJ_DIR)
        # Getting project name for each type of project
        if self.get_project_type().lower() == "local":
            dir_templates = os.path.join(dir_templates, os.path.split(self.get_local_project_path())[1])
        elif self.get_project_type().lower() == "git":
            dir_templates = self.get_git_project_origin().split('.')[-2]
        return dir_templates

    def check_conf(self):
        self._conf_parser = config_parser(self._conf_parser_file)
        self._exp_parser = expdef_parser(self._exp_parser_file)

    def check_proj(self):
        self._proj_parser_file = self.get_file_project_conf()
        if self._proj_parser_file == '':
            self._proj_parser = None
        else:
            self._proj_parser_file = os.path.join(self.get_project_dir(), self._proj_parser_file)
            self._proj_parser = projdef_parser(self._proj_parser_file)

    def reload(self):
        self._conf_parser = config_parser(self._conf_parser_file)
        self._exp_parser_file = self._conf_parser.get('config', 'EXPDEFFILE')
        self._exp_parser = expdef_parser(self._exp_parser_file)
        project_type = self.get_project_type()
        if project_type != "none":
            self.check_proj()

    def load_parameters(self):
        expdef = []
        for section in self._exp_parser.sections():
            expdef += self._exp_parser.items(section)

        for section in self._conf_parser.sections():
            expdef += self._conf_parser.items(section)

        parameters = dict()
        for item in expdef:
            parameters[item[0]] = item[1]

        project_type = self.get_project_type()
        if project_type != "none" and self._proj_parser is not None:
            # Load project parameters
            Log.debug("Loading project parameters...")
            parameters2 = parameters.copy()
            parameters2.update(self.load_project_parameters())
            parameters = parameters2

        return parameters

    def load_project_parameters(self):
        projdef = []
        for section in self._proj_parser.sections():
            projdef += self._proj_parser.items(section)

        parameters = dict()
        for item in projdef:
            parameters[item[0]] = item[1]

        return parameters

    @staticmethod
    def print_parameters(title, parameters):
        """Prints the parameters table in a tabular mode"""
        Log.info(title)
        Log.info("----------------------")
        Log.info("{0:<{col1}}| {1:<{col2}}".format("-- Parameter --", "-- Value --", col1=15, col2=15))
        for i in parameters:
            Log.info("{0:<{col1}}| {1:<{col2}}".format(i[0], i[1], col1=15, col2=15))
        Log.info("")

    def check_parameters(self):
        """Function to check configuration of Autosubmit.
        Returns True if all variables are set.
        If some parameter do not exist, the function returns False.

        :retruns: bool
        """
        result = True

        for section in self._conf_parser.sections():
            self.print_parameters("AUTOSUBMIT PARAMETERS - " + section, self._conf_parser.items(section))
            if "" in [item[1] for item in self._conf_parser.items(section)]:
                result = False
        for section in self._exp_parser.sections():
            self.print_parameters("EXPERIMENT PARAMETERS - " + section, self._exp_parser.items(section))
            if "" in [item[1] for item in self._exp_parser.items(section)]:
                result = False

        project_type = self.get_project_type()
        if project_type != "none" and self._proj_parser is not None:
            for section in self._proj_parser.sections():
                self.print_parameters("PROJECT PARAMETERS - " + section, self._proj_parser.items(section))
                if "" in [item[1] for item in self._proj_parser.items(section)]:
                    result = False

        return result

    def get_expid(self):
        return self._conf_parser.get('config', 'EXPID')

    def set_expid(self, exp_id):
        # Autosubmit conf
        content = file(self._conf_parser_file).read()
        if re.search('EXPID =.*', content):
            content = content.replace(re.search('EXPID =.*', content).group(0), "EXPID = " + exp_id)
        file(self._conf_parser_file, 'w').write(content)
        # Experiment conf
        content = file(self._exp_parser_file).read()
        if re.search('EXPID =.*', content):
            content = content.replace(re.search('EXPID =.*', content).group(0), "EXPID = " + exp_id)
        file(self._exp_parser_file, 'w').write(content)

    def get_project_type(self):
        return self._exp_parser.get('project', 'PROJECT_TYPE').lower()

    def get_file_project_conf(self):
        return self._exp_parser.get('project_files', 'FILE_PROJECT_CONF').lower()

    def get_git_project_origin(self):
        return self._exp_parser.get('git', 'PROJECT_ORIGIN').lower()

    def get_git_project_branch(self):
        return self._exp_parser.get('git', 'PROJECT_BRANCH').lower()

    def get_git_project_commit(self):
        return self._exp_parser.get('git', 'PROJECT_COMMIT').lower()

    def set_git_project_commit(self):
        """Function to register in the configuration the commit SHA of the git project version."""
        save = False
        project_branch_sha = None
        project_name = listdir(BasicConfig.LOCAL_ROOT_DIR + "/" + self.get_expid() + "/" +
                               BasicConfig.LOCAL_PROJ_DIR)[0]
        (status1, output) = getstatusoutput("cd " + BasicConfig.LOCAL_ROOT_DIR + "/" + self.get_expid() + "/" +
                                            BasicConfig.LOCAL_PROJ_DIR + "/" + project_name)
        (status2, output) = getstatusoutput("cd " + BasicConfig.LOCAL_ROOT_DIR + "/" + self.get_expid() + "/" +
                                            BasicConfig.LOCAL_PROJ_DIR + "/" + project_name + "; " +
                                            "git rev-parse --abbrev-ref HEAD")
        if status1 == 0 and status2 == 0:
            project_branch = output
            Log.debug("Project branch is: " + project_branch)

            (status1, output) = getstatusoutput("cd " + BasicConfig.LOCAL_ROOT_DIR + "/" + self.get_expid() + "/" +
                                                BasicConfig.LOCAL_PROJ_DIR + "/" + project_name)
            (status2, output) = getstatusoutput("cd " + BasicConfig.LOCAL_ROOT_DIR + "/" + self.get_expid() + "/" +
                                                BasicConfig.LOCAL_PROJ_DIR + "/" + project_name + "; " +
                                                "git rev-parse HEAD")
            if status1 == 0 and status2 == 0:
                project_sha = output
                save = True
                Log.debug("Project commit SHA is: " + project_sha)
                project_branch_sha = project_branch + " " + project_sha
            else:
                Log.critical("Failed to retrieve project commit SHA...")

        else:
            Log.critical("Failed to retrieve project branch...")

            # register changes
        if save:
            content = file(self._exp_parser_file).read()
            if re.search('PROJECT_COMMIT =.*', content):
                content = content.replace(re.search('PROJECT_COMMIT =.*', content).group(0),
                                          "PROJECT_COMMIT = " + project_branch_sha)
            file(self._exp_parser_file, 'w').write(content)
            Log.debug("Project commit SHA succesfully registered to the configuration file.")
        else:
            Log.critical("Changes NOT registered to the configuration file...")

    def get_svn_project_url(self):
        return self._exp_parser.get('svn', 'PROJECT_URL').lower()

    def get_svn_project_revision(self):
        return self._exp_parser.get('svn', 'PROJECT_REVISION').lower()

    def get_local_project_path(self):
        return self._exp_parser.get('local', 'PROJECT_PATH').lower()

    def get_date_list(self):
        return self._exp_parser.get('experiment', 'DATELIST').split(' ')

    def get_starting_chunk(self):
        return int(self._exp_parser.get('experiment', 'CHUNKINI'))

    def get_num_chunks(self):
        return int(self._exp_parser.get('experiment', 'NUMCHUNKS'))

    def get_member_list(self):
        return self._exp_parser.get('experiment', 'MEMBERS').split(' ')

    def get_rerun(self):
        return self._exp_parser.get('rerun', 'RERUN').lower()

    def get_chunk_list(self):
        return self._exp_parser.get('rerun', 'CHUNKLIST')

    def get_platform(self):
        return self._exp_parser.get('experiment', 'HPCARCH').lower()

    def set_platform(self, hpc):
        content = file(self._exp_parser_file).read()
        if re.search('HPCARCH =.*', content):
            content = content.replace(re.search('HPCARCH =.*', content).group(0), "HPCARCH = " + hpc)
        file(self._exp_parser_file, 'w').write(content)

    def set_version(self, autosubmit_version):
        content = file(self._conf_parser_file).read()
        if re.search('AUTOSUBMIT_VERSION =.*', content):
            content = content.replace(re.search('AUTOSUBMIT_VERSION =.*', content).group(0),
                                      "AUTOSUBMIT_VERSION = " + autosubmit_version)
        file(self._conf_parser_file, 'w').write(content)

    def set_local_root(self):
        content = file(self._conf_parser_file).read()
        if re.search('AUTOSUBMIT_LOCAL_ROOT =.*', content):
            content = content.replace(re.search('AUTOSUBMIT_LOCAL_ROOT =.*', content).group(0),
                                      "AUTOSUBMIT_LOCAL_ROOT = " + BasicConfig.LOCAL_ROOT_DIR)
        file(self._conf_parser_file, 'w').write(content)

    def get_total_jobs(self):
        return int(self._conf_parser.get('config', 'TOTALJOBS'))

    def get_max_waiting_jobs(self):
        return int(self._conf_parser.get('config', 'MAXWAITINGJOBS'))

    def get_safetysleeptime(self):
        return int(self._conf_parser.get('config', 'SAFETYSLEEPTIME'))

    def set_safetysleeptime(self, sleep_time):
        content = file(self._conf_parser_file).read()
        content = content.replace(re.search('SAFETYSLEEPTIME =.*', content).group(0),
                                  "SAFETYSLEEPTIME = %d" % sleep_time)
        file(self._conf_parser_file, 'w').write(content)

    def get_retrials(self):
        return int(self._conf_parser.get('config', 'RETRIALS'))

    @staticmethod
    def read_queues_conf(expid):
        parser = SafeConfigParser()
        parser.optionxform = str
        parser.read(os.path.join(BasicConfig.LOCAL_ROOT_DIR, expid, 'conf', "queues_" + expid + ".conf"))

        queues = dict()
        local_queue = PsQueue(expid)
        local_queue.name = 'local'
        local_queue.type = 'ps'
        local_queue.set_host(platform.node())
        local_queue.set_scratch(BasicConfig.LOCAL_ROOT_DIR)
        local_queue.set_project(expid)
        local_queue.set_user(BasicConfig.LOCAL_TMP_DIR)
        local_queue.update_cmds()

        queues['local'] = local_queue
        for section in parser.sections():
            queue_type = AutosubmitConfig.get_option(parser, section, 'TYPE', '').lower()
            queue_version = AutosubmitConfig.get_option(parser, section, 'VERSION', None)
            queue = None
            if queue_type == 'pbs':
                queue = PBSQueue(expid, queue_version)
            elif queue_type == 'sge':
                queue = SgeQueue(expid)
            elif queue_type == 'ps':
                queue = PsQueue(expid)
            elif queue_type == 'lsf':
                queue = LsfQueue(expid)
            elif queue_type == 'ecaccess':
                queue = EcQueue(expid, queue_version)
            elif queue_type == '':
                Log.error("Queue type not specified".format(queue_type))
                exit(1)
            else:
                Log.error("Queue type {0} not defined".format(queue_type))
                exit(1)

            queue.type = queue_type
            if AutosubmitConfig.get_option(parser, section, 'ADD_PROJECT_TO_HOST', '').lower() == 'true':
                host = '{0}-{1}'.format(AutosubmitConfig.get_option(parser, section, 'HOST', None),
                                        AutosubmitConfig.get_option(parser, section, 'PROJECT', None))
            else:
                host = AutosubmitConfig.get_option(parser, section, 'HOST', None)
            queue.set_host(host)
            queue.set_project(AutosubmitConfig.get_option(parser, section, 'PROJECT', None))
            queue.set_user(AutosubmitConfig.get_option(parser, section, 'USER', None))
            queue.set_scratch(AutosubmitConfig.get_option(parser, section, 'SCRATCH_DIR', None))
            queue.name = section.lower()
            queue.update_cmds()
            queues[section.lower()] = queue

        for section in parser.sections():
            if parser.has_option(section, 'SERIAL_QUEUE'):
                queues[section.lower()].set_serial_queue(queues[AutosubmitConfig.get_option(parser, section,
                                                                                            'SERIAL_QUEUE',
                                                                                            None).lower()])

        return queues

    @staticmethod
    def get_option(parser, section, option, default):
        if parser.has_option(section, option):
            return parser.get(section, option)
        else:
            return default


