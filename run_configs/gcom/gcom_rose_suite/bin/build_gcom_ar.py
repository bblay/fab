from gcom_build_steps import common_build_steps, object_archive_step  # copied here by the rose suite config

from fab.build_config import BuildConfig
from grab_gcom import gcom_source_config


def gcom_ar_config():
    """
    Create an object archive for linking.

    """
    config = BuildConfig(
        label='gcom object archive',
        # The grab step was run in a separate rose task, and therefore build config, and therefore workspace.
        # Use the grab config to see where it went. Depends on both rose jobs having the same $FAB_WORKSPACE.
        source_root=gcom_source_config().source_root)

    config.steps = [
        *common_build_steps(),
        object_archive_step(),
    ]

    return config


if __name__ == '__main__':
    gcom_ar_config().run()
