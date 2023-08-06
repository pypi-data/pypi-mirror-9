#!/usr/bin/env python

from distutils.core import setup
import sys


with open('VERSION') as f:
    version_tag = f.read().strip()
with open("COPYING") as f:
    license = f.read()
with open("README") as f:
    long_description = f.read()

setup(
    name             = "nepi",
    version          = version_tag,
    description      = "Network Experiment Management Framework",
    long_description = long_description,
    license          = license,
    author           = "Alina Quereilhac",
    author_email     = "alina.quereilhac@inria.fr",
    download_url     = "http://build.onelab.eu/nepi/nepi-{v}.tar.gz".format(v=version_tag),
    url              = "http://nepi.inria.fr/",
    platforms        = "Linux, OSX",
    package_dir      = {"": "src"},
    packages         = [
        "nepi",
        "nepi.execution",
        "nepi.resources",
        "nepi.resources.all",
        "nepi.resources.linux",
        "nepi.resources.linux.ccn",
        "nepi.resources.linux.ns3",
        "nepi.resources.linux.ns3.ccn",
        "nepi.resources.linux.netns",
        "nepi.resources.netns",
        "nepi.resources.ns3",
        "nepi.resources.ns3.classes",
        "nepi.resources.omf",
        "nepi.resources.planetlab",
        "nepi.resources.planetlab.ns3",
        "nepi.resources.planetlab.openvswitch",
        "nepi.util",
        "nepi.util.parsers",
        "nepi.data",
        "nepi.data.processing",
        "nepi.data.processing.ccn",
        "nepi.data.processing.ping"],
    package_data     = {
        "nepi.resources.planetlab" : [ "scripts/*.py" ],
        "nepi.resources.linux" : [ "scripts/*.py" ],
        "nepi.resources.linux.ns3" : [ "dependencies/*.tar.gz" ]
    }
)
