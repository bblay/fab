#
# cli equivalent:
#   fab ~/svn/um/trunk/src um.config -w ~/git/fab/tmp-workspace-um --stop-on-error -vv
#
# optionally (default):
#   --nprocs 2
#
# cli also needs um.config:
#     [settings]
#     target = um
#     exec-name = um
#
#     [flags]
#     fpp-flags =
#     fc-flags =
#     ld-flags =
#

import os
import logging
import shutil
import sys
from collections import namedtuple

from pathlib import Path

from config_sketch import PathFlags, FlagsConfig, PathFilter
from fab.constants import SOURCE_ROOT, OUTPUT_ROOT

from fab.builder import Fab, read_config
from fab.util import file_walk, time_logger


ConfigSketch = namedtuple(
    'ConfigSketch',
    ['project_name', 'grab_config', 'extract_config', 'cpp_flag_config', 'fpp_flag_config', 'fc_flag_config']
)


# hierarchy of config
#
# site (sys admin)
# project (source code)
# overrides
# blocked overrides
#
# what ought to inherit from env
# num cores in submit script, mem
# batch manager assigns resources
# project board in about amonth


def um_atmos_safe_config():

    # todo: docstring about relative and absolute (=output) include paths
    #       this is quite tightly coupled to the preprocessor

    # grab
    grab_config = {
        os.path.expanduser("~/svn/um/trunk/src"): "um",
        os.path.expanduser("~/svn/jules/trunk/src"): "jules",
        os.path.expanduser("~/svn/socrates/trunk/src"): "socrates",
        os.path.expanduser("~/svn/gcom/trunk/build"): "gcom",
    }

    # extract
    extract_config = [
        PathFilter(['src/atmosphere/convection/comorph/interface/standalone/'], include=False),

        PathFilter(['socrates/'], include=False),
        PathFilter(['socrates/nlte', '/socrates/radiance_core'], include=True),

        PathFilter(['src/scm/'], include=False),
        PathFilter(['src/scm/stub', 'src/scm/modules/s_scmop_mod.F90', 'src/scm/modules/s_scmop_mod.F90'], include=True),

        PathFilter(['jules/control/standalone/'], include=False),
    ]

    # fpp
    cpp_flag_config = FlagsConfig(
        # todo: bundle (some of) these with the 'cpp' definintion?
        path_flags=[
            PathFlags(path_filter="tmp-workspace/um/output/um",
                      add=['-I', '/um/include/other', '-I', '/shumlib/common/src', '-I', '/shumlib/shum_thread_utils/src']),
            PathFlags(path_filter="tmp-workspace/um/output/shumlib",
                      add=['-I', '/shumlib/common/src', '-I', '/shumlib/shum_thread_utils/src']),
        ])

    fpp_flag_config = FlagsConfig(
        # todo: bundle (some of) these with the 'cpp' definintion?
        path_flags=[
            PathFlags(path_filter="tmp-workspace/um/output/jules", add=['-DUM_JULES']),
            PathFlags(path_filter="tmp-workspace/um/output/gcom", add=['-I', '/gcom/include']),
            PathFlags(path_filter="tmp-workspace/um/output/um", add=['-I', 'include']),
        ])

    # todo: bundle these with the gfortran definition
    fc_flag_config = FlagsConfig()

    return ConfigSketch(
        project_name='um',
        grab_config=grab_config,
        extract_config=extract_config,
        cpp_flag_config=cpp_flag_config,
        fpp_flag_config=fpp_flag_config,
        fc_flag_config=fc_flag_config,
    )


def main():

    logger = logging.getLogger('fab')
    logger.addHandler(logging.StreamHandler(sys.stderr))

    # config
    config_sketch = um_atmos_safe_config()
    workspace = Path(os.path.dirname(__file__)) / "tmp-workspace" / config_sketch.project_name

    # Get source repos
    # with time_logger("grabbing"):
    #     grab_will_do_this(config_sketch.grab_config, workspace)

    # Extract the files we want to build
    with time_logger("extracting"):
        extract_will_do_this(config_sketch.extract_config, workspace)


    # fab build stuff
    config = read_config("um.config")
    settings = config['settings']
    # flags = config['flags']

    my_fab = Fab(
        # fab behaviour
        n_procs=3,
        stop_on_error=True,
        # use_multiprocessing=False,
        debug_skip=True,
        # dump_source_tree=True

        # build config
        workspace=workspace,
        target=settings['target'],
        exec_name=settings['exec-name'],
        cpp_flags=config_sketch.cpp_flag_config,
        fpp_flags=config_sketch.fpp_flag_config,
        fc_flags=config_sketch.fc_flag_config,
        ld_flags="",
        skip_files=config.skip_files,
        unreferenced_deps=config.unreferenced_deps,
        # include_paths=config.include_paths,  # todo: not clear if for pp or comp
     )

    logger = logging.getLogger('fab')
    logger.setLevel(logging.DEBUG)
    # logger.setLevel(logging.INFO)

    with time_logger("fab run"):
        my_fab.run()


def grab_will_do_this(src_paths, workspace):  #, logger):
    #logger.info("faking grab")
    for src_path, label in src_paths.items():
        shutil.copytree(src_path, workspace / SOURCE_ROOT / label, dirs_exist_ok=True)

    # todo: move into config
    # shum partial
    shum_excl = ["common/src/shumlib_version.c", "Makefile"]
    shum_incl = [
        "shum_wgdos_packing/src",
        "shum_string_conv/src",
        "shum_latlon_eq_grids/src",
        "shum_horizontal_field_interp/src",
        "shum_spiral_search/src",
        "shum_constants/src",
        "shum_thread_utils/src",
        "shum_data_conv/src",
        "shum_number_tools/src",
        "shum_byteswap/src",
        "common/src",
    ]
    shum_src = Path(os.path.expanduser("~/svn/shumlib/trunk"))
    for fpath in file_walk(shum_src):
        if any([i in str(fpath) for i in shum_excl]):
            continue
        if any([i in str(fpath) for i in shum_incl]):
            rel_path = fpath.relative_to(shum_src)
            output_fpath = workspace / SOURCE_ROOT / "shumlib" / rel_path
            if not output_fpath.parent.exists():
                output_fpath.parent.mkdir(parents=True)
            shutil.copy(fpath, output_fpath)


def extract_will_do_this(path_filters, workspace):
    source_folder = workspace / SOURCE_ROOT
    output_folder = workspace / OUTPUT_ROOT

    for fpath in file_walk(source_folder):

        include = True
        for path_filter in path_filters:
            res = path_filter.check(fpath)
            if res is not None:
                include = res

        # copy it to the build folder?
        if include:
            rel_path = fpath.relative_to(source_folder)
            dest_path = output_folder / rel_path
            # make sure the folder exists
            if not dest_path.parent.exists():
                os.makedirs(dest_path.parent)
            shutil.copy(fpath, dest_path)

        # else:
        #     print("excluding", fpath)


if __name__ == '__main__':
    main()
