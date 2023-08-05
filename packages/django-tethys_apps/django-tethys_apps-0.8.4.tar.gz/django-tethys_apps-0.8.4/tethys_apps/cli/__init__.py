# Commandline interface for Tethys
import argparse
import subprocess
import os
import random
import string

from django.template import Template, Context
from django.conf import settings

from tethys_apps.terminal_colors import TerminalColors
from .docker_commands import *

# Module level variables
GEN_SETTINGS_OPTION = 'settings'
GEN_APACHE_OPTION = 'apache'
VALID_GEN_OBJECTS = (GEN_SETTINGS_OPTION, GEN_APACHE_OPTION)
DEFAULT_INSTALLATION_DIRECTORY = '/usr/lib/tethys/src'
DEVELOPMENT_DIRECTORY = '/usr/lib/tethys/tethys'

# Setup Django settings
settings.configure()


def get_manage_path(args):
    """
    Validate user defined manage path, use default, or throw error
    """
    # Determine path to manage.py file
    manage_path = os.path.join(DEFAULT_INSTALLATION_DIRECTORY, 'manage.py')

    # Check for path option
    if args.manage:
        manage_path = args.manage

        # Throw error if path is not valid
        if not os.path.isfile(manage_path):
            print('Error: Can\'t open file "{0}", no such file.'.format(manage_path))
            exit(1)

    elif not os.path.isfile(manage_path):
        # Try the development path version
        manage_path = os.path.join(DEVELOPMENT_DIRECTORY, 'manage.py')

        # Throw error if default path is not valid
        if not os.path.isfile(manage_path):
            print('Error: Cannot find the "manage.py" file at the default location. Try using the "--manage"'
                  'option to provide the path to the location of the "manage.py" file.')
            exit(1)

    return manage_path


def scaffold_command(args):
    """
    Create a new Tethys app projects in the current directory.
    """
    PREFIX = 'tethysapp'
    project_name = args.name

    if PREFIX not in project_name:
        project_name = '{0}-{1}'.format(PREFIX, project_name)

    process = ['paster', 'create', '-t', 'tethys_app_scaffold', project_name]
    subprocess.call(process)


def generate_command(args):
    """
    Generate a settings file for a new installation.
    """
    # Setup variables
    template = None
    context = Context()

    # Determine template path
    gen_templates_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'gen_templates')
    template_path = os.path.join(gen_templates_dir, args.type)

    # Determine destination file name (defaults to type)
    destination_file = args.type

    # Settings file setup
    if args.type == GEN_SETTINGS_OPTION:
        # Desitnation filename
        destination_file = '{0}.py'.format(args.type)

        # Parse template
        template = Template(open(template_path).read())

        # Generate context variables
        secret_key = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(50)])
        context.update({'secret_key': secret_key})
        print('Generating new settings.py file...')

    if args.type == GEN_APACHE_OPTION:
        # Destination filename
        destination_file = 'tethys-default.conf'

        # Parse template
        template = Template(open(template_path).read())

    # Default destination path is the current working directory
    destination_dir = os.getcwd()

    if args.directory:
        if os.path.isdir(args.directory):
            destination_dir = args.directory
        else:
            print('Error: "{0}" is not a valid directory.')
            exit(1)

    destination_path = os.path.join(destination_dir, destination_file)

    # Check for pre-existing file
    if os.path.isfile(destination_path):
        valid_inputs = ('y', 'n', 'yes', 'no')
        no_inputs = ('n', 'no')

        overwrite_input = raw_input('Warning: "{0}" already exists. '
                                    'Overwrite? (y/n): '.format(destination_file)).lower()

        while overwrite_input not in valid_inputs:
            overwrite_input = raw_input('Invalid option. Overwrite? (y/n): ').lower()

        if overwrite_input in no_inputs:
            print('Generation of "{0}" cancelled.'.format(destination_file))
            exit(0)

    # Render template and write to file
    if template:
        with open(destination_path, 'w') as f:
            f.write(template.render(context))


def manage_command(args):
    """
    Management commands.
    """
    # Get the path to manage.py
    manage_path = get_manage_path(args)

    # Define the process to be run
    process = None

    if args.command == 'start':
        if args.port:
            process = ['python', manage_path, 'runserver', str(args.port)]
        else:
            process = ['python', manage_path, 'runserver']
    elif args.command == 'syncdb':
        process = ['python', manage_path, 'syncdb']

    # Call the process with a little trick to ignore the keyboard interrupt error when it happens
    if process:
        try:
            subprocess.call(process)
        except KeyboardInterrupt:
            pass


def docker_command(args):
    """
    Docker management commands.
    """
    if args.command == 'init':
        docker_init(container=args.container, defaults=args.defaults)

    elif args.command == 'start':
        docker_start(container=args.container)

    elif args.command == 'stop':
        docker_stop(container=args.container, boot2docker=args.boot2docker)

    elif args.command == 'status':
        docker_status()

    elif args.command == 'update':
        docker_update(container=args.container, defaults=args.defaults)

    elif args.command == 'remove':
        docker_remove(container=args.container)

    elif args.command == 'ip':
        docker_ip()


