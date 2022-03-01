#!/usr/bin/env python

from fab.build_config import BuildConfig
from fab.steps.archive_objects import ArchiveObjects
from gcom_build_common import common_build_steps
from grab_gcom import gcom_source_config


def gcom_ar_config():
    """
    Create an object archive for linking.

    """
    config = BuildConfig(label='gcom object archive', source_root=gcom_source_config().source_root)
    config.steps = [
        *common_build_steps(),
        ArchiveObjects(archiver='ar', output_fpath='$output/libgcom.a'),
    ]

    return config


if __name__ == '__main__':
    gcom_ar_config().run()
