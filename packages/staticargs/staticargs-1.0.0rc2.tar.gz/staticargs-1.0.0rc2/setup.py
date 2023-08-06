from setuptools import setup, find_packages
from codecs import open
import os

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "version"), "r") as version_handle:
    version = version_handle.read().strip()

setup(
	name = "staticargs",
	version = version,
	description = "Work around mutable default arguments in function definitions",
	url = "https://github.com/HurricaneLabs/staticargs",
	author = "Colton Leekley-Winslow",
	author_email = "colton@hurricanelabs.com",
	package_dir = {"":"src"},
	packages = find_packages("src"),
)

