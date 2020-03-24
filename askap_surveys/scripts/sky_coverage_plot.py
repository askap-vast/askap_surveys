#!/usr/bin/env python
import seaborn as sns
import skymapper
from askap_surveys import moc_register
from askap_surveys.plotting import FITSMOCSurvey, ASKAPSurveyMap


def main():
    # vast_fields = [FITSMOCSurvey(f"VAST_FIELD{i}.MOC.fits") for i in range(1, 7)]
    cnss = FITSMOCSurvey(moc_register["CNSS"])
    first = FITSMOCSurvey(moc_register["FIRST"])
    spt = FITSMOCSurvey(moc_register["SPT"])
    emu = FITSMOCSurvey(moc_register["EMU"])
    vphas = FITSMOCSurvey(moc_register["VPHAS-DR3"])
    vvv = FITSMOCSurvey(moc_register["VVV-DR5"])
    vast = FITSMOCSurvey(moc_register["VAST"])
    wallaby = FITSMOCSurvey(moc_register["WALLABY"])
    dingo = FITSMOCSurvey(moc_register["DINGO"])
    flash = FITSMOCSurvey(moc_register["FLASH"])
    gaskap = FITSMOCSurvey(moc_register["GASKAP"])
    possum = FITSMOCSurvey(moc_register["POSSUM"])
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
