import getpass
import logging
import os
from datetime import datetime
from fnmatch import fnmatch
import multiprocessing
from multiprocessing import cpu_count
from string import Template
from pathlib import Path
from typing import List

from fab.constants import BUILD_OUTPUT, SOURCE
from fab.metrics import send_metric, init_metrics, stop_metrics, metrics_summary
from fab.steps import Step
from fab.util import TimerLogger

logger = logging.getLogger('fab')


class BuildConfig(object):

    def __init__(self, label, source_root=None,
                 fab_workspace_root=None, steps: List[Step]=None,
                 multiprocessing=True, n_procs=None,
                 debug_skip=False):

        self.label = label

        # workspace folder
        if fab_workspace_root:
            fab_workspace_root = Path(fab_workspace_root)
        elif os.getenv("FAB_WORKSPACE"):
            fab_workspace_root = Path(os.getenv("FAB_WORKSPACE"))
        else:
            fab_workspace_root = Path("fab-workspace").absolute()
        self.workspace = fab_workspace_root / (label.replace(' ', '-'))

        # source config
        self.source_root = source_root or self.workspace / SOURCE

        # build steps
        self.steps: List[Step] = steps or []  # use default zero-config steps here

        # multiprocessing config
        self.multiprocessing = multiprocessing
        self.n_procs = n_procs
        if self.multiprocessing and not self.n_procs:
            # todo: can we use *all* available cpus, not -1, without causing a bottleneck?
            self.n_procs = max(1, len(os.sched_getaffinity(0)) - 1)

        self.debug_skip = debug_skip

    def logging_header(self):
        logger.info(f"{datetime.now()}")
        if self.multiprocessing:
            logger.info(f'machine cores: {cpu_count()}')
            logger.info(f'available cores: {len(os.sched_getaffinity(0))}')
            logger.info(f'using n_procs = {self.n_procs}')
        logger.info(f"workspace is {self.workspace}")

    def run(self):
        start_time = datetime.now().replace(microsecond=0)
        self.logging_header()

        if not self.workspace.exists():
            logger.info("creating workspace")
            self.workspace.mkdir(parents=True)

        artefacts = dict()
        # metrics_recv_conn, metrics_send_conn = multiprocessing.Pipe(duplex=False)
        init_metrics()
        # metrics_queue = multiprocessing.Queue()

        with TimerLogger(f'running {self.label} build steps') as steps_timer:

            # todo: passing self to a contained object smells like an anti pattern
            for step in self.steps:
                with TimerLogger(step.name) as step_timer:
                    step.run(artefacts=artefacts, config=self)
                send_metric('steps', step.name, step_timer.taken)

        send_metric('run', 'label', self.label)
        send_metric('run', 'datetime', start_time.isoformat())
        send_metric('run', 'time taken', steps_timer.taken)
        send_metric('run', 'sysname', os.uname().sysname)
        send_metric('run', 'nodename', os.uname().nodename)
        send_metric('run', 'machine', os.uname().machine)
        send_metric('run', 'user', getpass.getuser())

        # metrics_send_conn.close()
        stop_metrics()
        metrics_summary(self.workspace)

        # # read the metrics from the pipe
        # return collate_metrics(metrics_send_conn)


class PathFilter(object):
    def __init__(self, path_filters, include):
        self.path_filters = path_filters
        self.include = include

    def check(self, path):
        if any(i in str(path) for i in self.path_filters):
            return self.include
        return None


class AddFlags(object):
    """
    Add flags when our path filter matches.

    For example, add an include path for certain sub-folders.

    """
    def __init__(self, match: str, flags: List[str]):
        self.match: str = match
        self.flags: List[str] = flags

    def run(self, fpath: Path, input_flags: List[str], source_root: Path, workspace: Path):
        """
        See if our filter matches the incoming file. If it does, add our flags.

        """
        params = {'relative': fpath.parent, 'source': source_root, 'output': workspace / BUILD_OUTPUT}

        # does the file path match our filter?
        if not self.match or fnmatch(fpath, Template(self.match).substitute(params)):

            # use templating to render any relative paths in our flags
            add_flags = [Template(flag).substitute(params) for flag in self.flags]

            # add our flags
            input_flags += add_flags


class FlagsConfig(object):
    """
    Return flags for a given path. Contains a list of PathFlags.

    Multiple path filters can match a given path.
    For now, simply allows appending flags but will likely evolve to replace or remove flags.

    """
    def __init__(self, common_flags=None, path_flags: List[AddFlags]=None):
        self.common_flags = common_flags or []
        self.path_flags = path_flags or []

    def flags_for_path(self, path, source_root, workspace):

        # We COULD make the user pass these template params to the constructor
        # but we have a design requirement to minimise the config burden on the user,
        # so we take care of it for them here instead.
        params = {'source': source_root, 'output': workspace / BUILD_OUTPUT}
        flags = [Template(i).substitute(params) for i in self.common_flags]

        for flags_modifier in self.path_flags:
            flags_modifier.run(path, flags, source_root=source_root, workspace=workspace)

        return flags
