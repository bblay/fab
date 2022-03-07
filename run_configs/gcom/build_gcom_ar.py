from fab.build_config import BuildConfig
from gcom_build_steps import common_build_steps, grab_step, object_archive_step


def gcom_ar_config():
    """
    Create an object archive for linking.

    """
    config = BuildConfig(
        label='gcom static library',
        # debug_skip=True,
        # multiprocessing=False,
    )
    config.steps = [
        grab_step(),
        *common_build_steps(),
        object_archive_step(),
    ]

    return config


if __name__ == '__main__':
    gcom_ar_config().run()

    # metrics_summary()
