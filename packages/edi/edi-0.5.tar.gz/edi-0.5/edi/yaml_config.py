import os, yaml, edi_command, parent_checker



class EdiConfig(object):
    """Represents an Edi YAML config file containing EdiCommands. See /example_configs for examples."""
    rules = None

    def __init__(self):
        """Look for a .edi.yml file in every directory above the current one. If found, read it."""
        ediyml_filename = parent_checker.parent_checker(".edi.yml")

        if not ediyml_filename:
            self.rules = []
        else:
            with open(ediyml_filename, 'r') as ediyml_handle:
                self.rules = yaml.safe_load(ediyml_handle.read())

    def no_config(self):
        """Poor user is going to get whatever his system thinks his favorite text editor is."""
        return len(self.rules) == 0

    def get_commands(self, trigger):
        """Get a list of commands - either default command(s) (if no trigger hit), or the specified command(s) (if there is a hit)."""
        commands = [edi_command.EdiCommand(x) for x in self.rules if "trigger" in x and x.get('trigger', '') == trigger]
        return (False, [edi_command.EdiCommand(x) for x in self.rules if "trigger" not in x]) if len(commands) == 0 else (True, commands)
