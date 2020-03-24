import importlib.resources
from pathlib import Path
from typing import Optional

moc_register = {}


def _register_moc(moc_path: Path, name: Optional[str] = None):
    """Add a MOC to the internal register to make them easily accessible.

    Args:
        moc_path: Path to the FITS MOC file.

        name: Name of the survey to use as the key in the register. If None, uses the
            `moc_path` name stripped of all suffixes, e.g. for "/path/to/VAST.MOC.fits",
            "VAST" is used. Defaults to None.
    """
    if name is None:
        name = moc_path.name.split(".")[0]
    moc_register[name] = moc_path


def _register_package_mocs():
    """Register MOC files provided with the package.
    """
    with importlib.resources.path("askap_surveys.data", "moc") as moc_path:
        for moc_file in moc_path.glob("*.fits"):
            _register_moc(moc_file)


_register_package_mocs()
