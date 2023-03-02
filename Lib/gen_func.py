#!/bin/env python

__author__ = "Mariem Kammoun"
__copyright__ = "Copyright (c) 2023 STMicroelectronics."
__version__ = "0.0.1"
__email__ = "mariem.kammoun@actia-engineering.tn"

"""
Package License
"""

import os
import argparse
import pathlib
import chardet
import sys
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
from io import StringIO
from simple_file_checksum import get_checksum

# List all files in a directory using os.listdir
def list_all_files_in_directory(directory_path):
    files = []
    for entry in os.listdir(directory_path):
        if os.path.isfile(os.path.join(directory_path, entry)):
            files.append(entry)
    return files


#check the presence of the two package license files in the directory:
def files_presence_in_directory(directory_path, list_pkg):
    files_list = list_all_files_in_directory(directory_path)
    print(files_list)
    dic= {}
    for i in list_pkg:
        if i in files_list:
            dic.update({i : "exist"})
        else:
            dic.update({i : "not exist"})
    return dic


def skeleton_qa_table ():
    header = ["Check", "Status", "Error Log"]
    rows = []
    for i in range(11):
    # In each iteration, add an empty list to the main list
        rows.append([])

    return header, rows
