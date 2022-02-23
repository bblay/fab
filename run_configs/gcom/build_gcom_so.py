#!/usr/bin/env python

import os

from fab.build_config import BuildConfig
from fab.constants import SOURCE
from fab.fab_main import fab_main
from fab.steps.link_exe import LinkSharedObject
from run_configs.gcom.gcom_build_common import common_build_steps


def gcom_so_config(fab_workspace_root=None):
    """
    Create a shared object library for dynamic linking.

    """
    config = BuildConfig(label='gcom shared object', fab_workspace_root=fab_workspace_root)
    config.grab_config = {("gcom", "/home/h02/bblay/svn/gcom/trunk/build/"), }
    config.steps = [
        *common_build_steps(source_folder=config.workspace / SOURCE, fpic=True),
        LinkSharedObject(
            # todo: how best to specify this location
            linker=os.path.expanduser('~/.conda/envs/sci-fab/bin/mpifort'),
            output_fpath='$output/libgcom.so'),
    ]

    return config


if __name__ == '__main__':
    fab_main(gcom_so_config())
