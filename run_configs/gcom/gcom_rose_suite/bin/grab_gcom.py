from gcom_build_steps import grab_step  # copied here by the rose suite config

from fab.build_config import BuildConfig


def gcom_source_config():
    """
    Grab the gcom source, for use by multiple rose build configs.

    """
    return BuildConfig(
        label='gcom source',
        steps=[
            grab_step()
        ])


if __name__ == '__main__':
    print("__main__")
    gcom_source_config().run()
