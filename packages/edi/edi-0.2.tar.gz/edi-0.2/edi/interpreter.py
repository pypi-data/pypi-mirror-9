from __future__ import print_function
import os
import sys
import whichfiles
import yaml_config
import default_editor
import edi_command
import parent_checker

def launch_editor(filenames, editor):
    """Launch the default editor."""
    if len(filenames) == 0:
        print("No matching filenames found.")
    else:
        print("Loading:\n - {0}".format('\n - '.join(filenames)))
        os.system(editor.format(' '.join(filenames)))

def cli_interface():
    """CLI interpreter for edi."""
    args = sys.argv[1:]
    config = yaml_config.EdiConfig()

    cwd = os.getcwd()
    git_repo = os.path.dirname(parent_checker.parent_checker(".git"))

    # TODO: use current directory
    # TODO: work without a git repo
    # TODO: work with an hg repo.
    # TODO: edi 5 last = 5 last changed files

    if len(args) == 0 or len(args) == 1 and args[0] in ['-h', '--help', 'help']:
        print("Usage: edi [keyword1 keyword2 keyword3 ... ]")
        sys.exit(1)

    if config.no_config():
        commands = [yaml_config.EdiCommand({'name':'default', 'command': default_editor.default_editor()}),]
    else:
        trigger_hit, commands = config.get_commands(args[-1])

        if trigger_hit:
            args = args[:-1]

    command = commands[0].command

    if len(args) == 0:
        print("You must specify some key words.")
        sys.exit(1)

    # First check to see if there are files specified directly in the args (e.g. if user wnent to a dir and went edi *)
    # => In which case don't bother with keyword silliness, just open them.
    if len([arg for arg in args if os.path.exists(arg)]) == len(args):
        filenames_without_directories = [arg for arg in args if not os.path.isdir(arg)]
        sorted_filenames = sorted(filenames_without_directories, key=os.path.getctime, reverse=True)
        launch_editor(sorted_filenames, command)
        sys.exit()

    if args[0] == 'last':
        if len(args) == 1:
            filenames = whichfiles.lastedited()
        else:
            filenames = whichfiles.lastedited(howmany=int(args[1]))
        launch_editor(filenames, command)
        sys.exit(0)

    # Last argument is a number
    if args[-1].isdigit():
        filenames = whichfiles.keyword(args[:-1])
        load_how_many = int(args[-1])
    else:
        filenames = whichfiles.keyword(args)
        load_how_many = None

    # If more than one mathing file
    if len(filenames) > 1:
        if load_how_many is not None:
            if len(filenames) <= load_how_many:
                launch_editor(filenames, command)
    else:
        launch_editor([filenames[0],], command)

    # More than 12 filenames = just show first 12
    if len(filenames) > 12:
        print('\n'.join(filenames[:12]))
        print('\n[ and {0} more ... ]'.format(len(filenames) - 12))
    else:
        print('\n'.join(filenames))
