from gcom_build_steps import common_build_steps, link_shared_object_step  # copied here by the rose suite config

from fab.build_config import BuildConfig
from grab_gcom import gcom_source_config


def gcom_so_config():
    """
    Create a shared object for linking.

    """
    config = BuildConfig(
        label='gcom shared object',
        # The grab step was run in a separate rose task, and therefore build config, and therefore workspace.
        # Use the grab config to see where it went. Depends on both rose jobs having the same $FAB_WORKSPACE.
        source_root=gcom_source_config().source_root)
    config.steps = [
        *common_build_steps(fpic=True),
        link_shared_object_step(),
    ]

    return config


if __name__ == '__main__':
    gcom_so_config().run()
