import sys
from configparser import ConfigParser
from alembic.config import CommandLine, Config
from alembic.command import stamp
import venusian
import re

from hatak.command import Command

from haplugin.sql.testing import DatabaseTestCreation


class AlembicCommand(Command):

    def __init__(self):
        super().__init__('database', 'alembic')

    def __call__(self, args):
        self.settings = self.app.settings
        self.paths = self.app.paths
        self.generate_config()
        self.set_sys_argb(args)
        self.run_alembic()

    def generate_config(self):
        config = ConfigParser()
        config['alembic'] = {
            'script_location': self.paths['alembic']['versions'],
            'sqlalchemy.url': self.settings['db']['url'],
        }
        config['loggers'] = {
            'keys': 'root,sqlalchemy,alembic',
        }
        config['handlers'] = {
            'keys': 'console',
        }
        config['formatters'] = {
            'keys': 'generic, hatak',
        }
        config['logger_root'] = {
            'level': 'WARN',
            'handlers': 'console',
            'qualname': '',
        }
        config['logger_sqlalchemy'] = {
            'level': 'WARN',
            'handlers': '',
            'qualname': 'sqlalchemy.engine',
        }
        config['logger_alembic'] = {
            'level': 'INFO',
            'handlers': '',
            'qualname': 'alembic',
        }
        config['handler_console'] = {
            'class': 'StreamHandler',
            'args': '(sys.stderr,)',
            'level': 'NOTSET',
            'formatter': 'hatak',
        }
        config['formatter_hatak'] = {
            'format': '[Alembic] %(message)s',
        }

        with open(self.paths['alembic:ini'], 'w') as configfile:
            config.write(configfile)
            configfile.write('''[formatter_generic]
    datefmt = %H:%M:%S
    format = %(levelname)-5.5s [%(name)s] %(message)s
''')

    def set_sys_argb(self, args):
        sys.argv[1] = '-c'
        sys.argv.insert(2, self.paths['alembic']['ini'])
        if 'init' in sys.argv:
            sys.argv.append(self.paths['alembic']['versions'])

    def run_alembic(self):
        CommandLine().main()


class InitDatabase(AlembicCommand):

    def __init__(self):
        super(AlembicCommand, self).__init__('database', 'init')

    def run_alembic(self):
        creator = DatabaseTestCreation(self.app.settings)
        if '--iwanttodeletedb' in sys.argv:
            print("[Hatak] Removing old database...")
            creator.recreate_database('mainurl')
        print('[Hatak] Scanning for models...')
        scan = venusian.Scanner()
        scan.scan(
            __import__(self.app.module),
            ignore=[re.compile('tests$').search])
        print('[Hatak] Initializing database...')
        db = creator.init_db()
        if self.settings.get('fixtures', None):
            print('[Hatak] Creating fixtures...')
            Fixtures = self.app._import_from_string(self.settings['fixtures'])
            Fixtures(db, self.app).create_all()

        alembic_cfg = Config(self.paths['alembic:ini'])
        stamp(alembic_cfg, 'head')
