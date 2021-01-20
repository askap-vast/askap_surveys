"""Traverse the VAST data release directory structure and make a MOC of each image.
Usage:
    create_vast_mocs.py [--options] /path/to/VAST

Options:
    --tiles - process the TILE images
    --combined - process the COMBINED images
    --stokes={IQUV} - process the given Stokes parameter(s). Default: I

"""

import argparse
from functools import partial
from itertools import chain
import logging
import multiprocessing
from pathlib import Path
from typing import List
import warnings

from astropy.io import fits
from astropy.wcs import WCS, FITSFixedWarning
import mocpy
import multiprocessing_logging


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)-25s %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
multiprocessing_logging.install_mp_handler()
logger = logging.getLogger(__name__)


def stokes_type(stokes_str: str) -> List[str]:
    STOKES_PARAMS = ("I", "Q", "U", "V")
    stokes_str = stokes_str.upper()
    for char in stokes_str:
        if char not in STOKES_PARAMS:
            raise ValueError(
                f"Stokes parameter must be one of {''.join(STOKES_PARAMS)}"
            )
    return [char for char in stokes_str]


def get_moc_output_dir(image_path: Path) -> Path:
    output_dir_name = image_path.parent.name.replace("IMAGES", "MOCS")
    return image_path.parent.parent / output_dir_name


def make_moc(image: Path, overwrite=False):
    output_dir = get_moc_output_dir(image)
    output_dir.mkdir(mode=0o770, exist_ok=True)
    output_path = output_dir / image.with_suffix(".moc.fits").name
    if (output_path.exists() and overwrite) or not output_path.exists():
        logger.debug("Opening %s", image)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", FITSFixedWarning)
            hdul = fits.open(image)
            hdu = hdul[0]
            # mocpy doesn't like singleton axes, remove them
            hdu_squeezed = fits.hdu.image.ImageHDU(
                data=hdu.data.squeeze(),
                header=WCS(hdu.header).celestial.to_header(),
            )
            logger.info("Creating MOC for %s", image)
            moc = mocpy.MOC.from_fits_image(hdu_squeezed, max_norder=args.max_norder)
            moc.write(output_path, overwrite=overwrite)
            logger.info("Wrote MOC to %s", output_path)
            hdul.close()
    else:
        logger.info("Skipping %s", image)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "vast_data_dir",
        type=Path,
        help="VAST data release root directory that contains the EPOCH directories.",
    )
    parser.add_argument("--tiles", action="store_true", help="Process the TILE images.")
    parser.add_argument(
        "--combined", action="store_true", help="Process the COMBINED images."
    )
    parser.add_argument(
        "--stokes",
        type=stokes_type,
        default="I",
        help=(
            "Process the given Stokes parameter images. Allowed values: I, Q, U, V. "
            "Multiple parameters may be specified, e.g. --stokes=IV. Case-insensitive."
        ),
    )
    parser.add_argument(
        "--max-norder",
        type=int,
        default=10,
        help="Max order of output MOC. Larger numbers mean higher resolution.",
    )
    parser.add_argument(
        "--nworkers",
        type=int,
        default=1,
        help="Number of multiprocessing workers to spawn.",
    )
    parser.add_argument(
        "--dryrun",
        action="store_true",
        help=(
            "Don't create MOCs, only collect images and report the number that would be "
            "processed."
        ),
    )
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing MOCs.")

    args = parser.parse_args()

    vast_data_dir: Path = args.vast_data_dir
    images: chain = chain()
    logger.info("Building input image list ...")
    for stokes in args.stokes:
        if args.tiles:
            logger.info("Adding Stokes %s TILE images ...", stokes)
            images = chain(
                images,
                vast_data_dir.glob(
                    f"EPOCH*/TILES/STOKES{stokes}_IMAGES/image.{stokes.lower()}.*.restored.fits"
                ),
            )
        if args.combined:
            logger.info("Adding Stokes %s COMBINED images ...", stokes)
            images = chain(
                images,
                vast_data_dir.glob(
                    f"EPOCH*/COMBINED/STOKES{stokes}_IMAGES/*.{stokes}.fits"
                ),
            )
    logger.info("Finished building input image list.")
    if args.dryrun:
        logger.info("Would create %d MOCs.", len(list(images)))
    else:
        logger.debug("Creating multiprocessing pool with %d workers.", args.nworkers)
        pool = multiprocessing.Pool(processes=args.nworkers)
        pool.map(partial(make_moc, overwrite=args.overwrite), images)
        pool.close()
