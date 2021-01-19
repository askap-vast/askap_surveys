"""Traverse the VAST data release directory structure and make a MOC of each image.
Usage:
    create_vast_mocs.py [--options] /path/to/VAST

Options:
    --tiles - process the TILE images
    --combined - process the COMBINED images
    --stokes={IQUV} - process the given Stokes parameter(s). Default: I

"""

import argparse
from itertools import chain
import logging
from pathlib import Path
from typing import List
import warnings

from astropy.io import fits
from astropy.wcs import WCS, FITSFixedWarning
import mocpy
from mpi4py import MPI
import multiprocessing_logging


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)-25s %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
multiprocessing_logging.install_mp_handler()
logger = logging.getLogger(__name__)


def partition_list(_list, n):
    return [_list[i::n] for i in range(n)]


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


def make_moc(image: Path, max_norder, rank):
    logger.debug("rank: %d Opening %s", rank, image)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", FITSFixedWarning)
        hdul = fits.open(image)
        hdu = hdul[0]
        # mocpy doesn't like singleton axes, remove them
        hdu_squeezed = fits.hdu.image.ImageHDU(
            data=hdu.data.squeeze(),
            header=WCS(hdu.header).celestial.to_header(),
        )
        logger.info("rank: %d Creating MOC for %s", rank, image)
        moc = mocpy.MOC.from_fits_image(hdu_squeezed, max_norder=max_norder)
        output_dir = get_moc_output_dir(image)
        output_dir.mkdir(mode=0o770, exist_ok=True)
        output_path = output_dir / image.with_suffix(".moc.fits").name
        moc.write(output_path)
        logger.info("rank: %d Wrote MOC to %s", rank, output_path)
        hdul.close()


if __name__ == "__main__":
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    logger.info("MPI rank: %d size: %d", rank, size)
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
    args = parser.parse_args()

    if rank == 0:

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
        images = list(images)
        logger.info("Input image list contains %d images.", len(images))
        images_split = partition_list(images, size)
    else:
        images_split = None
    images_split = comm.scatter(images_split, root=0)
    logger.info("rank: %d num images: %s", rank, len(images_split))
    for image in images_split:
        logger.info("rank: %d Processing %s", rank, image)
        if not args.dryrun:
            make_moc(image, max_norder=args.max_norder, rank=rank)
