import os

class EdiCommand(object):
    """Represents an individual command from an Edi YAML file."""
    def __init__(self, rule_dict):
        self.name = rule_dict.get('name')
        self.command = rule_dict.get('command')

    def __repr__(self):
        return "({0}, {1})".format(self.name, self.command)
