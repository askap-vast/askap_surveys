# askap_surveys
Basic parameters for ASKAP surveys to aid coordination

Requirements (beyond standard):
* [skymapper](https://github.com/pmelchior/skymapper)
* [mocpy](https://cds-astro.github.io/mocpy/)
* [pymangle](https://github.com/esheldon/pymangle)
* [pygsm](https://github.com/telegraphic/PyGSM)
* [healpy](https://healpy.readthedocs.io)

Format for each survey (largely taken from confluence pages like https://confluence.csiro.au/display/askapsst/EMU):

```
Name,RA,Dec,Footprint,Pitch,Rotation,Frequency,Interleaved
EMU_2059-51, 21:00:00.000, -51:07:06.39, closepack36, 0.9, 45.0, 943.491, No
EMU_2034-60, 20:34:17.142, -60:19:18.17, closepack36, 0.9, 45.0, 943.491, No
EMU_2042-55, 20:42:00.000, -55:43:29.41, closepack36, 0.9, 45.0, 943.491, No
EMU_2115-60, 21:15:25.714, -60:19:18.17, closepack36, 0.9, 45.0, 943.491, No
EMU_2132-51, 21:32:43.636, -51:07:06.39, closepack36, 0.9, 45.0, 943.491, No
EMU_2027-51, 20:27:16.363, -51:07:06.39, closepack36, 0.9, 45.0, 943.491, No
EMU_2118-55, 21:18:00.000, -55:43:29.41, closepack36, 0.9, 45.0, 943.491, No
EMU_2154-55, 21:54:00.000, -55:43:29.41, closepack36, 0.9, 45.0, 943.491, No
EMU_2156-60, 21:56:34.285, -60:19:18.17, closepack36, 0.9, 45.0, 943.491, No
EMU_2205-51, 22:05:27.272, -51:07:06.39, closepack36, 0.9, 45.0, 943.491, No
```

Each survey ([DINGO](https://confluence.csiro.au/display/askapsst/DINGO), [EMU](https://confluence.csiro.au/display/askapsst/EMU), [FLASH](https://confluence.csiro.au/display/askapsst/FLASH), [GASKAP](https://confluence.csiro.au/display/askapsst/GASKAP), [POSSUM](https://confluence.csiro.au/display/askapsst/POSSUM), [VAST](https://confluence.csiro.au/display/askapsst/VAST), [WALLABY](https://confluence.csiro.au/display/askapsst/WALLABY)) has a `CSV` file as well as a `MOC`.  The latter can be loaded into [aladin](https://aladin.u-strasbg.fr) as well.

Scripts:
* `askap_field_to_moc.py`: convert a `CSV` file to a `MOC` and a ds9 regions file.  Usage: `python ./askap_field_to_moc.py --fields=VAST.csv --moc=VAST.MOC.fits --reg=VAST.reg`.  **NOTE** this is preliminary and doesn't correctly use frequency/footprint/pitch information.
* `make_sky_coverage_plot_dk.py`: take all of the individual surveys and overplot them on the GSM sky image.  Various parameters can be tweaked (number of surveys shown, colors, ...).


Other surveys:
* FIRST: coverage maps from http://sundog.stsci.edu/first/catalogs/readme.html#coverage
* DES: mangle file from http://www.mpe.mpg.de/~tdwelly/erosita/multiwavelength_coverage/
* SPT: rough parameters read off plot from Story et al. 2013, https://iopscience.iop.org/article/10.1088/0004-637X/779/1/86/pdf
* VPHAS: http://horus.roe.ac.uk/vsa/coverage-maps.html
* VVV: http://horus.roe.ac.uk/vsa/coverage-maps.html
