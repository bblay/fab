#!/usr/bin/env python
import os

from fab.build_config import BuildConfig
from fab.steps.link_exe import LinkSharedObject
from gcom_build_common import common_build_steps
from grab_gcom import gcom_source_config


def gcom_so_config():
    """
    Create a shared object for linking.

    """
    config = BuildConfig(label='gcom shared object', source_root=gcom_source_config().source_root)
    config.steps = [
        *common_build_steps(fpic=True),
        LinkSharedObject(
            # todo: how best to specify this location
            linker=os.path.expanduser('~/.conda/envs/sci-fab/bin/mpifort'),
            output_fpath='$output/libgcom.so'),
    ]

    return config


if __name__ == '__main__':
    gcom_so_config().run()
