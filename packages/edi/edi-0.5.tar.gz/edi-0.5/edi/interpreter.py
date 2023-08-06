import os, whichfiles, yaml_config, default_editor, edi_command, parent_checker
from sys import stdout, stderr, argv, exit

def launch_editor(filenames, editor):
    """Launch the default editor and quit (or show error msg if no filenames listed)."""
    if len(filenames) == 0:
        stderr.write("No matching filenames found.\n")
        exit(1)
    else:
        stdout.write("Loading:\n - {0}\n".format('\n - '.join(filenames)))
        os.system(editor.format(' '.join(filenames)))
        exit()

def cli_interface():
    """CLI interpreter for edi."""
    args = argv[1:]
    config = yaml_config.EdiConfig()
    cwd = os.getcwd()
    git_repo = os.path.dirname(parent_checker.parent_checker(".git"))

    # TODO: use current directory
    # TODO: work without a git repo
    # TODO: work with an hg repo.

    if len(args) == 0 or len(args) == 1 and args[0] in ['-h', '--help', 'help']:
        stdout.write("Usage:\n\n")
        stdout.write("                   edi keyword1 - Open file matching keyword1.\n")
        stdout.write("          edi keyword1 keyword2 - Open file matching keyword1 and keyword2.\n")
        stdout.write(" edi keyword1 keyword2 keyword3 - Open file matching all keywords.\n")
        stdout.write("                       edi last - Open last 10 files that you modified.\n")
        stdout.write("                     edi last 5 - Open last 5 files that you modified.\n")
        exit(1)

    if config.no_config():
        commands = [edi_command.EdiCommand({'name':'default', 'command': default_editor.default_editor()}),]
    else:
        trigger_hit, commands = config.get_commands(args[-1])

        if trigger_hit:
            args = args[:-1]

    command = commands[0].command

    if len(args) == 0:
        stderr.write("You must specify some key words.\n")
        exit(1)

    # First check to see if there are files specified directly in the args (e.g. if user wnent to a dir and went edi *)
    # => In which case don't bother with keyword silliness, just open them.
    if len([arg for arg in args if os.path.exists(arg)]) == len(args):
        filenames_without_directories = [arg for arg in args if not os.path.isdir(arg)]
        sorted_filenames = sorted(filenames_without_directories, key=os.path.getctime, reverse=True)
        launch_editor(sorted_filenames, command)
        exit()

    if args[0] == 'last':
        if len(args) == 1:
            filenames = whichfiles.lastedited()
        else:
            filenames = whichfiles.lastedited(howmany=int(args[1]))
        launch_editor(filenames, command)
        exit(0)

    # Last argument is a number? Use for "edi last 5"
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
        if len(filenames) > 0:
            launch_editor([filenames[0],], command)
        else:
            launch_editor([], command)

    # More than 12 filenames = just show first 12
    if len(filenames) > 12:
        stdout.write("{0}\n".format('\n'.join(filenames[:12])))
        stdout.write('\n[ and {0} more ... ]'.format(len(filenames) - 12))
    else:
        stdout.write("{0}\n".format('\n'.join(filenames)))
