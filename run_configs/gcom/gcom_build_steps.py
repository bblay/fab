from typing import List

from fab.steps import Step
from fab.steps.analyse import Analyse
from fab.steps.archive_objects import ArchiveObjects
from fab.steps.compile_c import CompileC
from fab.steps.compile_fortran import CompileFortran
from fab.steps.grab import GrabFolder
from fab.steps.link_exe import LinkSharedObject
from fab.steps.preprocess import CPreProcessor, FortranPreProcessor
from fab.steps.walk_source import FindSourceFiles


def grab_step():
    # todo: this will be a proper grab step, this is just placeholder
    return GrabFolder(src="/home/h02/bblay/svn/gcom/trunk/build/", dst_name="gcom")


def common_build_steps(fpic=False) -> List[Step]:
    steps: List[Step] = [
        FindSourceFiles(),
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

        *compilers(fpic=fpic),
    ]

    return steps


def compilers(fpic=False) -> List[Step]:
    fpic = ['-fPIC'] if fpic else []

    return [
        CompileC(common_flags=['-c', '-std=c99'] + fpic),
        CompileFortran(
            # compiler=os.path.expanduser(os.getenv('GFORTRAN')),
            compiler='gfortran',
            common_flags=['-c', '-J', '$output'] + fpic),
    ]


def object_archive_step():
    return ArchiveObjects(archiver='ar', output_fpath='$output/libgcom.a')


def link_shared_object_step():
    return LinkSharedObject(linker='mpifort', output_fpath='$output/libgcom.so')
