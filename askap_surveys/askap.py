import os
import pandas as pd
from mocpy import MOC
from astropy.coordinates import SkyCoord
import astropy.units as u
import numpy as np
import regions


class ASKAPSurvey:
    ASKAP_ROTATION = 45 * u.deg  # may not be an appropriate assumption!
    # full width (diameter)
    WIDTH = 2 * 4.1 * u.deg
    HEIGHT = WIDTH

    def __init__(self, field_list, max_depth=7):
        if not os.path.exists(field_list):
            raise IOError("Cannot find file %s" % field_list)
        self.fields_df = pd.read_csv(field_list)
        self.max_depth = max_depth

        self.region_list = regions.ShapeList()
        self.moc = MOC()
        for _, field in self.fields_df.iterrows():
            center = SkyCoord(ra=field.RA, dec=field.Dec, unit="hourangle,deg")
            sep = np.hypot(self.WIDTH, self.HEIGHT) / 2.0
            self.region_list.append(
                regions.RectangleSkyRegion(
                    center,
                    self.WIDTH,
                    self.HEIGHT,
                    self.ASKAP_ROTATION + (field.Rotation * u.deg),
                )
            )
            self.vertices = SkyCoord(
                [
                    center.directional_offset_by(
                        self.ASKAP_ROTATION + pa + (field.Rotation * u.deg), sep
                    )
                    for pa in [45, 135, 225, 315] * u.deg
                ]
            )
            self.moc = self.moc.union(
                MOC.from_polygon_skycoord(self.vertices, max_depth=self.max_depth)
            )

    def to_moc(self, filename):
        self.moc.write(filename, overwrite=True)

    def to_reg(self, filename):
        regions.write_ds9(self.region_list, filename, coordsys="fk5")
