#!/usr/bin/env python

from fab.build_config import BuildConfig
from fab.steps.grab import GrabFolder


def gcom_source_config():
    """
    Grab the gcom source, for use by multiple rose build configs.

    """
    config = BuildConfig(label='gcom source')
    config.steps = [
        GrabFolder(src="/home/h02/bblay/svn/gcom/trunk/build/", dst_label="gcom"),
    ]

    return config


if __name__ == '__main__':
    gcom_source_config().run()
