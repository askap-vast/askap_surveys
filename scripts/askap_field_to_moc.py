import argparse
from askap_surveys.askap import ASKAPSurvey


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--fields", type=str, help="CSV file with list of fields",
    )
    parser.add_argument(
        "--moc", type=str, help="Name for output MOC file", default=None
    )
    parser.add_argument(
        "--reg", type=str, help="Name for output ds9 region file", default=None
    )
    args = parser.parse_args()
    s = ASKAPSurvey(args.fields)
    if args.moc is not None and len(args.moc) > 0:
        s.to_moc(args.moc)
    if args.reg is not None and len(args.reg) > 0:
        s.to_reg(args.reg)


if __name__ == "__main__":
    main()
