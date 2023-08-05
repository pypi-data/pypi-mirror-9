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

    keyword_load_last_modified = False

    if args[-1] in ["last", "l",]:
        args = args[:-1]

        if len(args) == 0:
            filenames = whichfiles.lastedited()
            launch_editor(filenames, command)
            sys.exit(0)
        else:
            keyword_load_last_modified = True

    filenames = whichfiles.keyword(args)

    if len(filenames) > 1:
        if keyword_load_last_modified == True:
            launch_editor([filenames[0],], command)
        else:
            if len(filenames) > 12:
                print('\n'.join(filenames[:12]))
                print('\n[ and {0} more ... ]'.format(len(filenames) - 12))
            else:
                print('\n'.join(filenames))
    else:
        launch_editor(filenames, command)
