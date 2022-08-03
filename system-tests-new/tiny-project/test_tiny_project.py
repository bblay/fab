import logging
import shutil
from pathlib import Path

from fab.steps.walk_source import FindSourceFiles

from fab.build_config import BuildConfig
from fab.steps.analyse import Analyse
from fab.steps.compile_fortran import CompileFortran
from fab.steps.grab import GrabFolder
from fab.steps.link_exe import LinkExe
from fab.steps.preprocess import fortran_preprocessor

logger = logging.getLogger('fab')


class TestTinyProject(object):

    def test(self, tmp_path):
        # We want to build in a clean workspace each time the test is run.
        # (Pytest provides the tmp_path fixture.)
        self.fab_workspace = tmp_path
        print(f"fab_workspace is {self.fab_workspace}")

        logger.setLevel(logging.DEBUG)

        self.clean_build()

        self.no_change_rebuild()

        # mod file source changed
        self.incremental_build_src_change()

        # mod file signature changed
        self.incremental_build_sig_change()

    def clean_build(self):
        this_folder = Path(__file__).parent

        config = BuildConfig(
            project_label='tiny project',
            fab_workspace=self.fab_workspace,
            steps=[
                GrabFolder(this_folder / 'project-source', dst='src'),
                FindSourceFiles(),
                fortran_preprocessor(preprocessor='cpp -traditional-cpp -P'),
                Analyse(root_symbol='my_prog'),
                CompileFortran(compiler='gfortran -c', common_flags=['-J', '$output']),
                LinkExe(flags=['-lgfortran']),
            ]
        )

        config.run()

        # check it built ok

        # record the file timestamps

    def no_change_rebuild(self):
        this_folder = Path(__file__).parent

        config = BuildConfig(
            project_label='tiny project',
            fab_workspace=self.fab_workspace,
            steps=[
                GrabFolder(this_folder / 'project-source', dst='src'),
                FindSourceFiles(),
                fortran_preprocessor(preprocessor='cpp -traditional-cpp -P'),
                Analyse(root_symbol='my_prog'),
                CompileFortran(compiler='gfortran -c', common_flags=['-J', '$output']),
                LinkExe(flags=['-lgfortran']),
            ]
        )

        config.run()

        # check it built ok

        # record the file timestamps

    def incremental_build_src_change(self):
        # modify the source
        this_folder = Path(__file__).parent

        config = BuildConfig(
            project_label='tiny project',
            fab_workspace=self.fab_workspace,
            steps=[
                GrabFolder(this_folder / 'project-source', dst='src'),
                FindSourceFiles(),
                fortran_preprocessor(preprocessor='cpp -traditional-cpp -P'),
                Analyse(root_symbol='my_prog'),
                CompileFortran(compiler='gfortran -c', common_flags=['-J', '$output']),
                LinkExe(flags=['-lgfortran']),
            ]
        )

        shutil.copy(this_folder / 'test-files' / 'my_mod-src-change.F90',
                    self.fab_workspace / 'tiny-project' / 'source' / 'src' / 'my_mod.F90')

        config.run()

        # check it built ok

        # record the file timestamps

        # check only the right stuff has changed

    def incremental_build_sig_change(self):
        # modify the source
        this_folder = Path(__file__).parent

        config = BuildConfig(
            project_label='tiny project',
            fab_workspace=self.fab_workspace,
            steps=[
                GrabFolder(this_folder / 'project-source', dst='src'),
                FindSourceFiles(),
                fortran_preprocessor(preprocessor='cpp -traditional-cpp -P'),
                Analyse(root_symbol='my_prog'),
                CompileFortran(compiler='gfortran -c', common_flags=['-J', '$output']),
                LinkExe(flags=['-lgfortran']),
            ]
        )

        shutil.copy(this_folder / 'test-files' / 'my_mod-sig-change.F90',
                    self.fab_workspace / 'tiny-project' / 'source' / 'src' / 'my_mod.F90')

        config.run()

        # check it built ok

        # record the file timestamps

        # check only the right stuff has changed
