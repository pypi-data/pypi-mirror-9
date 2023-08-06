#!/usr/bin/env python3

# The MIT License (MIT)
#
# Copyright (c) 2014-2015 Benedikt Schmitt <benedikt@benediktschmitt.de>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
About
-----

Extends the EMSM by a backup manager.

Download
--------

You can find the latest version of this plugin in the EMSM
`GitHub repository <https://github.com/benediktschmitt/emsm>`_.

Configuration
-------------

.. code-block:: ini

    [backups]
    archive_format = bztar
    restore_message = This world is about to be ressetted to an earlier state.
    restore_delay = 5
    max_storage_size = 30
    backup_logs = yes

**archive_format**

    Is the name of the archive format used to create the backups. This string has
    to be listed in *shutil.get_archive_formats()*. Usually, there should be at
    least *zip* or *tar* available.

**restore_message**

    Is send to the world's chat before restoring the world.

**restore_delay**

    Seconds between sending the *restore_message* to the chat and starting
    the restore.

**max_storage_size**

    Maximum number of backups in the storage folder, before older backups
    will be removed.

**backup_logs**

    If ``yes``, the log files are included into the backup, otherwise not.

Arguments
---------

.. note::

    All arguments will only affect the worlds selected with *--world* or
    *--all-world*

.. option:: --list

    Lists all available backups.

.. option:: --create

    Creates a new backup.

.. option:: --restore PATH

    Restores the world with the backup from the given BACKUP_PATH.

.. option:: --restore-latest

    Restores, if available, the latest backup of the world.

.. option:: --restore-menu

    Opens a menu, where the user can select which backup he wants to restore.

Cron
----

You should create a cronjob to create daily backups:

.. code-block:: none

    # m h dom mon dow user command
    # Creates a backup of all worlds everyday at 2:00h
    0 2 *   *   *   root minecraft -W backups --create


Backup archive structure
------------------------

A typical backup archive has this structure:

.. code-block:: none

    o
    |- world_conf.json        # The EMSM configuration of the world
    |- world                  # the minecraft world
        |- server.log
        |- server.properties
        |- ...

Changelog
---------

EMSM v3
^^^^^^^

    * changed package structure and dropped support for EMSM v2 backups.
