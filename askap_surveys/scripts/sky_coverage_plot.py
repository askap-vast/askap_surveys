#!/usr/bin/env python
import seaborn as sns
import skymapper
from askap_surveys import moc_register
from askap_surveys.plotting import FITSMOCSurvey, ASKAPSurveyMap

import argparse

def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '-o',
        '--out',
        default="test.pdf",
        type=str,
        help="Output name for plot",
        )
    parser.add_argument(
        '--askaponly',
        action="store_true",
        help="Only include the ASKAP surveys",
        )
    parser.add_argument(
        '-p','--projection',
        choices=skymapper.projection_register.keys(),
        help="Projection type",
        default="Mollweide",
        )
    parser.add_argument(
        '-m','--map_options',
        nargs='*',
        help="Additional map projection arguments as key=value pairs (e.g., 'lon_0=180', ...).  See https://github.com/pmelchior/skymapper/blob/master/skymapper/projection.py",
        )
    

    args = parser.parse_args()

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

    map_options={}
    for i in args.map_options:
        k,v=i.split('=')
        map_options[k.strip()]=float(v)

    p = ASKAPSurveyMap(cmap=sns.color_palette("husl", 13),
                       projection=args.projection,
                       **map_options,
                       )
    if not args.askaponly:
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

    p.save(args.out)
    print("Wrote output to '%s'" % args.out)

if __name__ == "__main__":
    main()
