from fab.build_config import BuildConfig
from fab.steps.archive_objects import ArchiveObjects
from fab.steps.grab import GrabFolder
from gcom_rose_suite.gcom_build_common import common_build_steps


def gcom_ar_config():
    """
    Create both a shared object and an object archive.

    """
    config = BuildConfig(label='gcom shared and static libraries')
    config.steps = [
        GrabFolder(src="/home/h02/bblay/svn/gcom/trunk/build/", dst_label="gcom"),
        *common_build_steps(),
        ArchiveObjects(archiver='ar', output_fpath='$output/libgcom.a'),

    ]

    return config


if __name__ == '__main__':
    gcom_ar_config().run()
