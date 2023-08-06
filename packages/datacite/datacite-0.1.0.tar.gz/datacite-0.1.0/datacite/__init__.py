# -*- coding: utf-8 -*-
#
# This file is part of DataCite.
#
# Copyright (C) 2015 CERN.
#
# DataCite is free software; you can redistribute it and/or modify it
# under the terms of the Revised BSD License; see LICENSE file for
# more details.


"""Python API wrapper for the DataCite Metadata Store API."""

from __future__ import absolute_import, unicode_literals, print_function

from .client import DataCiteMDSClient

__all__ = ('DataCiteMDSClient', )
