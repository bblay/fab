import os
from pathlib import Path
from typing import Dict

from svn import remote

from fab.steps import Step
from fab.util import run_command


# todo: currently only works  with a trailing slash - address this
class GrabFolder(Step):
    """
    Step to copy a source folder to the project workspace.

    """
    def __init__(self, src, dst_label, name=None):
        super().__init__(name or f'grab folder {dst_label}')
        self.src: Path = src
        self.dst_label: Path = dst_label

    def run(self, artefacts: Dict, config):
        super().run(artefacts, config)

        if not config.source_root.exists():
            config.source_root.mkdir(parents=True, exist_ok=True)

        command = ['rsync', '-ruq', str(os.path.expanduser(self.src)), str(config.source_root / self.dst_label)]
        run_command(command)


class GrabSvn(Step):

    def __init__(self, src, dst_label, name=None):
        super().__init__(name or f'grab svn {dst_label}')
        self.src = src
        self.dst_label = dst_label

    def run(self, artefacts: Dict, config):
        super().run(artefacts, config)

        if not config.source_root.exists():
            config.source_root.mkdir(parents=True, exist_ok=True)

        r = remote.RemoteClient(self.src)
        r.checkout(str(config.source_root / self.dst_label))
