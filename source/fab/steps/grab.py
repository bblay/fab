import os
from pathlib import Path
from typing import Dict

from fab.steps import Step
from fab.util import run_command


class GrabFolder(Step):
    """
    Step to copy a source folder to the project workspace.

    """
    def __init__(self, src, dst_label, name='grab folder'):
        super().__init__(name)
        self.src: Path = src
        self.dst_label: Path = dst_label

    def run(self, artefacts: Dict, config):
        if not config.source_root.exists():
            config.source_root.mkdir(parents=True, exist_ok=True)

        command = ['rsync', '-ruq', str(os.path.expanduser(self.src)), str(config.source_root / self.dst_label)]
        run_command(command)
