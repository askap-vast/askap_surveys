import warnings
import skymapper
from mocpy import MOC
import healpy
import astropy.units as u
from astropy.coordinates import SkyCoord
from astropy.io import fits
import matplotlib
from cycler import cycler
import numpy as np
import pygsm


class FITSMOCSurvey(skymapper.survey.Survey):
    def __init__(self, moc_fits: fits.HDUList, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.moc = MOC.from_fits(moc_fits)

    def contains(self, ra, dec):
        return self.moc.contains(ra * u.deg, dec * u.deg)


class ASKAPSurveyMap:
    def __init__(
        self,
        freq=888,
        plot_hpx_order=7,
        gridsep=30,
        cmap=matplotlib.pyplot.get_cmap("Dark2"),
        projection="Mollweide",
        **kwargs,
    ):
        if projection not in skymapper.projection_register.keys():
            raise ValueError(f"Projection {projection} not valid for skymapper")
        self.freq = freq
        self.plot_hpx_order = plot_hpx_order
        self.gridsep = gridsep
        if isinstance(cmap, matplotlib.colors.ListedColormap):
            self.cmap = cmap.colors
        else:
            self.cmap = cmap

        # make the background map
        nside = 512  # pygsm outputs nside=512
        npix = healpy.nside2npix(nside)
        ra, dec = healpy.pix2ang(nside, np.arange(npix), lonlat=True)
        coords = SkyCoord(ra, dec, unit="deg")
        gsm = pygsm.GlobalSkyModel()

        # this is in Galactic coords - convert back to equatorial
        bg_gsm = gsm.generate(self.freq)
        coords_gal = coords.galactic
        bg_gsm_equatorial = healpy.pixelfunc.get_interp_val(
            bg_gsm, coords_gal.l.value, coords_gal.b.value, lonlat=True
        )
        bg_gsm_equatorial_o7 = healpy.ud_grade(
            bg_gsm_equatorial, 2 ** self.plot_hpx_order
        )  # degrade the resolution

        # self.projection = skymapper.Mollweide(lon_0=RA0)
        self.projection = getattr(skymapper, projection)(**kwargs)
        self.ax = skymapper.Map(self.projection, interactive=False)
        self.ax.grid(sep=self.gridsep)
        self.nside = 2 ** self.plot_hpx_order
        self.color_cycle = cycler(facecolors=self.cmap)
        self.color_cycle_it = iter(self.color_cycle)

        # and plot the background map
        self.ax.healpix(
            bg_gsm_equatorial_o7,
            color_percentiles=[0, 99],
            cmap="Greys",
            norm=matplotlib.colors.LogNorm(),
        )

        self.plotted_surveys = []
        self.labels = []

    def add_survey(
        self, survey, label, alpha=0.5, color=None, edgealpha=None, edgemarkersize=1
    ):
        if color is None:
            color = next(self.color_cycle_it)
        else:
            color = {"facecolors": color}
        self.plotted_surveys.append(
            self.ax.footprint(
                survey,
                self.nside,
                alpha=alpha,
                label=label,
                edgecolors=color["facecolors"],
                facecolors=color["facecolors"],
            )
        )
        # need to manually set the edgecolors of the footprint PolyCollections as skymapper
        # sets these to "face". This seems supposed by mpl but something goes wrong when
        # creating the legend. My guess is "face" gets decoded in .get_edgecolors()
        # but this may not get called in during the legend creation.
        self.plotted_surveys[-1].set_edgecolors(
            self.plotted_surveys[-1].get_edgecolors()
        )  # get around a skymapper bug (see below)
        self.labels.append(label)

        if edgealpha is not None and hasattr(survey, "moc"):
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=DeprecationWarning)
            boundaries = survey.moc.get_boundaries(order=self.plot_hpx_order)
            for coords in boundaries:
                # draw as points as the line isn't very clever and draws across the map
                # when crossing the antimeridian
                _ = self.ax.plot(
                    coords.ra.deg,
                    coords.dec.deg,
                    ".",
                    color=self.plotted_surveys[-1].get_edgecolors()[0],
                    markersize=edgemarkersize,
                    alpha=edgealpha,
                )

    def add_legend(self, handles=None, labels=None, ncolmax=5):
        # get total list of handles and labels
        all_handles = self.plotted_surveys
        # add in any additional handles and labels if specified
        if handles is not None and len(handles) > 0:
            all_handles += handles
        all_labels = self.labels
        if labels is not None and len(labels) > 0:
            all_labels += labels

        ncol = min(len(all_handles), ncolmax)

        self.legend = self.ax.fig.legend(
            all_handles,
            all_labels,
            loc="lower center",
            # x0, y0, width, height
            bbox_to_anchor=(0.0, 0.7, 0.95, 1.0),
            ncol=ncol,
            mode="expand",
        )

    def save(self, filename, dpi=150):
        self.ax.fig.savefig(
            filename,
            dpi=dpi,
            bbox_inches=matplotlib.transforms.Bbox.from_bounds(0, 0.5, 6.0, 4.2),
        )
