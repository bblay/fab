#!/usr/bin/env python

import logging
import os
import shutil
from pathlib import Path

import fab
from fab.builder import Build
from fab.config import Config
from fab.constants import SOURCE_ROOT
from fab.steps.analyse import Analyse
from fab.steps.archive_objects import ArchiveObjects
from fab.steps.compile_c import CompileC
from fab.steps.compile_fortran import CompileFortran
from fab.steps.link_exe import LinkSharedObject
from fab.steps.preprocess import CPreProcessor, FortranPreProcessor
from fab.steps.walk_source import FindSourceFiles
from fab.util import time_logger


def gcom_object_archive_config(fab_workspace_root=None):
    """
    Create a library for static linking.

    """
    config = Config(label='gcom object archive', fab_workspace_root=fab_workspace_root)

    config.grab_config = {("gcom", "~/svn/gcom/trunk/build"), }

    config.steps = [
        FindSourceFiles(config.workspace / SOURCE_ROOT),  # template?
        CPreProcessor(),
        FortranPreProcessor(
            common_flags=[
                '-traditional-cpp', '-P',
                '-I', '$source/gcom/include',
                '-DGC_VERSION="7.6"',
                '-DGC_BUILD_DATE="20220111"',
                '-DGC_DESCRIP="dummy desrip"',
                '-DPREC_64B', '-DMPILIB_32B',
            ],
        ),
        Analyse(root_symbol=None),  # no program unit, we're not building an exe
        CompileC(common_flags=['-c', '-std=c99']),
        CompileFortran(
            compiler=os.path.expanduser('~/.conda/envs/sci-fab/bin/gfortran'),
            common_flags=['-c', '-J', '$output']
        ),
        ArchiveObjects(archiver='ar', output_fpath='$output/libgcom.a'),
    ]

    return config


def gcom_shared_object_config(fab_workspace_root=None):
    """
    Create a library for dynamic linking.

    """
    from fab.dep_tree import by_type

    static_config = gcom_object_archive_config()

    shared_config = Config(
        label='gcom shared object',
        fab_workspace_root=fab_workspace_root,
        grab_config=static_config.grab_config,
        steps=static_config.steps,
    )

    # compile with fPIC
    fc = list(by_type(shared_config.steps, CompileFortran))[0]  # todo: ugly
    fc.flags.common_flags.append('-fPIC')

    cc = list(by_type(shared_config.steps, CompileC))[0]
    cc.flags.common_flags.append('-fPIC')

    # todo: this is a little hacky as it includes the step to create the static library too
    # link the object archive into a shared object.
    shared_config.steps.append(LinkSharedObject(
        linker=os.path.expanduser('~/.conda/envs/sci-fab/bin/mpifort'),
        output_fpath='$output/libgcom.so'))

    return shared_config


def main():
    logger = logging.getLogger('fab')
    # logger.setLevel(logging.DEBUG)
    logger.setLevel(logging.INFO)

    config = gcom_object_archive_config()

    # ignore this, it's not here :)
    with time_logger("grabbing"):
        grab_will_do_this(config.grab_config, config.workspace)

    #
    configs = [gcom_object_archive_config(), gcom_shared_object_config()]
    for config in configs:
        with time_logger("gcom build"):
            Build(config=config).run()


def grab_will_do_this(src_paths, workspace):
    for label, src_path in src_paths:
        shutil.copytree(
            os.path.expanduser(src_path),
            workspace / SOURCE_ROOT / label,
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns('.svn')
        )


if __name__ == '__main__':
    main()
