# Copyright Modal Labs 2022
# Copyright (c) Modal Labs 2022

import ast
import datetime
import importlib
import os
import pkgutil
import re
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import List, Optional

import requests
from invoke import task
from rich.console import Console
from rich.table import Table

year = datetime.date.today().year
copyright_header_start = "# Copyright Modal Labs"
copyright_header_full = f"{copyright_header_start} {year}"
