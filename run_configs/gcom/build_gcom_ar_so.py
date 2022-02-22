import os

from fab.build_config import BuildConfig
from fab.constants import SOURCE
from fab.fab_main import fab_main
from fab.steps.archive_objects import ArchiveObjects
from fab.steps.link_exe import LinkSharedObject
from run_configs.gcom.gcom_build_common import common_build_steps, compilers


def gcom_both_config(fab_workspace_root=None):
    """
    Create both a shared object and an object archive.

    """
    config = BuildConfig(label='gcom object archive', fab_workspace_root=fab_workspace_root)
    config.grab_config = {("gcom", "/home/h02/bblay/svn/gcom/trunk/build"), }
    config.steps = [
        *common_build_steps(source_folder=config.workspace / SOURCE),
        ArchiveObjects(archiver='ar', output_fpath='$output/libgcom.a'),

        *compilers(fpic=True),
        LinkSharedObject(
            linker=os.path.expanduser('~/.conda/envs/sci-fab/bin/mpifort'),
            output_fpath='$output/libgcom.so'),
    ]

    return config


if __name__ == '__main__':
    fab_main(gcom_both_config())
