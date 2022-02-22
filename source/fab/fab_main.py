import logging
import os

from fab.constants import SOURCE
from fab.builder import Build
from fab.util import time_logger, run_command


def fab_main(config):
    """
    Helper function to run fab with a given config.

    """
    logger = logging.getLogger('fab')
    # logger.setLevel(logging.DEBUG)
    logger.setLevel(logging.INFO)

    # ignore this, it's not here :)
    with time_logger("grabbing"):
        grab_will_do_this(config.grab_config, config.workspace)

    with time_logger("gcom build ar"):
        Build(config=config).run()


def grab_will_do_this(src_paths, workspace):
    for label, src_path in src_paths:
        # shutil.copytree(
        #     os.path.expanduser(src_path),
        #     workspace / SOURCE_ROOT / label,
        #     dirs_exist_ok=True,
        #     ignore=shutil.ignore_patterns('.svn')
        # )

        # todo: ignore_patterns('.svn')
        command = ['rsync', '-ruq', str(os.path.expanduser(src_path)), str(workspace / SOURCE / label)]
        run_command(command)
