#   Copyright 2009-2015 Oli Schacher
#
# Licensed under the Apache License, Version 2.0 (the "License");
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
#
#
"""
Example Plugin
"""

from fuglu.shared import ScannerPlugin, DUNNO


class ExamplePlugin(ScannerPlugin):

    """Copy this to make a new plugin"""

    def __init__(self, config, section=None):
        ScannerPlugin.__init__(self, config, section)
        self.requiredvars = {
            'greeting': {
                'default': 'hello world!',
                'description': 'greeting the plugin should log to the console',
            }
        }
        # DO NOT call self.config.get .. here!

    def __str__(self):
        return "Example"

    def examine(self, suspect):
        # config Example
        greeting = self.config.get(self.section, 'greeting')

        # debug info is helpful when the message is run through fuglu_debug
        suspect.debug("Greeting: %s" % greeting)

        # log example
        self._logger().info("%s greets %s: %s" %
                            (suspect.from_address, suspect.to_address, greeting))

        # header access example
        msgrep = suspect.get_message_rep()
        if msgrep.has_key("From"):
            self._logger().info("Message from: %s" % msgrep['From'])
        else:
            self._logger().warning("Message has no 'From' header!")

        return DUNNO
