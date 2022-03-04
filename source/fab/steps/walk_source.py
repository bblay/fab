"""
Gather files from a source folder.

"""
import logging
from typing import Optional, List, Tuple

from fab.build_config import PathFilter
from fab.steps import Step
from fab.util import file_walk

logger = logging.getLogger('fab')


class FindSourceFiles(Step):

    def __init__(self,
                 output_name="all_source",  # todo: artefact output name
                 name="Walk source",
                 file_filtering: Optional[List[Tuple]] = None):

        super().__init__(name)
        self.output_artefact = output_name

        file_filtering = file_filtering or []
        self.path_filters: List[PathFilter] = [PathFilter(*i) for i in file_filtering]

    def run(self, artefacts, config, metrics_send_conn):
        """
        Get all files in the folder and subfolders.

        Requires no artefacts, creates the "all_source" artefact.

        """
        super().run(artefacts, config, metrics_send_conn)

        fpaths = list(file_walk(config.source_root))
        if not fpaths:
            raise RuntimeError(f"no source files found")

        # file filtering
        filtered_fpaths = []
        for fpath in fpaths:

            wanted = True
            for path_filter in self.path_filters:
                # did this filter have anything to say about this file?
                res = path_filter.check(fpath)
                if res is not None:
                    wanted = res

            if wanted:
                filtered_fpaths.append(fpath)
            else:
                logger.debug(f"excluding {fpath}")

        # # create output folders
        # # todo: separate step for folder creation?
        # build_output = config.source_root.parent / BUILD_OUTPUT
        # source_folders = set()
        # for fpath in filtered_fpaths:
        #     source_folders.add(fpath.parent.relative_to(config.source_root))
        # for source_folder in source_folders:
        #     path = build_output / source_folder
        #     path.mkdir(parents=True, exist_ok=True)

        artefacts[self.output_artefact] = filtered_fpaths