"""


# Modules
# ------------------------------------------------

# std
import hashlib
import os
import time
import shutil
import datetime
import tempfile
import logging
import json

# third party
import termcolor

# local
import emsm
from emsm.core.base_plugin import BasePlugin


# Backward compatibility
# ------------------------------------------------

try:
    FileExistsError
except NameError:
    FileExistsError = OSError


# Data
# ------------------------------------------------

PLUGIN = "Backups"

AVLB_ARCHIVE_FORMATS = [name for name, desc in shutil.get_archive_formats()]

log = logging.getLogger(__file__)


# Functions
# ------------------------------------------------

def file_hash(path):
    """
    Returns the sha512 hash sum of the file at *path*.
    """
    with open(path, "rb") as file:
        data = file.read()
        sum_ = hashlib.sha512(data)
    return sum_.hexdigest()


# Classes
# ------------------------------------------------

class BackupManager(object):
    """
    Manages the backups of one world.
    """

    def __init__(self, app, world, max_storage_size, backup_dir, backup_logs):
        """
        """
        self._app = app
        self._world = world
        self._backup_dir = backup_dir
        self._max_storage_size = max_storage_size
        self._backup_logs = backup_logs

        os.makedirs(self._backup_dir, exist_ok=True)
        return None

    def app(self):
        """
        Returns that EMSM application that implicitly owns this object.
        """
        return self._app

    def world(self):
        """
        Returns the world whichs backups are managed.
        """
        return self._world

    def backup_dir(self):
        """
        Returns the backup directory.
        """
        return self._backup_dir

    def max_storage_size(self):
        """
        Returns the maximum number of backups that can be stored to the same
        time. If this value is *0*, then there is no limit.
        """
        return self._max_storage_size

    def backup_logs(self):
        """
        Returns the option to include the logs in the backup.
        """
        return self._backup_logs

    # We use the *filenames* to store the *timestamp* of a backup.

    def _filename_format(self):
        """
        Returns a string that can be formatted with *datetime.strftime()*.

        Example:
            >>> now = datetime.datetime.now()
            >>> fmt = bm.filename_format()
            >>> fmt
            %Y_%m_%d-%H_%M_%S-foobar
            >>> now.strftime(fmt)
            '2014_09_02-20_37_08-foobar'
        """
        filename_format = "%Y_%m_%d-%H_%M_%S-{}".format(self._world.name())
        return filename_format

    def _date_from_filename(self, path):
        """
        Extracts the timestamp from the filename and returns the corresponding
        ``datetime.datetime`` instance.

        See also:
            * filename_format()
        """
        # Extract the filename and remove any extensions.
        path = os.path.basename(path)
        filename = path[:path.find(".")]

        # Extract the datetime.
        try:
            return datetime.datetime.strptime(filename, self._filename_format())
        except ValueError as err:
            return None

    def _create_filename(self, date):
        """
        Creates the filename (without extensions) for the backup that has
        been created at the datetime *date*.
        """
        filename = date.strftime(self._filename_format())
        return filename

    def backup_list(self):
        """
        Returns a dictionary that maps the creation date of the backup to
        the backup path.
        """
        backups = dict()
        for filename in os.listdir(self._backup_dir):
            path = os.path.join(self._backup_dir, filename)

            if not os.path.isfile(path):
                continue
            if path.endswith(".tmp"):
                continue

            date = self._date_from_filename(filename)
            if date is None:
                continue

            backups[date] = path
        return backups

    def latest_backup(self):
        """
        Returns a two tuple, that contains the date and the path of the latest
        available backup. If no backup is available, ``(None, None)`` is
        returned.

        See also:
            * backup_list()
        """
        backups = self.backup_list()
        if backups:
            date = max(backups.keys())
            path = backups[date]
            return (date, path)
        else:
            return (None, None)

    def clean_backup_dir(self):
        """
        Removes old backups that are no longer needed.

        See also:
            * max_storage_size()
        """
        # Remove some old backups if we store currently too many backups.
        if self._max_storage_size > 0:
            backups = list(self.backup_list().items())
            backups.sort(reverse=True)

            while len(backups) > self._max_storage_size:
                date, path = backups.pop()
                os.remove(path)

        # Remove .tmp files.
        # These are backups which could not be craeated successfully.
        for filename in os.listdir(self._backup_dir):
            path = os.path.join(self._backup_dir, filename)

            if path.endswith(".tmp"):
                try:
                    os.remove(path)
                except OSError:
                    pass
        return None

    def _save_world(self, backup_dir):
        """
        Copies the world directory (world data) into the backup directory:

            EMSM_ROOT/worlds/foo -> backup_dir/world
        """
        try:
            # We need to disable the auto-save for the backup. I'm paranoid,
            # so I'disable auto-save in this try-catch construct.
            if self._world.is_online():
                self._world.send_command("save-off")
                try:
                    # We use verbose send, to wait until the world has been
                    # saved.
                    self._world.send_command_get_output("save-all", timeout=30)
                except emsm.core.worlds.WorldCommandTimeout as err:
                    pass

            # Copy the world data to *backup_dir*.
            if self._backup_logs:
                shutil.copytree(
                    self._world.directory(),
                    os.path.join(backup_dir, "world")
                )
            else:
                shutil.copytree(
                    self._world.directory(),
                    os.path.join(backup_dir, "world"),
                    ignore=shutil.ignore_patterns("logs")
                )
        finally:
            if self._world.is_online():
                self._world.send_command("save-on")
                self._world.send_command("save-all")
        return None

    def _restore_world(self, backup_dir):
        """
        Copies the world directory from the backup in *backup_dir* into the
        EMSM world folder.

        Exceptions:
            * WorldIsOnlineError

        See also:
            * _save_world()
        """
        # Break if the world is currently online.
        if self._world.is_online():
            raise emsm.core.worlds.WorldIsOnlineError()

        # Delete the world directory (``EMSM/world/...``)
        for i in range(100):
            # XXX: Fixes an error with server.log.lck
            # and shutil.rmtree(...) when the server was online.
            try:
                shutil.rmtree(self._world.directory())
            except OSError:
                time.sleep(0.05)
            else:
                break

        # Copy the world backup to the EMSM world directory.
        shutil.copytree(
            src = os.path.join(backup_dir, "world"),
            dst = self._world.directory()
            )
        return None

    def _save_world_conf(self, backup_dir):
        """
        Saves the configuration of the world in *backup_dir/conf/world.json*.
        """
        world_conf_backup_path = os.path.join(backup_dir, "world_conf.json")
        with open(world_conf_backup_path, "w") as file:
            conf = dict(self._world.conf())
            json.dump([self._world.name(), conf], file)
        return None

    def _restore_world_conf(self, backup_dir):
        """
        If the backup at *backup_dir* includes the world configuration, it
        will be restored. If not, nothing happens.
        """
        world_conf_backup_path = os.path.join(backup_dir, "world_conf.json")

        # Load the configuration backup.
        with open(world_conf_backup_path) as file:
            _, backup_conf = json.load(file)

        # Restore the configuration.
        #
        # Todo:
        #   * restore the *port* option?
        conf = self._world.conf()
        conf.clear()
        conf.update(backup_conf)
        return None

    def create(self, archive_format):
        """
        Creates a backup of the world and returns the name of the created
        backup archive.

        Parameters:
            * archive_format
                A string in shutil.get_archive_formats() that defines the
                compression type.

        Exceptions:
            * ...
        """
        with tempfile.TemporaryDirectory() as tmp_data_dir:

            # Copy all stuff that should be included into the backup in the
            # temporary directory.
            self._save_world(tmp_data_dir)
            self._save_world_conf(tmp_data_dir)

            # Put all in an archive.
            backup_filename = self._create_filename(datetime.datetime.now())
            with tempfile.TemporaryDirectory() as tmp_archive_dir:

                # *make_archive* returns the **complete** path to the crated
                # archive.
                backup_path = shutil.make_archive(
                    base_name = os.path.join(tmp_archive_dir, backup_filename),
                    format = archive_format,
                    root_dir = tmp_data_dir,
                    base_dir = "./"
                    )

                # Move the backup to our folder in *plugins_data_dir*:
                #   EMSM_ROOT/plugins_data/backups/foo/
                #
                # We move the backup to a temporary filename, so that
                # when something goes wrong, no corrupted backup will be
                # stored.
                # When the *move* was successful, we rename the file.
                dst = os.path.join(
                    self._backup_dir, os.path.basename(backup_path)
                    )
                shutil.move(src=backup_path, dst=dst + ".tmp")
                os.rename(dst + ".tmp", dst)

        self.clean_backup_dir()
        return None

    def restore(self, backup_file, message=str(), delay=0):
        """
        Restores the backup of the world from the given *backup_file*. If
        the backup archive contains the server executable it will be restored
        too if necessairy.

        Exceptions:
            * WorldStartFailed
            * WorldStopFailed
            * ... shutil.unpack_archive() exceptions ...
        """
        # Extract the backup in a temporary directory and copy then all things
        # into the EMSM directories.
        with tempfile.TemporaryDirectory() as temp_dir:
            shutil.unpack_archive(
                filename = backup_file,
                extract_dir = temp_dir
                )

            # Stop the world.
            was_online = self._world.is_online()
            if was_online:
                self._world.send_command("say {}".format(message))
                time.sleep(delay)
                self._world.kill_processes()

            # Restore the world.
            self._restore_world(temp_dir)
            self._restore_world_conf(temp_dir)

        # Restart the world if it was online before restoring.
        if was_online:
            self._world.start()
        return None


class UiBackupManager(BackupManager):

    def list(self):
        """
        Prints a list with all existing backups.
        """
        backups = list(self.backup_list().items())
        backups.sort(reverse=True)

        print(termcolor.colored("{}:".format(self.world().name()), "cyan"))
        if not backups:
            print("\t", "- no backups found -")
        else:
            for date, path in backups:
                print("\t", "*", date.ctime())
        return None

    def create(self, archive_format):
        """
        Creates a new backup.
        """
        print(termcolor.colored("{}:".format(self.world().name()), "cyan"))

        try:
            super().create(archive_format)
        except Exception as err:
            # The EMSM will print the exception, so we do nothing here.
            # We only catch Exception to show, that a lot of things
            # can go wrong when creating a backup.
            raise
        else:
            print("\t", "done.")
        return None

    def _restore(self, *, backup_path, message, delay, verify_restore=True):
        """
        The main purpose of this method is simply to wrap the restore
        progress and print it in a user friendly way to the console.

        The *message* and *delay* parameter are passed to the super class
        *restore()* method.

        If *verify_restore* is True, the user is asked if he really wants to
        restore (and so overwrite) the world.
        """
        if verify_restore:
            prompt = "\t Do you really want to restore and " +\
                     termcolor.colored("overwrite", "red") +\
                     " the world '{}'?"
            prompt = prompt.format(self.world().name())
            if not emsm.core.lib.userinput.ask(prompt):
                return None

        # Restore the world.
        try:
            super().restore(backup_path, message, delay)
        except emsm.core.worlds.WorldStopFailed:
            print("\t", termcolor.colored("error:", "red"),
                  "the world could not be stopped.")
        except emsm.core.worlds.WorldStartFailed:
            print("\t", termcolor.colored("error:", "red"),
                  "the world could not be restarted.")
        except Exception as err:
            # This is an unexpected exception that may be an IOError or
            # OSError. Let the EMSM log it and print a warning.
            # We can't handle them properly, since we can not react on
            # them.
            raise
        else:
            print("\t", "done.")
        return None

    def restore(self, backup_path, message, delay, backup_date=None):
        """
        This method corresponds to the command line argument:

            --restore PATH
        """
        print(termcolor.colored("{}:".format(self.world().name()), "cyan"))

        # Print some information about the backup archive.
        print("\t", "backup path: {}".format(backup_path))

        # Restore the backup.
        self._restore(
            backup_path=backup_path, message=message, delay=delay,
            verify_restore=True
            )
        return None

    def restore_latest(self, message, delay):
        """
        This method corresponds to the command line argument:

            --restore-latest
        """
        print(termcolor.colored("{}:".format(self.world().name()), "cyan"))

        # Break if no backup is available.
        latest_backup = self.latest_backup()
        if latest_backup == (None, None):
            print("\t", termcolor.colored("error:", "red"), "no backup available.")
        else:
            date, path = latest_backup
            print("\t", "backup date:", date.ctime())

            # Restore the backup.
            self._restore(
                backup_path=path, message=message, delay=delay,
                verify_restore=True
                )
        return None

    def restore_menu(self, message, delay):
        """
        This method corresponds to the command line argument:

            --restore-menu
        """
        print(termcolor.colored("{}:".format(self.world().name()), "cyan"))

        # Get all existing backups.
        backups = list(self.backup_list().items())
        backups.sort(reverse=True)

        # Break if no backup is available.
        if not backups:
            print("\t", termcolor.colored("error:", "red"),
                  "no backup available.")
        else:
            # Print the backup list.
            for i, backup in enumerate(backups):
                date, path = backup
                print("\t", "{})".format(i), date.ctime())

            # Let the user select a backup.
            i = emsm.core.lib.userinput.get_value(
                prompt = "\t Which backup do you want to restore?",
                conv_func = lambda s: int(s.strip()),
                check_func = lambda s: 0 <= s < len(backups)
                )
            backup = backups[i]

            # Restore the backup.
            self._restore(
                backup_path=backup[1], message=message, delay=delay,
                verify_restore=True
                )
        return None


class Backups(BasePlugin):

    VERSION = "4.0.0-beta"

    DESCRIPTION = __doc__

    def __init__(self, app, name):
        """
        """
        BasePlugin.__init__(self, app, name)

        self._setup_conf()
        self._setup_argparser()
        return None

    def _setup_conf(self):
        """
        Sets the configuration up.
        """
        conf = self.conf()

        # Read
        # ^^^^

        # archive_format
        self._archive_format = conf.get("archive_format")
        if not self._archive_format in AVLB_ARCHIVE_FORMATS:
            self._archive_format = AVLB_ARCHIVE_FORMATS[0]

        # restore_message
        self._restore_message = conf.get(
            "restore_message",
            "This world is about to be resetted to an earlier state."
            )

        # restore_delay
        self._restore_delay = conf.getint("restore_delay", 5)
        if self._restore_delay < 0:
            self._restore_delay = 0

        # max_storage_size
        self._max_storage_size = conf.getint("max_storage_size", 30)
        if self._max_storage_size < 0:
            self._max_storage_size = 0

        # backup_logs
        self._backup_logs = conf.getboolean("backup_logs", True)

        # Write
        # ^^^^^

        conf.clear()
        conf["archive_format"] = str(self._archive_format)
        conf["restore_message"] = str(self._restore_message)
        conf["restore_delay"] = str(self._restore_delay)
        conf["max_storage_size"] = str(self._max_storage_size)
        conf["backup_logs"] = "yes" if self._backup_logs else "no"
        return None

    def _setup_argparser(self):
        """
        Sets the argument parser up.
        """
        parser = self.argparser()

        parser.description = "A manager for the backups of the worlds"

        # We want to allow only one action per run, so we put everything
        # in a mutually exclusive group.
        me_group = parser.add_mutually_exclusive_group()
        me_group.add_argument(
            "--list",
            action = "count",
            dest = "backups_list",
            help = "Lists all available backups."
            )
        me_group.add_argument(
            "--create",
            action = "count",
            dest = "backups_create",
            help = "Creates a new backup."
            )
        me_group.add_argument(
            "--restore",
            action = "store",
            dest = "backups_restore",
            metavar = "PATH",
            help = "Restores the backup at the given path."
            )
        me_group.add_argument(
            "--restore-latest",
            action = "count",
            dest = "backups_restore_latest",
            help = "Restores the latest backup."
            )
        me_group.add_argument(
            "--restore-menu",
            action = "count",
            dest = "backups_restore_menu",
            help = "Opens a dialog allowing the user to select the backup "\
                   "that should be restored."
            )
        return None

    def run(self, args):
        """
        """
        # We process the worlds in alphabetical order, so we need to sort
        # them first.
        worlds = self.app().worlds().get_selected()
        worlds.sort(key = lambda w: w.name())

        for world in worlds:
            bm = UiBackupManager(
                app = self.app(),
                world = world,
                max_storage_size = self._max_storage_size,
                backup_dir = os.path.join(self.data_dir(), world.name()),
                backup_logs = self._backup_logs
                )

            if args.backups_list:
                bm.list()
            elif args.backups_create:
                bm.create(self._archive_format)
            elif args.backups_restore:
                bm.restore(args.backups_restore, self._restore_message,
                           self._restore_delay
                           )
            elif args.backups_restore_latest:
                bm.restore_latest(self._restore_message, self._restore_delay)
            elif args.backups_restore_menu:
                bm.restore_menu(self._restore_message, self._restore_delay)
        return None
