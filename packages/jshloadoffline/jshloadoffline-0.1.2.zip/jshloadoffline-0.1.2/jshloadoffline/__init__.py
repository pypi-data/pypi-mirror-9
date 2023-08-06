#!/usr/bin/env python
#-*- coding: utf-8 -*-

from __future__ import unicode_literals
import os.path
from path import path


class JshLoadoffline(object):
    def __init__(self, root_dir='', **kwargs):
        self.root_dir = root_dir
        self.customer = kwargs.get('customer')
        self.kind = kwargs.get('kind', 'fvt_wip')
        self.ext = kwargs.get('ext', 'txt')
        self.pattern = '{}_{}.{}'.format(self.customer, self.kind, self.ext)

    def load_data(self, folders=[], kind='year_trend'):
        if kind.endswith('_trend') and not self.customer:
            return 0

        data_folder = self._get_data_folder(folders)
        if not os.path.exists(data_folder):
            return 0

        if kind.endswith('_trend'):
            return self.load_trend_data(data_folder)

        return getattr(self, 'load_{}'.format(kind), data_folder)

    def _get_data_folder(self, names=[]):
        folder = self.root_dir
        for name in names:
            folder = os.path.join(folder, '{}'.format(name))

        return folder

    def load_trend_data(self, folder):
        qty = 0
        d = path(folder)
        for log in d.files(self.pattern):
            with open(log) as f:
                qty += int(f.readline().strip())

        return qty
