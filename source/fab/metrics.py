import logging
import os
from collections import defaultdict
from multiprocessing.connection import Connection
from multiprocessing import Process, Pipe
from pathlib import Path

# import matplotlib
# matplotlib.use('Agg')
# import matplotlib.pyplot as plt
from typing import Optional

logger = logging.getLogger('fab')


_metrics = defaultdict(dict)

_metrics_recv_conn: Optional[Connection] = None
_metrics_send_conn: Optional[Connection] = None
_metric_read_process: Optional[Process] = None


def init_metrics():
    global _metrics_recv_conn, _metrics_send_conn, _metric_read_process

    _metrics_recv_conn, _metrics_send_conn = Pipe(duplex=False)

    # start a recording process
    _metric_read_process = Process(target=read_metric, args=(_metrics_recv_conn,))
    _metric_read_process.start()


def read_metric(metrics_recv_conn):
    global _metrics

    # we run in a subprocess, so we get a copy of _metrics_send_conn before it closes.
    # when the calling process finally does close it, we'll still have an open copy of it,
    # so the connection will still be considered open!
    # therefore we close *OUR* copy of it now.
    _metrics_send_conn.close()

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
        _metrics[group][name] = value
        num_recorded += 1

    logger.info(f"read_metric: recorded {num_recorded} metrics")

    metrics_summary()


def send_metric(group: str, name: str, value):
    # called from subprocesses
    _metrics_send_conn.send([group, name, value])


def stop_metrics():
    _metrics_send_conn.close()
    _metric_read_process.join(10)
    logger.info(f"_metric_read_process exit code = {_metric_read_process.exitcode}")


def metrics_summary():

    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    logger.info(f'metrics_summary: got metrics for: {_metrics.keys()}')

    Path('metrics').mkdir(exist_ok=True)

    things = ['preprocess fortran', 'preprocess c', 'compile fortran']
    for thing in things:

        fbase = os.path.join("metrics", thing.replace(' ', '_'))

        plt.hist(_metrics[thing].values(), 10)
        plt.savefig(f"{fbase}.png")
        plt.close()

        top_ten = sorted(_metrics[thing].items(), key=lambda kv: kv[1], reverse=True)[:10]
        with open(f"{fbase}.txt", "wt") as txt_file:
            txt_file.write("top ten\n")
            for i in top_ten:
                txt_file.write(f"{i}\n")

    plt.pie(_metrics['steps'].values(), labels=_metrics['steps'].keys(), normalize=True)
    plt.savefig("metrics/pie.png")
    plt.close()
