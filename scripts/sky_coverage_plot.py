#!/usr/bin/env python
import importlib.resources
import seaborn as sns
import skymapper
from askap_surveys.plotting import FITSMOCSurvey, ASKAPSurveyMap


def main():
    with importlib.resources.path("askap_surveys.data", "moc") as moc_path:
        # vast_fields = [FITSMOCSurvey(f"VAST_FIELD{i}.MOC.fits") for i in range(1, 7)]
        cnss = FITSMOCSurvey(moc_path / "CNSS.MOC.fits")
        first = FITSMOCSurvey(moc_path / "FIRST.MOC.fits")
        spt = FITSMOCSurvey(moc_path / "SPT.MOC.fits")
        emu = FITSMOCSurvey(moc_path / "EMU.MOC.fits")
        vphas = FITSMOCSurvey(moc_path / "vphas-DR3-AllBands-hires.fits")
        vvv = FITSMOCSurvey(moc_path / "VVV-DR5.MOC.fits")
        vast = FITSMOCSurvey(moc_path / "VAST.MOC.fits")
        wallaby = FITSMOCSurvey(moc_path / "WALLABY.MOC.fits")
        dingo = FITSMOCSurvey(moc_path / "DINGO.MOC.fits")
        flash = FITSMOCSurvey(moc_path / "FLASH.MOC.fits")
        gaskap = FITSMOCSurvey(moc_path / "GASKAP.MOC.fits")
        possum = FITSMOCSurvey(moc_path / "POSSUM.MOC.fits")
    des = skymapper.survey.DES()

    p = ASKAPSurveyMap(cmap=sns.color_palette("husl", 13), lon_0=0)
    p.add_survey(first, "FIRST", 0.2)
    p.add_survey(des, "DES", 0.3, edgealpha=0.5)
    p.add_survey(cnss, "CNSS", 0.75)
    p.add_survey(spt, "SPT", 0.2, edgealpha=0.5)
    p.add_survey(vphas, "VPHAS", 0.25)
    p.add_survey(vvv, "VVV", 0.2)

    p.add_survey(emu, "EMU", 0.5)
    p.add_survey(vast, "VAST", 0.125, edgealpha=0.5)
    p.add_survey(wallaby, "WALLABY", 0.5)
    p.add_survey(dingo, "DINGO", 0.5)
    p.add_survey(flash, "FLASH", 0.5)
    p.add_survey(gaskap, "GASKAP", 0.75, edgealpha=1.0)
    p.add_survey(possum, "POSSUM", 0.5)

    p.add_legend()

    p.save("test.pdf")


if __name__ == "__main__":
    main()
