import argparse
import importlib
import pathlib
import textwrap
from subprocess import STDOUT, check_call

path = pathlib.Path(__file__).parent.absolute()
dvc = path.parent / "dvc"
pyinstaller = path / "pyinstaller"
innosetup = path / "innosetup"
fpm = path / "fpm"

parser = argparse.ArgumentParser()
parser.add_argument(
    "pkg", choices=["deb", "rpm", "osxpkg", "exe"], help="package type"
)
args = parser.parse_args()

(dvc / "utils" / "build.py").write_text(f'PKG = "{args.pkg}"')

# Autogenerate version, similar to what we do in setup.py
spec = importlib.util.spec_from_file_location(
    "dvc.version", dvc / "version.py"
)
dvc_version = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dvc_version)
version = dvc_version.__version__

(dvc / "version.py").write_text(
    textwrap.dedent(
        f"""\
        # AUTOGENERATED at build time by scripts/build.py
        __version__ = "{version}"
    """
    )
)

check_call(
    ["python", "build.py"], cwd=pyinstaller, stderr=STDOUT,
)

if args.pkg == "exe":
    check_call(
        ["python", "build.py"], cwd=innosetup, stderr=STDOUT,
    )
else:
    check_call(
        ["python", "build.py", args.pkg], cwd=fpm, stderr=STDOUT,
    )
