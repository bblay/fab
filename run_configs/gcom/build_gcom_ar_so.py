from fab.build_config import BuildConfig

from gcom_build_steps import common_build_steps, compilers, grab_step, link_shared_object_step, object_archive_step


def gcom_both_config():
    """
    Create both a shared object and an object archive for linking.

    """
    config = BuildConfig(label='gcom shared and static libraries')
    config.steps = [
        grab_step(),

        # ar
        *common_build_steps(),
        object_archive_step(),

        # so
        *compilers(fpic=True),
        link_shared_object_step(),
    ]

    return config


if __name__ == '__main__':
    gcom_both_config().run()
