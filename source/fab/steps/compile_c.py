"""
C file compilation.

"""
import logging
from typing import List

from fab.dep_tree import AnalysedFile

from fab.steps import Step
from fab.tasks import TaskException
from fab.util import CompiledFile, run_command, SourceGetter, Artefact, FilterBuildTree

logger = logging.getLogger('fab')


DEFAULT_SOURCE_GETTER = FilterBuildTree(suffixes=['.c'])


class CompileC(Step):

    # todo: tell the compiler (and other steps) which artefact name to create?
    def __init__(self, compiler: List[str], flags, workspace, source: SourceGetter=None, name="compile c"):
        super().__init__(name)
        self.source_getter = source or DEFAULT_SOURCE_GETTER
        self._compiler = compiler
        self._flags = flags
        self._workspace = workspace

    def run(self, artefacts):
        """
        Compiles all C files in the *build_tree* artefact, creating the *compiled_c* artefact.

        This step uses multiprocessing, unless disabled in the :class:`~fab.steps.Step` class.

        """
        to_compile = self.source_getter(artefacts)
        logger.info(f"compiling {len(to_compile)} c files")

        results = self.run_mp(items=to_compile, func=self._compile_file)

        # any errors?
        errors = [result for result in results if isinstance(result, Exception)]
        if errors:
            err_msg = '\n\n'.join(map(str, errors))
            logger.error(f"There were {len(errors)} errors compiling {len(to_compile)} c files:\n{err_msg}")
            exit(1)

        # results
        compiled_c = [result for result in results if isinstance(result, CompiledFile)]
        logger.info(f"compiled {len(compiled_c)} c files")

        artefacts['compiled_c'] = compiled_c

    def _compile_file(self, analysed_file: AnalysedFile):
        command = [*self._compiler]
        command.extend(self._flags.flags_for_path(analysed_file.fpath))
        command.append(str(analysed_file.fpath))

        output_file = analysed_file.fpath.with_suffix('.o')
        command.extend(['-o', str(output_file)])

        logger.debug('Running command: ' + ' '.join(command))

        try:
            run_command(command)
        except Exception as err:
            return TaskException(f"error compiling {analysed_file.fpath}: {err}")

        return CompiledFile(analysed_file, output_file)
