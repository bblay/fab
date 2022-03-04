from fab.build_config import BuildConfig

from gcom_build_steps import common_build_steps, grab_step
from run_configs.gcom.gcom_build_steps import link_shared_object_step


def gcom_both_config():
    """
    Create a shared object for linking.

    """
    config = BuildConfig(label='gcom shared library')
    config.steps = [
        grab_step(),
        *common_build_steps(fpic=True),
        link_shared_object_step(),
    ]

    return config


if __name__ == '__main__':
    gcom_both_config().run()
