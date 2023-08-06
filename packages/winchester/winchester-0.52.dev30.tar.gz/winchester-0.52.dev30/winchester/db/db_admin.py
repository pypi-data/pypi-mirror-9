import argparse
import alembic
import logging

from winchester.db.alembic_command import AlembicCommandLine


logger = logging.getLogger(__name__)


class DBAdminCommandLine(AlembicCommandLine):
    description = "Winchester DB admin commandline tool."

    def add_options(self, parser):
        parser.add_argument('--config', '-c',
                            default='winchester.yaml',
                            type=str,
                            help='The name of the winchester config file')


    def get_config(self, options):
        alembic_cfg = alembic.config.Config()
        alembic_cfg.set_main_option("winchester_config", options.config)
        alembic_cfg.set_main_option("script_location", "winchester.db:migrations")
        return alembic_cfg


def main():
    cmd = DBAdminCommandLine(allowed_commands=['upgrade', 'downgrade',
                                               'current', 'history', 'stamp'])
    cmd.main()


if __name__ == '__main__':
    main()
