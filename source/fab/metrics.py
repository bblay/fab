import datetime
import logging
from collections import defaultdict
from multiprocessing import Process, Pipe
from multiprocessing.connection import Connection
from pathlib import Path
from typing import Optional

logger = logging.getLogger('fab')

# the pipe connections for individual metrics
_metric_recv_conn: Optional[Connection] = None
_metric_send_conn: Optional[Connection] = None

# the process which receives individual metrics
_metric_recv_process: Optional[Process] = None

# the pipe connection for receiving the collated metrics, once they've stopped being sent
_all_metrics_recv_conn: Optional[Connection] = None


def init_metrics():
    global _metric_recv_conn, _metric_send_conn, _metric_recv_process, _all_metrics_recv_conn

    # the pipe connections for individual metrics
    _metric_recv_conn, _metric_send_conn = Pipe(duplex=False)

    # the pipe connections for the collated metrics, once they've stopped being sent
    _all_metrics_recv_conn, all_metrics_send_conn = Pipe(duplex=False)

    # start the receiving process
    _metric_recv_process = Process(target=read_metric, args=(_metric_recv_conn, all_metrics_send_conn))
    _metric_recv_process.start()


def read_metric(metric_recv_conn: Connection, all_metrics_send_conn: Connection):
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
            metric = metric_recv_conn.recv()
        except EOFError:
            # logger.info('read_metric: end of metrics')
            break
        except Exception:
            logger.info('read_metric: unhandled error receiving metrics')
            break

        group, name, value = metric
        metrics[group][name] = value
        num_recorded += 1

    logger.info(f"read_metric: recorded {num_recorded} metrics")

    # send the collated metrics
    all_metrics_send_conn.send(metrics)
    all_metrics_send_conn.close()


def send_metric(group: str, name: str, value):
    _metric_send_conn.send([group, name, value])


def stop_metrics():
    _metric_send_conn.close()
    _metric_recv_process.join(1)
    # logger.info(f"_metric_recv_process exit code = {_metric_recv_process.exitcode}")


def metrics_summary(workspace):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    metrics = _all_metrics_recv_conn.recv()

    logger.info(f'metrics_summary: got metrics for: {metrics.keys()}')

    metrics_folder = Path(workspace) / "metrics"
    metrics_folder.mkdir(exist_ok=True)

    # graphs for individual steps
    step_names = ['preprocess fortran', 'preprocess c', 'compile fortran']
    for step_name in step_names:

        fbase = metrics_folder / step_name.replace(' ', '_')

        values = metrics[step_name].values()
        total_time = datetime.timedelta(seconds=int(metrics["steps"][step_name]))

        plt.hist(values, 10)
        plt.suptitle(f'{step_name} histogram\n'
                     f'{len(values)} files took {total_time} on {metrics["run"]["datetime"]}')
        plt.xlabel('time (s)')
        plt.savefig(f"{fbase}.png")
        plt.close()

        top_ten = sorted(metrics[step_name].items(), key=lambda kv: kv[1], reverse=True)[:10]
        with open(f"{fbase}.txt", "wt") as txt_file:
            txt_file.write("top ten\n")
            for i in top_ten:
                txt_file.write(f"{i}\n")

    # overall pie chart of time taken by each step
    step_metrics = metrics['steps'].items()
    step_times = [kv[1] for kv in step_metrics]
    step_labels = [kv[0] for kv in step_metrics]
    plt.pie(step_times, labels=step_labels, normalize=True,
            wedgeprops={"linewidth": 1, "edgecolor": "white"})

    run = metrics['run']
    time_taken = datetime.timedelta(seconds=int(run['time taken']))

    plt.suptitle(f"{run['label']} took {time_taken}\n"
                 f"on {run['sysname']}, {run['nodename']}, {run['machine']}, {metrics['run']['datetime']}")

    plt.savefig(metrics_folder / "pie.png")
    plt.close()
