# -*- coding: utf-8 -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2015 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU Affero General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option)
#  any later version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for
#  more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Console Commands
"""

from __future__ import absolute_import
from __future__ import unicode_literals

import sys
import platform
import argparse
import datetime
import socket
import logging
from getpass import getpass

import edbob

from ._version import __version__
from .util import load_entry_points
from rattail.db import Session
from rattail.db.continuum  import configure_versioning, disable_versioning
from rattail.db.util import configure_session_factory
from .console import Progress


log = logging.getLogger(__name__)


class ArgumentParser(argparse.ArgumentParser):
    """
    Custom argument parser.

    This overrides some of the parsing logic which is specific to the primary
    command object.
    """

    def parse_args(self, args=None, namespace=None):
        args, argv = self.parse_known_args(args, namespace)
        args.argv = argv
        return args


def date_argument(string):
    """
    Validate and coerce a date argument.

    This function is designed be used as the ``type`` parameter when calling
    ``ArgumentParser.add_argument()``, e.g.::

       parser = ArgumentParser()
       parser.add_argument('--date', type=date_argument)
    """
    try:
        date = datetime.datetime.strptime(string, '%Y-%m-%d').date()
    except ValueError:
        raise argparse.ArgumentTypeError("Date must be in YYYY-MM-DD format")
    return date


class Command(object):
    """
    The primary command for the application.

    This effectively *is* the ``rattail`` console application.  It mostly
    provides the structure for subcommands, which really do all the work.

    This command is designed to be subclassed, should your application need
    similar functionality.
    """
    name = 'rattail'
    version = __version__
    description = "Retail Software Framework"
    long_description = """
Rattail is a retail software framework.

Copyright (c) 2010-2012 Lance Edgar <lance@edbob.org>

This program comes with ABSOLUTELY NO WARRANTY.  This is free software,
and you are welcome to redistribute it under certain conditions.
See the file COPYING.txt for more information.
"""

    stdout = sys.stdout
    stderr = sys.stderr

    def __init__(self):
        self.subcommands = load_entry_points('{0}.commands'.format(self.name))

    def __unicode__(self):
        return unicode(self.name)

    def iter_subcommands(self):
        """
        Iterate over the subcommands.

        This is a generator which yields each associated :class:`Subcommand`
        class sorted by :attr:`Subcommand.name`.
        """
        for name in sorted(self.subcommands):
            yield self.subcommands[name]

    def print_help(self):
        """
        Print help text for the primary command.

        The output will include a list of available subcommands.
        """
        self.stdout.write("""{0}

Usage: {1} [options] <command> [command-options]

Options:
  -c PATH, --config=PATH
                    Config path (may be specified more than once)
  -n, --no-init     Don't load config before executing command
  -d, --debug       Increase logging level to DEBUG
  -P, --progress    Show progress indicators (where relevant)
  -v, --verbose     Increase logging level to INFO
  -V, --version     Display program version and exit

