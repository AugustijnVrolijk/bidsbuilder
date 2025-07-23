from setuptools import setup, find_packages


setup(
    name="bidsbuilder",
    version="0.1.0",
    packages=find_packages(where=r"/src"),
    install_requires=["attrs>=25.3.0",
            "bidsschematools>=1.0.4",
            "mne>=1.9.0",
            "pandas>=2.2.3",
            "setuptools>=72.1.0",
            "typing_extensions>=4.13.2"],
)