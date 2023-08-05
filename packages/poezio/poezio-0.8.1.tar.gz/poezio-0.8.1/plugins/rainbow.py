"""
This plugin colors each character of a message with a random color.

Installation
------------

You only have to load the plugin.

.. code-block:: none

    /load rainbow

Usage
-----

.. glossary::

    /rainbow

        Say something in a Chat tab.

.. note:: Can create fun things when used with :ref:`The figlet plugin <figlet-plugin>`.
"""
from plugin import BasePlugin
import xhtml
import random

possible_colors = list(range(256))
# remove the colors that are almost white or almost black
for col in [16, 232, 233, 234, 235, 236, 237, 15, 231, 255, 254, 253, 252, 251]:
    possible_colors.remove(col)

def rand_color():
    return '\x19%s}' % (random.choice(possible_colors),)

class Plugin(BasePlugin):
    def init(self):
        self.api.add_event_handler('muc_say', self.rainbowize)
        self.api.add_event_handler('private_say', self.rainbowize)
        self.api.add_event_handler('conversation_say', self.rainbowize)

    def rainbowize(self, msg, tab):
        msg['body'] = ''.join(['%s%s' % (rand_color(),char,) for char in xhtml.clean_text(msg['body'])])
