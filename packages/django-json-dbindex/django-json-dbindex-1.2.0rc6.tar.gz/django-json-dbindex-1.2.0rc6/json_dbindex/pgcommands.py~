# -*- coding: utf-8 -*-
#
# Copyright (c) 2014 Rodolphe Quiédeville <rodolphe@quiedeville.org>
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
from django.utils.importlib import import_module
import json
import sys
import re
import logging
from os import path
from django.db import connection


def index_exists(index):
    """Execute raw sql
    """
    cursor = connection.cursor()
    qry = "SELECT count(indexname) FROM pg_indexes WHERE indexname = %s"
    cursor.execute(qry, [index['name']])
    row = cursor.fetchone()
    cursor.close()
    return row[0] == 1


def drop_index(index):
    """
    Do drop
    """
    try:
        cursor = connection.cursor()
        cursor.execute(index['cmd'])
        cursor.close()
    except:
        pass

