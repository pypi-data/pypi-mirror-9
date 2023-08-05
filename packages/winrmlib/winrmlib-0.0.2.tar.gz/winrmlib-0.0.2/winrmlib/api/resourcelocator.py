# (c) 2015, Ian Clegg <ian.clegg@sourcewarp.com>
#
# winrmlib is licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
__author__ = 'ian.clegg@sourcewarp.com'

class ResourceLocator(object):
    """
    Resource Locator
    TO DO, constructor should accept a dictionary of options and a dictionary of list for selectors
    """

    def __init__(self, url):
        self.url = url
        self.options = {}
        self.selectors = {}

    def add_option(self, name, value, must_comply):
        self.options[name] = [value, must_comply]

    def clear_options(self):
        self.options = {}

    def add_selector(self, name, value):
        self.selectors[name] = value

    def clear_selectors(self):
        self.selectors = {}