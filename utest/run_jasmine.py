#!/usr/bin/env python

import os
import shutil
from glob import glob
from io import BytesIO
from os.path import abspath, dirname, exists, join
from subprocess import call
from urllib.request import urlopen
from zipfile import ZipFile

JASMINE_REPORTER_URL = "https://github.com/larrymyers/jasmine-reporters/zipball/0.2.1"
BASE = abspath(dirname(__file__))
REPORT_DIR = join(BASE, "jasmine-results")
EXT_LIB = join(BASE, "..", "ext-lib")
JARDIR = join(EXT_LIB, "jasmine-reporters", "ext")


def run_tests():
    workdir = os.getcwd()
    os.chdir(BASE)
    download_jasmine_reporters()
    clear_reports()
    run()
    os.chdir(workdir)


def run():
    cmd = [
        "java",
        "-cp",
        os.pathsep.join([join(JARDIR, "js.jar"), join(JARDIR, "jline.jar")]),
        "org.mozilla.javascript.tools.shell.Main",
        "-opt",
        "-1",
        "envjs.bootstrap.js",
        join(BASE, "webcontent", "SpecRunner.html"),
    ]
    call(cmd)


def clear_reports():
    if exists(REPORT_DIR):
        shutil.rmtree(REPORT_DIR)
    os.mkdir(REPORT_DIR)


def download_jasmine_reporters():
    if exists(join(EXT_LIB, "jasmine-reporters")):
        return
    if not exists(EXT_LIB):
        os.mkdir(EXT_LIB)
    reporter = urlopen(JASMINE_REPORTER_URL)
    z = ZipFile(BytesIO(reporter.read()))
    z.extractall(EXT_LIB)
    extraction_dir = glob(join(EXT_LIB, "larrymyers-jasmine-reporters*"))[0]
    print("Extracting Jasmine-Reporters to", extraction_dir)
    shutil.move(extraction_dir, join(EXT_LIB, "jasmine-reporters"))


if __name__ == "__main__":
    run_tests()
