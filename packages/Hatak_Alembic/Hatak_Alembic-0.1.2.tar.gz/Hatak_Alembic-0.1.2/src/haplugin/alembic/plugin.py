from hatak.plugin import Plugin
from haplugin.sql import SqlPlugin

from .commands import AlembicCommand, InitDatabase


class AlembicPlugin(Plugin):

    def add_commands(self, parent):
        parent.add_command(AlembicCommand())
        parent.add_command(InitDatabase())

    def add_depedency_plugins(self):
        self.app._validate_dependency_plugin(SqlPlugin)
