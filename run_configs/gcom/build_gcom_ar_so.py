import os

from fab.build_config import BuildConfig
from fab.steps.archive_objects import ArchiveObjects
from fab.steps.link_exe import LinkSharedObject
from gcom_build_common import common_build_steps, compilers, grab_step


def gcom_both_config():
    """
    Create both a shared object and an object archive.

    """
    config = BuildConfig(label='gcom shared and static libraries')
    config.steps = [
        grab_step(),

        # ar
        *common_build_steps(),
        ArchiveObjects(archiver='ar', output_fpath='$output/libgcom.a'),

        # so
        *compilers(fpic=True),
        LinkSharedObject(
            linker=os.path.expanduser('~/.conda/envs/sci-fab/bin/mpifort'),
            output_fpath='$output/libgcom.so'),
    ]

    return config


if __name__ == '__main__':
    gcom_both_config().run()