Commands:\n""".format(self.description, self.name))

        for cmd in self.iter_subcommands():
            self.stdout.write("  {0:<16s}  {1}\n".format(cmd.name, cmd.description))

        self.stdout.write("\nTry '{0} help <command>' for more help.\n".format(self.name))

    def run(self, *args):
        """
        Parse command line arguments and execute appropriate subcommand.
        """
        parser = ArgumentParser(
            prog=self.name,
            description=self.description,
            add_help=False,
            )

        parser.add_argument('-c', '--config', action='append', dest='config_paths',
                            metavar='PATH')
        parser.add_argument('-d', '--debug', action='store_true', dest='debug')
        parser.add_argument('-n', '--no-init', action='store_true', default=False)
        parser.add_argument('-P', '--progress', action='store_true', default=False)
        parser.add_argument('--stdout', metavar='PATH', type=argparse.FileType('w'),
                            help="Optional path to which STDOUT should be effectively redirected.")
        parser.add_argument('--stderr', metavar='PATH', type=argparse.FileType('w'),
                            help="Optional path to which STDERR should be effectively redirected.")
        parser.add_argument('-v', '--verbose', action='store_true', dest='verbose')
        parser.add_argument('-V', '--version', action='version',
                            version="%(prog)s {0}".format(self.version))
        parser.add_argument('command', nargs='*')

        # Parse args and determine subcommand.
        args = parser.parse_args(list(args))
        if not args or not args.command:
            self.print_help()
            return

        # Show (sub)command help if so instructed, or unknown subcommand.
        cmd = args.command.pop(0)
        if cmd == 'help':
            if len(args.command) != 1:
                self.print_help()
                return
            cmd = args.command[0]
            if cmd not in self.subcommands:
                self.print_help()
                return
            cmd = self.subcommands[cmd](parent=self)
            cmd.parser.print_help()
            return
        elif cmd not in self.subcommands:
            self.print_help()
            return

        # Okay, we should be done needing to print help messages.  Now it's
        # safe to redirect STDOUT/STDERR, if necessary.
        if args.stdout:
            self.stdout = args.stdout
        if args.stderr:
            self.stderr = args.stderr

        # Basic logging should be established before init()ing.

        # Use root logger if setting logging flags.
        log = logging.getLogger()

        # TODO: Figure out the basic logging pattern we're after here.
        # edbob.basic_logging()
        logging.basicConfig()

        if args.verbose:
            log.setLevel(logging.INFO)
        if args.debug:
            log.setLevel(logging.DEBUG)

        # Initialize everything...
        config = None
        if not args.no_init:
            edbob.init(self.name, *(args.config_paths or []))
            config = edbob.config

            # Command line logging flags should override config.
            if args.verbose:
                log.setLevel(logging.INFO)
            if args.debug:
                log.setLevel(logging.DEBUG)

            # Configure the default database engine.
            configure_session_factory(config)

            # Configure Continuum versioning.
            configure_versioning(config)

        # And finally, do something of real value...
        cmd = self.subcommands[cmd](self)
        cmd.config = config
        cmd.show_progress = args.progress
        cmd.progress = Progress if args.progress else None
        cmd._run(*(args.command + args.argv))


class Subcommand(object):
    """
    Base class for application subcommands.
    """
    name = 'UNDEFINED'
    description = 'UNDEFINED'

    def __init__(self, parent=None, show_progress=None):
        self.parent = parent
        self.stdout = getattr(parent, 'stdout', sys.stdout)
        self.stderr = getattr(parent, 'stderr', sys.stderr)
        self.show_progress = show_progress
        self.progress = Progress if show_progress else None
        self.parser = argparse.ArgumentParser(
            prog='{0} {1}'.format(getattr(self.parent, 'name', 'UNDEFINED'), self.name),
            description=self.description)
        self.add_parser_args(self.parser)

    def __repr__(self):
        return "Subcommand(name={0})".format(repr(self.name))

    def add_parser_args(self, parser):
        """
        Configure additional arguments for the subcommand argument parser.
        """
        pass
            
    def _run(self, *args):
        args = self.parser.parse_args(list(args))
        return self.run(args)

    def run(self, args):
        """
        Run the subcommand logic.
        """
        raise NotImplementedError


class AddUser(Subcommand):
    """
    Adds a user to the database.
    """

    name = 'adduser'
    description = "Add a user to the database."

    def add_parser_args(self, parser):
        parser.add_argument('username',
                            help="Username for the new account.")
        parser.add_argument('-A', '--administrator',
                            action='store_true',
                            help="Add the new user to the Administrator role.")

    def run(self, args):
        from rattail.db import model
        from rattail.db.auth import set_user_password, administrator_role

        session = Session()

        if session.query(model.User).filter_by(username=args.username).count():
            session.close()
            self.stderr.write("User '{0}' already exists.\n".format(args.username))
            return

        passwd = ''
        while not passwd:
            try:
                passwd = getpass("Enter a password for user '{0}': ".format(args.username))
            except KeyboardInterrupt:
                self.stderr.write("\nOperation was canceled.\n")
                return

        user = model.User(username=args.username)
        set_user_password(user, passwd)
        if args.administrator:
            user.roles.append(administrator_role(session))
        session.add(user)
        session.commit()
        session.close()
        self.stdout.write("Created user: {0}\n".format(args.username))


class DatabaseSyncCommand(Subcommand):
    """
    Controls the database synchronization service.
    """

    name = 'dbsync'
    description = "Manage the database synchronization service"

    def add_parser_args(self, parser):
        subparsers = parser.add_subparsers(title='subcommands')

        start = subparsers.add_parser('start', help="Start service")
        start.set_defaults(subcommand='start')
        stop = subparsers.add_parser('stop', help="Stop service")
        stop.set_defaults(subcommand='stop')

        if sys.platform == 'linux2':
            parser.add_argument('-p', '--pidfile',
                                help="Path to PID file", metavar='PATH')
            parser.add_argument('-D', '--do-not-daemonize',
                                action='store_false', dest='daemonize', default=True,
                                help="Do not daemonize when starting.")

    def run(self, args):
        from rattail.db.sync import linux as dbsync

        if args.subcommand == 'start':
            try:
                dbsync.start_daemon(self.config, args.pidfile, args.daemonize)
            except KeyboardInterrupt:
                if not args.daemonize:
                    self.stderr.write("Interrupted.\n")
                else:
                    raise

        elif args.subcommand == 'stop':
            dbsync.stop_daemon(self.config, args.pidfile)


class Dump(Subcommand):
    """
    Do a simple data dump.
    """

    name = 'dump'
    description = "Dump data to file."

    def add_parser_args(self, parser):
        parser.add_argument(
            '--output', '-o', metavar='FILE',
            help="Optional path to output file.  If none is specified, "
            "data will be written to standard output.")
        parser.add_argument(
            'model', help="Model whose data will be dumped.")

    def get_model(self):
        """
        Returns the module which contains all relevant data models.

        By default this returns ``rattail.db.model``, but this method may be
        overridden in derived commands to add support for extra data models.
        """
        from rattail.db import model
        return model

    def run(self, args):
        from .db.dump import dump_data

        model = self.get_model()
        if hasattr(model, args.model):
            cls = getattr(model, args.model)
        else:
            self.stderr.write("Unknown model: {0}\n".format(args.model))
            sys.exit(1)

        progress = None
        if self.show_progress: # pragma no cover
            progress = Progress

        if args.output:
            output = open(args.output, 'wb')
        else:
            output = self.stdout

        session = Session()
        dump_data(session, cls, output, progress=progress)
        session.close()

        if output is not self.stdout:
            output.close()


class FileMonitorCommand(Subcommand):
    """
    Interacts with the file monitor service; called as ``rattail filemon``.
    This command expects a subcommand; one of the following:

    * ``rattail filemon start``
    * ``rattail filemon stop``

    On Windows platforms, the following additional subcommands are available:

    * ``rattail filemon install``
    * ``rattail filemon uninstall`` (or ``rattail filemon remove``)

    .. note::
       The Windows Vista family of operating systems requires you to launch
       ``cmd.exe`` as an Administrator in order to have sufficient rights to
       run the above commands.

    .. See :doc:`howto.use_filemon` for more information.
    """

    name = 'filemon'
    description = "Manage the file monitor service"

    def add_parser_args(self, parser):
        subparsers = parser.add_subparsers(title='subcommands')

        start = subparsers.add_parser('start', help="Start service")
        start.set_defaults(subcommand='start')
        stop = subparsers.add_parser('stop', help="Stop service")
        stop.set_defaults(subcommand='stop')

        if sys.platform == 'linux2':
            parser.add_argument('-p', '--pidfile',
                                help="Path to PID file.", metavar='PATH')
            parser.add_argument('-D', '--do-not-daemonize',
                                action='store_false', dest='daemonize', default=True,
                                help="Do not daemonize when starting.")

        elif sys.platform == 'win32': # pragma no cover

            install = subparsers.add_parser('install', help="Install service")
            install.set_defaults(subcommand='install')
            install.add_argument('-a', '--auto-start', action='store_true',
                                 help="Configure service to start automatically.")
            install.add_argument('-U', '--username',
                                 help="User account under which the service should run.")

            remove = subparsers.add_parser('remove', help="Uninstall (remove) service")
            remove.set_defaults(subcommand='remove')

            uninstall = subparsers.add_parser('uninstall', help="Uninstall (remove) service")
            uninstall.set_defaults(subcommand='remove')

    def run(self, args):
        if sys.platform == 'linux2':
            from rattail.filemon import linux as filemon

            if args.subcommand == 'start':
                filemon.start_daemon(self.config, args.pidfile, args.daemonize)

            elif args.subcommand == 'stop':
                filemon.stop_daemon(self.config, args.pidfile)

        elif sys.platform == 'win32': # pragma no cover
            self.run_win32(args)

        else:
            self.stderr.write("File monitor is not supported on platform: {0}\n".format(sys.platform))
            sys.exit(1)

    def run_win32(self, args): # pragma no cover
        from rattail.win32 import require_elevation
        from rattail.win32 import service
        from rattail.win32 import users
        from rattail.filemon import win32 as filemon

        require_elevation()

        options = []
        if args.subcommand == 'install':

            username = args.username
            if username:
                if '\\' in username:
                    server, username = username.split('\\')
                else:
                    server = socket.gethostname()
                if not users.user_exists(username, server):
                    sys.stderr.write("User does not exist: {0}\\{1}\n".format(server, username))
                    sys.exit(1)

                password = ''
                while password == '':
                    password = getpass("Password for service user: ").strip()
                options.extend(['--username', r'{0}\{1}'.format(server, username)])
                options.extend(['--password', password])

            if args.auto_start:
                options.extend(['--startup', 'auto'])

        service.execute_service_command(filemon, args.subcommand, *options)

        # If installing with custom user, grant "logon as service" right.
        if args.subcommand == 'install' and args.username:
            users.allow_logon_as_service(username)

        # TODO: Figure out if the following is even required, or if instead we
        # should just be passing '--startup delayed' to begin with?

        # If installing auto-start service on Windows 7, we should update
        # its startup type to be "Automatic (Delayed Start)".
        # TODO: Improve this check to include Vista?
        if args.subcommand == 'install' and args.auto_start:
            if platform.release() == '7':
                name = filemon.RattailFileMonitor._svc_name_
                service.delayed_auto_start_service(name)


class ImportSubcommand(Subcommand):
    """
    Base class for subcommands which use the data importing system.
    """

    def add_parser_args(self, parser):
        parser.add_argument('--no-versioning', action='store_true',
                            help="Disables versioning during the import.  This is "
                            "intended to be useful e.g. during initial import, where "
                            "the process can be quite slow even without the overhead "
                            "of versioning.")
        parser.add_argument('--dry-run', action='store_true',
                            help="Go through the motions and allow logging to occur, "
                            "but do not actually commit the transaction at the end.")
        parser.add_argument('models', nargs='*', metavar='MODEL',
                            help="One or more models to import.  If not specified, "
                            "then all supported models will be imported.")

    def run(self, args):
        log.info("begin {0} for data model(s): {1}".format(
                self.name, ', '.join(args.models or ["ALL"])))

        if args.no_versioning:
            disable_versioning()

        session = Session(continuum_user=self.continuum_user)
        self.import_data(args, session)

        if args.dry_run:
            session.rollback()
            log.info("dry run, so transaction was rolled back")
        else:
            session.commit()
            log.info("transaction was committed")
        session.close()

    @property
    def continuum_user(self):
        """
        Info needed to assign the Continuum user for the database session.
        """

    def import_data(self, args, session):
        """
        Custom logic for importing data, to be implemented by subclass.
        """


class ImportCSV(ImportSubcommand):
    """
    Import data from a CSV file.
    """
    name = 'import-csv'
    description = "Import data from a CSV file."

    def add_parser_args(self, parser):
        super(ImportCSV, self).add_parser_args(parser)
        parser.add_argument('importer',
                            help="Spec string for importer class which should handle the import.")
        parser.add_argument('csv_path',
                            help="Path to the data file which will be imported.")

    def import_data(self, args, session):
        from rattail.db.importing.providers.csv import make_provider

        provider = make_provider(self.config, session, args.importer, data_path=args.csv_path)
        data = provider.get_data(progress=self.progress)
        affected = provider.importer.import_data(data, provider.supported_fields, 'uuid',
                                                 progress=self.progress)
        log.info("added or updated {0} {1} records".format(affected, provider.model_name))


class InitializeDatabase(Subcommand):
    """
    Creates the initial Rattail tables within a database.
    """

    name = 'initdb'
    description = "Create initial tables in a database."

    def add_parser_args(self, parser):
        parser.add_argument('url', metavar='URL',
                            help="Database engine URL")

    def run(self, args):
        from sqlalchemy import create_engine
        from alembic.util import obfuscate_url_pw
        from rattail.db import model
        
        engine = create_engine(args.url)
        model.Base.metadata.create_all(engine)
        print("Created initial tables for database:")
        print("  {0}".format(obfuscate_url_pw(engine.url)))


class LoadHostDataCommand(Subcommand):
    """
    Loads data from the Rattail host database, if one is configured.
    """

    name = 'load-host-data'
    description = "Load data from host database"

    def run(self, args):
        from .db import get_engines
        from .db import load

        engines = get_engines(self.config)
        if 'host' not in engines:
            sys.stderr.write("Host engine URL not configured.\n")
            sys.exit(1)

        proc = load.LoadProcessor(self.config)
        proc.load_all_data(engines['host'], Progress)


class MakeConfigCommand(Subcommand):
    """
    Creates a sample configuration file.
    """

    name = 'make-config'
    description = "Create a configuration file"

    def add_parser_args(self, parser):
        parser.add_argument('path', default='rattail.conf', metavar='PATH',
                            help="Path to the new file")
        parser.add_argument('-f', '--force', action='store_true',
                            help="Overwrite an existing file")


    def run(self, args):
        import os
        import os.path
        import shutil
        from rattail.files import resource_path

        dest = os.path.abspath(args.path)
        if os.path.exists(dest):
            if os.path.isdir(dest):
                sys.stderr.write("Path must include the filename; "
                                 "you gave a directory:\n  {0}\n".format(dest))
                sys.exit(1)
            if not args.force:
                sys.stderr.write("File already exists "
                                 "(use --force to overwrite):\n  "
                                 "{0}\n".format(dest))
                sys.exit(1)
            os.remove(dest)

        src = resource_path('rattail:data/rattail.conf.sample')
        shutil.copyfile(src, dest)


class MakeUserCommand(Subcommand):
    """
    Creates a system user for Rattail.
    """
    name = 'make-user'
    description = "Create a system user account for Rattail"

    def add_parser_args(self, parser):
        parser.add_argument('-U', '--username', metavar='USERNAME', default='rattail',
                            help="Username for the new user; defaults to 'rattail'.")
        parser.add_argument('--full-name', metavar='FULL_NAME',
                            help="Full (display) name for the new user.")
        parser.add_argument('--comment', metavar='COMMENT',
                            help="Comment string for the new user.")

    def run(self, args):
        if sys.platform != 'win32':
            sys.stderr.write("Sorry, only win32 platform is supported.\n")
            sys.exit(1)

        from rattail.win32 import users
        from rattail.win32 import require_elevation

        require_elevation()

        if users.user_exists(args.username):
            sys.stderr.write("User already exists: {0}\n".format(args.username))
            sys.exit(1)

        try:
            password = None
            while not password:
                password = getpass(b"Enter a password: ").strip()
        except KeyboardInterrupt:
            sys.stderr.write("Operation canceled by user.")
            sys.exit(2)

        users.create_user(args.username, password,
                          full_name=args.full_name, comment=args.comment)
        sys.stdout.write("Created user: {0}\n".format(args.username))


class PalmCommand(Subcommand):
    """
    Manages registration for the HotSync Manager conduit; called as::

       rattail palm
    """

    name = 'palm'
    description = "Manage the HotSync Manager conduit registration"

    def add_parser_args(self, parser):
        subparsers = parser.add_subparsers(title='subcommands')

        register = subparsers.add_parser('register', help="Register Rattail conduit")
        register.set_defaults(subcommand='register')

        unregister = subparsers.add_parser('unregister', help="Unregister Rattail conduit")
        unregister.set_defaults(subcommand='unregister')

    def run(self, args):
        from rattail import palm
        from rattail.win32 import require_elevation
        from rattail.exceptions import PalmError

        require_elevation()

        if args.subcommand == 'register':
            try:
                palm.register_conduit()
            except PalmError, error:
                sys.stderr.write(str(error) + '\n')

        elif args.subcommand == 'unregister':
            try:
                palm.unregister_conduit()
            except PalmError, error:
                sys.stderr.write(str(error) + '\n')
                

class PurgeBatchesCommand(Subcommand):
    """
    Purges stale batches from the database; called as:

    .. code-block:: sh

       rattail purge-batches
    """
    name = 'purge-batches'
    description = "Purge stale batches from the database"

    def add_parser_args(self, parser):
        parser.add_argument('-A', '--all', action='store_true',
                            help="Purge ALL batches regardless of purge date")
        parser.add_argument('--date', '-D', type=date_argument,
                            help="Optional effective date for the purge.  If "
                            "none is specified, the current date is assumed.")

    def run(self, args):
        from rattail.db.util import obfuscate_url_pw
        from rattail.db.batches import util

        self.stdout.write("Purging batches from database:\n")
        self.stdout.write("    {0}\n".format(obfuscate_url_pw(Session.kw['bind'].url)))

        normal = util.purge_batches(effective_date=args.date, purge_everything=args.all)
        orphaned = util.purge_orphaned_batches()

        self.stdout.write("\nPurged {0} normal and {1} orphaned batches.\n".format(normal, orphaned))


def main(*args):
    """
    The primary entry point for the Rattail command system.
    """

    if args:
        args = list(args)
    else:
        args = sys.argv[1:]

    cmd = Command()
    cmd.run(*args)
