#!/usr/bin/env python
import logging
import os

from fab.build_config import BuildConfig, AddFlags
from fab.steps.analyse import Analyse
from fab.steps.compile_c import CompileC
from fab.steps.compile_fortran import CompileFortran
# from fab.steps.grab import GrabFolder
from fab.steps.grab import GrabSvn
from fab.steps.link_exe import LinkExe
from fab.steps.preprocess import CPreProcessor, FortranPreProcessor
from fab.steps.root_inc_files import RootIncFiles
from fab.steps.walk_source import FindSourceFiles


def jules_config():
    config = BuildConfig(label='Jules Build')
    # config.multiprocessing = False
    # config.debug_skip = True

    # log this env var, which is important for mpifort
    logger = logging.getLogger('fab')
    logger.info(f"OMPI_FC is {os.environ.get('OMPI_FC') or 'not defined'}")

    # A big list of symbols which are used in jules without a use statement.
    # Fab doesn't automatically identify such dependencies, and so they must be specified here by the user.
    unreferenced_dependencies = [
        'sunny', 'solpos', 'solang', 'redis', 'init_time', 'init_irrigation', 'init_urban', 'init_fire', 'init_drive',
        'init_imogen', 'init_prescribed_data', 'init_vars_tmp', 'imogen_check', 'imogen_update_clim', 'control',
        'imogen_update_carb', 'next_time', 'sow', 'emerge', 'develop', 'partition', 'radf_co2', 'radf_non_co2',
        'adf_ch4gcm_anlg', 'drdat', 'clim_calc', 'diffcarb_land_co2', 'ocean_co2', 'diffcarb_land_ch4',
        'diff_atmos_ch4', 'day_calc', 'response', 'radf_ch4', 'gcm_anlg', 'delta_temp', 'rndm', 'invert', 'vgrav',
        'conversions_mod', 'water_constants_mod', 'planet_constants_mod', 'veg_param_mod', 'flake_interface']

    # allow_mismatch_flags = [('*/io/dump/read_dump_mod.f90', ['-fallow-argument-mismatch']),]

    # revision = "21398"  # this one compiles
    revision = "r22411"  # release 6.3, feb 28 2022
    config.steps = [

        # GrabFolder(src='~/svn/jules/trunk/src/', dst_label='src'),
        # GrabFolder(src='~/svn/jules/trunk/utils/', dst_label='util'),
        GrabSvn(src='https://code.metoffice.gov.uk/svn/jules/main/trunk/src/', dst_label='src', revision=revision),
        GrabSvn(src='https://code.metoffice.gov.uk/svn/jules/main/trunk/utils/', dst_label='utils', revision=revision),

        FindSourceFiles(file_filtering=[
            (['src/control/um/'], False),
            (['src/initialisation/um/'], False),
            (['src/control/rivers-standalone/'], False),
            (['src/initialisation/rivers-standalone/'], False),
            (['src/params/shared/cable_maths_constants_mod.F90'], False)]),

        RootIncFiles(),

        CPreProcessor(),

        FortranPreProcessor(
            preprocessor='cpp',
            common_flags=['-traditional-cpp', '-P', '-DMPI_DUMMY', '-DNCDF_DUMMY', '-I', '$output']),

        Analyse(root_symbol='jules', unreferenced_deps=unreferenced_dependencies),

        CompileC(),

        CompileFortran(
            compiler='gfortran',
            common_flags=['-c', '-J', '$output'],
            path_flags=[
                AddFlags('*/io/dump/read_dump_mod.f90', ['-fallow-argument-mismatch'])
            ]),

        LinkExe(
            linker='mpifort',
            output_fpath='$output/jules.exe',
            flags=['-lm']),
    ]

    return config


def main():
    # logging.getLogger('fab').setLevel(logging.DEBUG)
    jules_config().run()


if __name__ == '__main__':
    main()
