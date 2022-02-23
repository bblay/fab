#!/usr/bin/env python

from fab.build_config import BuildConfig
from fab.constants import SOURCE
from fab.fab_main import fab_main
from fab.steps.archive_objects import ArchiveObjects
from run_configs.gcom.gcom_build_common import common_build_steps


def gcom_ar_config(fab_workspace_root=None):
    """
    Create an object archive library for static linking.

    """
    config = BuildConfig(label='gcom object archive', fab_workspace_root=fab_workspace_root)
    config.grab_config = {("gcom", "/home/h02/bblay/svn/gcom/trunk/build/"), }
    config.steps = [
        *common_build_steps(source_folder=config.workspace / SOURCE),
        ArchiveObjects(archiver='ar', output_fpath='$output/libgcom.a'),
    ]

    return config


if __name__ == '__main__':
    fab_main(gcom_ar_config())
