from fab.build_config import BuildConfig
from fab.steps.archive_objects import ArchiveObjects
from gcom_build_common import common_build_steps, grab_step


def gcom_ar_config():
    """
    Create both a shared object and an object archive.

    """
    config = BuildConfig(label='gcom static library')
    config.steps = [
        grab_step(),
        *common_build_steps(),
        ArchiveObjects(archiver='ar', output_fpath='$output/libgcom.a'),

    ]

    return config


if __name__ == '__main__':
    gcom_ar_config().run()
