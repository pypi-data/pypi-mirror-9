"""
Repeats the last word of the last message in the conversation, and use it in
an annoying “C’est toi le” sentence.

Installation
------------

You only have to load the plugin:

.. code-block:: none

    /load stoi

.. glossary::

    /stoi
        **Usage:** ``/stoi``

"""
from plugin import BasePlugin
import tabs
import string
import xhtml

char_we_dont_want = string.punctuation+' ’„“”…«»'

class Plugin(BasePlugin):
    def init(self):
        for tab_type in (tabs.MucTab, tabs.PrivateTab, tabs.ConversationTab):
            self.api.add_tab_command(tab_type, 'stoi',
                                     handler=self.stoi,
                                     help="Repeats the last word of the last message "
                                          "in the conversation, and use it in an "
                                          "annoying “C’est toi le” sentence.",
                                     short='C’est toi le stoi.')

    def stoi(self, args):
        messages = self.api.get_conversation_messages()
        if not messages:
            # Do nothing if the conversation doesn’t contain any message
            return
        last_message = messages[-1]
        txt = xhtml.clean_text(last_message.txt)
        for char in char_we_dont_want:
            txt = txt.replace(char, ' ')
        if txt.strip():
            last_word = txt.split()[-1]
        else:
            last_word = "vide"
        self.api.send_message("C’est toi le %s." % last_word)
