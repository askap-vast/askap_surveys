from setuptools import setup, find_packages

setup(
    name="askap_surveys",
    version="0.1.1",
    description="Repository of ASKAP survey footprints and other relevant surveys.",
    author="David Kaplan, Andrew O'Brien",
    author_email="kaplan@uwm.edu",
    url="",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "sky_coverage_plot=askap_surveys.scripts.sky_coverage_plot:main",
            "askap_field_to_moc=askap_surveys.scripts.askap_field_to_moc:main",
            "create_vast_mocs=askap_surveys.scripts.create_vast_mocs:main",
        ],
    },
    python_requires=">=3.7",
    include_package_data=True,
    zip_safe=False,
)
