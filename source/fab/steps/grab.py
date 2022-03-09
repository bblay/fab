import os
from pathlib import Path
from typing import Dict

from svn import remote

from fab.steps import Step
from fab.util import run_command


# todo: abc
class GrabBase(Step):
    def __init__(self, src, dst_label, name=None):
        super().__init__(name=name or f'{self.__class__.__name__} {dst_label}')
        self.src: Path = src
        self.dst_label: Path = dst_label

    def run(self, artefacts: Dict, config):
        super().run(artefacts, config)
        if not config.source_root.exists():
            config.source_root.mkdir(parents=True, exist_ok=True)


# todo: currently only works  with a trailing slash - address this
class GrabFolder(GrabBase):
    """
    Step to copy a source folder to the project workspace.

    """
    def run(self, artefacts: Dict, config):
        super().run(artefacts, config)

        command = ['rsync', '-ruq', str(os.path.expanduser(self.src)), str(config.source_root / self.dst_label)]
        run_command(command)


# todo: allow checkout instead of export for repeated runs? (so it knows what not to download?)
class GrabSvn(GrabBase):
    def __init__(self, src, dst_label, revision=None, name=None):
        super().__init__(src, dst_label, name)
        self.revision = revision

    def run(self, artefacts: Dict, config):
        super().run(artefacts, config)

        r = remote.RemoteClient(self.src)
        r.export(str(config.source_root / self.dst_label), revision=self.revision, force=True)
