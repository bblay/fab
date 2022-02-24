#!/usr/bin/env python

from fab.build_config import BuildConfig
from gcom_build_common import grab_step


def gcom_source_config():
    """
    Grab the gcom source, for use by multiple rose build configs.

    """
    return BuildConfig(label='gcom source', steps=[grab_step()])


if __name__ == '__main__':
    gcom_source_config().run()
