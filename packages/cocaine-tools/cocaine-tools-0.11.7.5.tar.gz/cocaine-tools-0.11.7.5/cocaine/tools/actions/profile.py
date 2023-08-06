#
# Copyright (c) 2013+ Anton Tyurin <noxiouz@yandex.ru>
# Copyright (c) 2013+ Evgeny Safronov <division494@gmail.com>
# Copyright (c) 2011-2014 Other contributors as noted in the AUTHORS file.
#
# This file is part of Cocaine-tools.
#
# Cocaine is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Cocaine is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

from cocaine.futures import chain
from cocaine.tools import actions
from cocaine.tools.actions import CocaineConfigReader, log
from cocaine.tools.printer import printer
from cocaine.tools.tags import PROFILES_TAGS

__author__ = 'Evgeny Safronov <division494@gmail.com>'


class Specific(actions.Specific):
    def __init__(self, storage, name):
        super(Specific, self).__init__(storage, 'profile', name)


class List(actions.List):
    def __init__(self, storage):
        super(List, self).__init__('profiles', PROFILES_TAGS, storage)


class View(actions.View):
    def __init__(self, storage, name):
        super(View, self).__init__(storage, 'profile', name, 'profiles')


class Upload(Specific):
    def __init__(self, storage, name, profile):
        super(Upload, self).__init__(storage, name)
        self.profile = profile
        if not self.profile:
            raise ValueError('Please specify profile file path')

    @chain.source
    def execute(self):
        with printer('Loading profile'):
            profile = CocaineConfigReader.load(self.profile)
        with printer('Uploading "%s"', self.name):
            yield self.storage.write('profiles', self.name, profile, PROFILES_TAGS)


class Remove(Specific):
    @chain.source
    def execute(self):
        log.info('Removing "%s"... ', self.name)
        yield self.storage.remove('profiles', self.name)
        log.info('OK')
