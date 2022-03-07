import logging
import os
from collections import defaultdict
from multiprocessing import Process, Pipe
from multiprocessing.connection import Connection
from pathlib import Path
from typing import Optional

logger = logging.getLogger('fab')

_metric_recv_conn: Optional[Connection] = None
_metric_send_conn: Optional[Connection] = None
_metric_recv_process: Optional[Process] = None


def init_metrics(workspace):
    global _metric_recv_conn, _metric_send_conn, _metric_recv_process

    _metric_recv_conn, _metric_send_conn = Pipe(duplex=False)

    # start a recording process
    _metric_recv_process = Process(target=read_metric, args=(_metric_recv_conn, workspace))
    _metric_recv_process.start()


def read_metric(metrics_recv_conn, workspace):
    metrics = defaultdict(dict)

    # todo: do this better
    # we run in a subprocess, so we get a copy of _metric_send_conn before it closes.
    # when the calling process finally does close it, we'll still have an open copy of it,
    # so the connection will still be considered open!
    # therefore we close *OUR* copy of it now.
    _metric_send_conn.close()

    logger.info('read_metric: waiting for metrics')
    num_recorded = 0
    while True:

        try:
            metric = metrics_recv_conn.recv()
            # logger.info(f'got metric {metric}')
            # logger.info(f'metrics for {_metrics.keys()}')
        except EOFError:
            logger.info('read_metric: nd of metrics')
            break
        except Exception:
            logger.info('read_metric: unhandled error receiving metrics')
            break

        group, name, value = metric
        metrics[group][name] = value
        num_recorded += 1

    logger.info(f"read_metric: recorded {num_recorded} metrics")

    metrics_summary(metrics, workspace)


def send_metric(group: str, name: str, value):
    # called from subprocesses
    _metric_send_conn.send([group, name, value])


def stop_metrics():
    _metric_send_conn.close()
    _metric_recv_process.join(10)
    logger.info(f"_metric_recv_process exit code = {_metric_recv_process.exitcode}")


def metrics_summary(metrics, workspace):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    logger.info(f'metrics_summary: got metrics for: {metrics.keys()}')

    metrics_folder = Path(workspace) / "metrics"
    metrics_folder.mkdir(exist_ok=True)

    things = ['preprocess fortran', 'preprocess c', 'compile fortran']
    for thing in things:

        fbase = metrics_folder / thing.replace(' ', '_')

        plt.hist(metrics[thing].values(), 10)
        plt.savefig(f"{fbase}.png")
        plt.close()

        top_ten = sorted(metrics[thing].items(), key=lambda kv: kv[1], reverse=True)[:10]
        with open(f"{fbase}.txt", "wt") as txt_file:
            txt_file.write("top ten\n")
            for i in top_ten:
                txt_file.write(f"{i}\n")

    plt.pie(metrics['steps'].values(), labels=metrics['steps'].keys(), normalize=True)
    plt.savefig(metrics_folder / "pie.png")
    plt.close()
