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
Module containing functions to manage autosubmit's database.
"""
import os
import sqlite3
import string

from autosubmit.config.log import Log
from autosubmit.config.basicConfig import BasicConfig

CURRENT_DATABASE_VERSION = 1


def create_db(qry):
    """
    Creates a new database for autosubmit

    :param qry: query to create the new database
    :type qry: str    """

    try:
        (conn, cursor) = open_conn()
    except DbException as e:
        Log.error('Connection to database could not be established: {0}', e.message)
        return False

    try:
        cursor.execute(qry)
    except sqlite3.Error:
        close_conn(conn, cursor)
        Log.error('The database can not be created.' + 'DB file:' + BasicConfig.DB_PATH)
        return False

    conn.commit()
    close_conn(conn, cursor)
    return True


def _set_experiment(name, description, version):
    """
    Stores experiment in database

    :param name: experiment's name
    :type name: str
    :param description: experiment's description
    :type description: str
    """
    if not check_db():
        return False
    name = check_name(name)
    if name == '':
        return False
    try:
        (conn, cursor) = open_conn()
    except DbException as e:
        Log.error('Connection to database could not be established: {0}', e.message)
        return False
    try:
        cursor.execute('INSERT INTO experiment (name, description, autosubmit_version) VALUES (:name, :description, '
                       ':version)',
                       {'name': name, 'description': description, 'version': version})
    except sqlite3.IntegrityError as e:
        close_conn(conn, cursor)
        Log.error('Could not register experiment: {0}'.format(e))
        return False

    conn.commit()
    close_conn(conn, cursor)
    return True


def check_experiment_exists(name):
    """
    Checks if exist an experiment with the given name.

    :param name: Experiment name
    :type name: str
    :return: If experiment exists returns true, if not returns false
    :rtype: bool
    """
    if not check_db():
        return False
    name = check_name(name)
    if name == '':
        return False

    try:
        (conn, cursor) = open_conn()
    except DbException as e:
        Log.error('Connection to database could not be established: {0}', e.message)
        return False
    conn.isolation_level = None

    # SQLite always return a unicode object, but we can change this
    # behaviour with the next sentence
    conn.text_factory = str
    cursor.execute('select name from experiment where name=:name', {'name': name})
    row = cursor.fetchone()
    close_conn(conn, cursor)
    if row is None:
        Log.error('The experiment name "{0}" does not exist yet!!!', name)
        return False
    return True


def new_experiment(hpc, description, version):
    """
    Stores a new experiment on the database and generates its identifier

    :param hpc: name of the main HPC to be used by the experiment
    :type hpc: str
    :param description: experiment's description
    :type description: str
    :return: experiment id for the new experiment
    :rtype: str
    """
    last_exp_name = last_name(hpc)
    if last_exp_name == '':
        return ''
    if last_exp_name == 'empty':
        if hpc == 'test':
            new_name = 'test000'
        else:
            new_name = hpc[0]+'000'
    else:
        new_name = _next_name(last_exp_name)
    if new_name == '':
        return ''
    if not _set_experiment(new_name, description, version):
        return ''
    Log.info('The new experiment "{0}" has been registered.', new_name)
    return new_name


def copy_experiment(name, hpc, description, version):
    """
    Creates a new experiment by copying an existing experiment

    :param name: identifier of experiment to copy
    :type name: str
    :param hpc: name of the main HPC to be used by the experiment
    :type hpc: str
    :param description: experiment's description
    :type description: str
    :return: experiment id for the new experiment
    :rtype: str
    """
    if not check_experiment_exists(name):
        return ''
    new_name = new_experiment(hpc, description, version)
    return new_name


def base36encode(number, alphabet=string.digits + string.ascii_lowercase):
    """
    Convert positive integer to a base36 string.

    :param number: number to convert
    :type number: int
    :param alphabet: set of characters to use
    :type alphabet: str
    :return: number's base36 string value
    :rtype: str
    """
    if not isinstance(number, (int, long)):
        raise TypeError('number must be an integer')

    # Special case for zero
    if number == 0:
        return '0'

    base36 = ''

    sign = ''
    if number < 0:
        sign = '-'
        number = - number

    while number > 0:
        number, i = divmod(number, len(alphabet))
        # noinspection PyAugmentAssignment
        base36 = alphabet[i] + base36

    return sign + base36


def base36decode(number):
    """
    Converts a base36 string to a positive integer

    :param number: base36 string to convert
    :type number: str
    :return: number's integer value
    :rtype: int
    """
    return int(number, 36)


def _next_name(name):
    """
    Get next experiment identifier

    :param name: previous experiment identifier
    :type name: str
    :return: new experiment identifier
    :rtype: str
    """
    name = check_name(name)
    if name == '':
        return ''
    # Convert the name to base 36 in number add 1 and then encode it
    return base36encode(base36decode(name) + 1)


def last_name(hpc):
    """
    Gets last experiment identifier used for HPC

    :param hpc: HPC name
    :type hpc: str
    :return: last experiment identifier used for HPC, 'empty' if there is none
    :rtype: str
    """
    if not check_db():
        return ''
    try:
        (conn, cursor) = open_conn()
    except DbException as e:
        Log.error('Connection to database could not be established: {0}', e.message)
        return ''
    conn.text_factory = str
    if hpc == 'test':
        hpc_name = 'test'
    else:
        hpc_name = hpc[0]
    hpc_name += '___'
    cursor.execute('SELECT name '
                   'FROM experiment '
                   'WHERE rowid=(SELECT max(rowid) FROM experiment WHERE name LIKE "' + hpc_name + '")')
    row = cursor.fetchone()
    if row is None:
        row = ('empty', )
    close_conn(conn, cursor)
    return row[0]


def delete_experiment(name):
    """
    Removes experiment from database

    :param name: experiment identifier
    :type name: str
    :return: True if delete is succesful
    :rtype: bool
    """
    if not check_db():
        return False
    name = check_name(name)
    if name == '':
        return False
    try:
        (conn, cursor) = open_conn()
    except DbException as e:
        Log.error('Connection to database could not be established: {0}', e.message)
        return False
    cursor.execute('DELETE FROM experiment '
                   'WHERE name=:name', {'name': name})
    row = cursor.fetchone()
    if row is None:
        Log.debug('The experiment {0} has been deleted!!!', name)
    close_conn(conn, cursor)
    return True


def check_name(name):
    """
    Checks if it is a valid experiment identifier

    :param name: experiment identifier to check
    :type name: str
    :return: name if is valid, terminates program otherwise
    :rtype: str
    """
    name = name.lower()
    if len(name) < 4 or not name.isalnum():
        Log.error("So sorry, but the name must have at least 4 alphanumeric chars!!!")
        return ''
    return name


def check_db():
    """
    Checks if database file exist

    :return: None if exists, terminates program if not
    """

    if not os.path.exists(BasicConfig.DB_PATH):
        Log.error('Some problem has happened...check the database file.' + 'DB file:' + BasicConfig.DB_PATH)
        return False
    return True


def open_conn():
    """
    Opens a connection to database

    :return: connection object, cursor object
    :rtype: sqlite3.Connection, sqlite3.Cursor
    """
    conn = sqlite3.connect(BasicConfig.DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT version '
                       'FROM db_version;')
        row = cursor.fetchone()
        if row is None:
            version = 0
        else:
            version = row[0]
    except sqlite3.OperationalError:
        try:
            cursor.execute('SELECT type '
                           'FROM experiment;')
            version = -1
        except sqlite3.Error:
            version = 0
    if version < CURRENT_DATABASE_VERSION:
        if not _update_database(version, cursor):
            raise DbException('Database version could not be updated')
    elif version > CURRENT_DATABASE_VERSION:
        Log.critical('Database version is not compatible with this autosubmit version. Please execute pip install '
                     'autosubmit --upgrade')
        raise DbException('Database version not compatible')
    return conn, cursor


def close_conn(conn, cursor):
    """
    Commits changes and close connection to database

    :param conn: connection to close
    :type conn: sqlite3.Connection
    :param cursor: cursor to close
    :type cursor: sqlite3.Cursor
    """
    conn.commit()
    cursor.close()
    conn.close()
    return


def _update_database(version, cursor):

    Log.info("Autosubmit's database version is {0}. Current version is {1}. Updating...",
             version, CURRENT_DATABASE_VERSION)
    try:
        # For databases from Autosubmit 2
        if version <= -1:
            cursor.executescript('CREATE TABLE experiment_backup(id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, '
                                 'name VARCHAR NOT NULL, type VARCHAR, autosubmit_version VARCHAR, '
                                 'description VARCHAR NOT NULL, model_branch VARCHAR, template_name VARCHAR, '
                                 'template_branch VARCHAR, ocean_diagnostics_branch VARCHAR);'
                                 'INSERT INTO experiment_backup (name,type,description,model_branch,template_name,'
                                 'template_branch,ocean_diagnostics_branch) SELECT name,type,description,model_branch,'
                                 'template_name,template_branch,ocean_diagnostics_branch FROM experiment;'
                                 'UPDATE experiment_backup SET autosubmit_version = "2";'
                                 'DROP TABLE experiment;'
                                 'ALTER TABLE experiment_backup RENAME TO experiment;')
        if version <= 0:
            # Autosubmit beta version. Create db_version table
            cursor.executescript('CREATE TABLE db_version(version INTEGER NOT NULL);'
                                 'INSERT INTO db_version (version) VALUES (1);'
                                 'ALTER TABLE experiment ADD COLUMN autosubmit_version VARCHAR;'
                                 'UPDATE experiment SET autosubmit_version = "3.0.0b" '
                                 'WHERE autosubmit_version NOT NULL;')
        cursor.execute('UPDATE db_version SET version={0};'.format(CURRENT_DATABASE_VERSION))
    except sqlite3.Error as e:
        Log.critical('Can not update database: {0}', e)
        return False
    Log.info("Update completed")
    return True


class DbException(Exception):
    """
    Exception class for database errors
    """
    def __init__(self, message):
        self.message = message