def syncstores_command(args):
    """
    Sync persistent stores.
    """
    # Get the path to manage.py
    manage_path = get_manage_path(args)

    # This command is a wrapper for a custom Django manage.py method called syncstores.
    # See tethys_apps.mangement.commands.syncstores
    process = ['python', manage_path, 'syncstores']

    if args.refresh:
        valid_inputs = ('y', 'n', 'yes', 'no')
        no_inputs = ('n', 'no')
        proceed = raw_input('{1}WARNING:{2} You have specified the database refresh option. This will drop all of the '
                            'databases for the following apps: {0}. This could result in significant data loss and '
                            'cannot be undone. Do you wish to continue? (y/n): '.format(', '.join(args.app),
                                                                                        TerminalColors.WARNING,
                                                                                        TerminalColors.ENDC)).lower()

        while proceed not in valid_inputs:
            proceed = raw_input('Invalid option. Do you wish to continue? (y/n): ').lower()

        if proceed not in no_inputs:
            process.extend(['-r'])
        else:
            print('Operation cancelled by user.')
            exit(0)

    if args.firsttime:
        process.extend(['-f'])

    if args.database:
        process.extend(['-d', args.database])

    if args.app:
        process.extend(args.app)

    try:
        subprocess.call(process)
    except KeyboardInterrupt:
        pass


def tethys_command():
    """
    Tethys commandline interface function.
    """
    # Create parsers
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title='Commands')

    # Setup scaffold command
    scaffold_parser = subparsers.add_parser('scaffold', help='Create a new Tethys app project from a scaffold.')
    scaffold_parser.add_argument('name', help='The name of the new Tethys app project to create. Only lowercase '
                                              'letters, numbers, and underscores allowed.')
    scaffold_parser.set_defaults(func=scaffold_command)

    # Setup generate command
    gen_parser = subparsers.add_parser('gen', help='Aids the installation of Tethys by automating the '
                                                   'creation of supporting files.')
    gen_parser.add_argument('type', help='The type of object to generate.', choices=VALID_GEN_OBJECTS)
    gen_parser.add_argument('-d', '--directory', help='Destination directory for the generated object.')
    gen_parser.set_defaults(func=generate_command)

    # Setup start server command
    manage_parser = subparsers.add_parser('manage', help='Management commands for Tethys Platform.')
    manage_parser.add_argument('command', help='Management command to run.', choices=['start', 'syncdb'])
    manage_parser.add_argument('-m', '--manage', help='Absolute path to manage.py for Tethys Platform installation.')
    manage_parser.add_argument('-p', '--port', type=int, help='Port on which to start the development server.')
    manage_parser.set_defaults(func=manage_command)

    # Sync stores command
    syncstores_parser = subparsers.add_parser('syncstores', help='Management command for App Persistent Stores.')
    syncstores_parser.add_argument('app', help='Name of the target on which to perform persistent store sync OR "all" '
                                               'to sync all of them.',
                                   nargs='+')
    syncstores_parser.add_argument('-r', '--refresh',
                                   help='When called with this option, the tables will be dropped prior to syncing'
                                        ' resulting in a refreshed database.',
                                   action='store_true',
                                   dest='refresh')
    syncstores_parser.add_argument('-f', '--firsttime',
                                   help='Call with this option to force the initializer functions to be executed with '
                                        '"first_time" parameter True.',
                                   action='store_true',
                                   dest='firsttime')
    syncstores_parser.add_argument('-d', '--database', help='Name of database to sync.')
    syncstores_parser.add_argument('-m', '--manage', help='Absolute path to manage.py for Tethys Platform installation.')
    syncstores_parser.set_defaults(func=syncstores_command, refresh=False, firstime=False)

    # Setup the docker commands
    docker_parser = subparsers.add_parser('docker', help="Management commands for the Tethys Docker containers.")
    docker_parser.add_argument('command',
                               help='Docker command to run.',
                               choices=['init', 'start', 'stop', 'status', 'update', 'remove', 'ip'])
    docker_parser.add_argument('-d', '--defaults',
                               action='store_true',
                               dest='defaults',
                               help="Run command without prompting without interactive input, using defaults instead.")
    docker_parser.add_argument('-c', '--container',
                               help="Execute the command only on the given container.",
                               choices=[POSTGIS_INPUT, GEOSERVER_INPUT, N52WPS_INPUT])
    docker_parser.add_argument('-b', '--boot2docker',
                               action='store_true',
                               dest='boot2docker',
                               help="Stop boot2docker on container stop. Only applicable to stop command.")
    docker_parser.set_defaults(func=docker_command)

    # Parse the args and call the default function
    args = parser.parse_args()
    args.func(args)