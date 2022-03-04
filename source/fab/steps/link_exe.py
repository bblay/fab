"""
Link an executable.

"""
import logging
import os
from pathlib import Path
from string import Template
from typing import List

from fab.constants import BUILD_OUTPUT

from fab.steps import Step
from fab.util import log_or_dot, run_command, Artefacts, SourceGetter

logger = logging.getLogger('fab')

DEFAULT_SOURCE_GETTER = Artefacts(['compiled_c', 'compiled_fortran'])


class LinkExe(Step):
    """
    A build step to produce an executable from a list of object (.o) files.

    """

    def __init__(self, linker: str, output_fpath, flags=None, source: SourceGetter = None, name='link exe'):
        """
        Args:
            - linker: E.g 'gcc' or 'ld'.
            - flags: A list of flags to pass to the linker.
            - output_fpath: The file path of the output exe.
            - source:
            - name:

        """
        super().__init__(name)
        self.source_getter = source or DEFAULT_SOURCE_GETTER
        self.linker = linker
        self.flags: List[str] = flags or []
        self.output_fpath: str = str(output_fpath)

    def run(self, artefacts, config, metrics_send_conn):
        """
        Links all the object files in the *compiled_c* and *compiled_fortran* artefacts.

        (Current thinking) does not create an entry in the artefacts dict.

        """
        super().run(artefacts, config, metrics_send_conn)

        compiled_files = self.source_getter(artefacts)

        command = [self.linker]

        output_fpath = Template(self.output_fpath).substitute(output=str(config.workspace / BUILD_OUTPUT))
        output_fpath = os.path.abspath(output_fpath)
        if self._config.debug_skip and Path(output_fpath).exists():
            logger.info(f'Link skipping {output_fpath}')
            return self.output_fpath
        logger.info(f'Linking {output_fpath}')

        command.extend(['-o', output_fpath])
        command.extend([str(a.output_fpath) for a in compiled_files])
        # note: this must this come after the list of object files?
        command.extend(self.flags)

        log_or_dot(logger, 'Link running command: ' + ' '.join(command))
        try:
            run_command(command)
        except Exception as err:
            raise Exception(f"error linking: {err}")

        return self.output_fpath


# todo: this is not a subclass, it is a sibling.
class LinkSharedObject(LinkExe):

    def __init__(self, linker: str, output_fpath: str, flags=None,
                 source: SourceGetter = None, name='link shared object'):
        super().__init__(linker=linker, flags=flags, output_fpath=output_fpath, source=source, name=name)

        ensure_flags = ['-fPIC', '-shared']
        for f in ensure_flags:
            if f not in self.flags:
                self.flags.append(f)
