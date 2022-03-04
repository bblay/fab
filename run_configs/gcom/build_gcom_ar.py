import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from fab.build_config import BuildConfig

from gcom_build_steps import common_build_steps, grab_step, object_archive_step


def gcom_ar_config():
    """
    Create an object archive for linking.

    """
    config = BuildConfig(
        label='gcom static library',
        debug_skip=True,
        multiprocessing=False,
    )
    config.steps = [
        grab_step(),
        *common_build_steps(),
        object_archive_step(),
    ]

    return config


def metrics_summary(metrics):
    top_ten = sorted(metrics['compile fortran'].items(), key=lambda kv: kv[1], reverse=True)[:10]
    print("top ten", top_ten)

    plt.hist(metrics['compile fortran'].values(), 10)
    plt.savefig("foo.png")

    plt.pie(metrics['steps'].values(), labels=metrics['steps'].keys(), normalize=True)
    plt.savefig("pie.png")


if __name__ == '__main__':
    metrics = gcom_ar_config().run()

    metrics_summary(metrics)
