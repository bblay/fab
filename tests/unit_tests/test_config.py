from pathlib import Path

from fab.build_config import AddFlags
from fab.constants import SOURCE


class TestAddFlags(object):

    def test_run(self):
        workspace = Path("/workspace")
        add_flags = AddFlags(match="$source/foo/*", flags=['-I', '$relative/include'])

        my_flags = ["-foo"]
        add_flags.run(fpath=Path(f"/workspace/{SOURCE}/foo/bar.c"), input_flags=my_flags, workspace=workspace)
        assert my_flags == ['-foo', '-I', f'/workspace/{SOURCE}/foo/include']

        my_flags = ["-foo"]
        add_flags.run(fpath=Path(f"/workspace/{SOURCE}/bar/bar.c"), input_flags=my_flags, workspace=workspace)
        assert my_flags == ['-foo']
