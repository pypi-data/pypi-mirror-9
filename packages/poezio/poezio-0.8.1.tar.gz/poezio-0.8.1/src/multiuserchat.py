# Copyright 2010-2011 Florent Le Coz <louiz@louiz.org>
#
# This file is part of Poezio.
#
# Poezio is free software: you can redistribute it and/or modify
# it under the terms of the zlib license. See the COPYING file.

"""
Implementation of the XEP-0045: Multi-User Chat.
Add some facilities that are not available on the XEP_0045
sleek plugin
"""

from xml.etree import cElementTree as ET

from common import safeJID
import logging
log = logging.getLogger(__name__)

NS_MUC_ADMIN = 'http://jabber.org/protocol/muc#admin'

def send_private_message(xmpp, jid, line):
    """
    Send a private message
    """
    jid = safeJID(jid)
    xmpp.send_message(mto=jid, mbody=line, mtype='chat')

def send_groupchat_message(xmpp, jid, line):
    """
    Send a message to the groupchat
    """
    jid = safeJID(jid)
    xmpp.send_message(mto=jid, mbody=line, mtype='groupchat')

def change_show(xmpp, jid, own_nick, show, status):
    """
    Change our 'Show'
    """
    jid = safeJID(jid)
    pres = xmpp.make_presence(pto='%s/%s' % (jid, own_nick))
    if show: # if show is None, don't put a <show /> tag. It means "available"
        pres['type'] = show
    if status:
        pres['status'] = status
    pres.send()

def change_subject(xmpp, jid, subject):
    """
    Change the room subject
    """
    jid = safeJID(jid)
    msg = xmpp.make_message(jid)
    msg['type'] = 'groupchat'
    msg['subject'] = subject
    msg.send()

def change_nick(core, jid, nick, status=None, show=None):
    """
    Change our own nick in a room
    """
    xmpp = core.xmpp
    presence = xmpp.make_presence(pshow=show, pstatus=status, pto=safeJID('%s/%s' % (jid, nick)))
    core.events.trigger('changing_nick', presence)
    presence.send()

def join_groupchat(core, jid, nick, passwd='', maxhistory=None, status=None, show=None, seconds=0):
    xmpp = core.xmpp
    stanza = xmpp.makePresence(pto='%s/%s' % (jid, nick), pstatus=status, pshow=show)
    x = ET.Element('{http://jabber.org/protocol/muc}x')
    if passwd:
        passelement = ET.Element('password')
        passelement.text = passwd
        x.append(passelement)
    if seconds:
        history = ET.Element('{http://jabber.org/protocol/muc}history')
        history.attrib['seconds'] = str(seconds)
        x.append(history)
    stanza.append(x)
    core.events.trigger('joining_muc', stanza)
    to = stanza["to"]
    stanza.send()
    xmpp.plugin['xep_0045'].rooms[jid] = {}
    xmpp.plugin['xep_0045'].ourNicks[jid] = to.resource

def leave_groupchat(xmpp, jid, own_nick, msg):
    """
    Leave the groupchat
    """
    jid = safeJID(jid)
    try:
        xmpp.plugin['xep_0045'].leaveMUC(jid, own_nick, msg)
    except KeyError:
        log.debug("muc.leave_groupchat: could not leave the room %s" % jid)

def set_user_role(xmpp, jid, nick, reason, role, callback=None):
    """
    (try to) Set the role of a MUC user
    (role = 'none': eject user)
    """
    jid = safeJID(jid)
    iq = xmpp.makeIqSet()
    query = ET.Element('{%s}query' % NS_MUC_ADMIN)
    item = ET.Element('{%s}item' % NS_MUC_ADMIN, {'nick':nick, 'role':role})
    if reason:
        reason_el = ET.Element('{%s}reason' % NS_MUC_ADMIN)
        reason_el.text = reason
        item.append(reason_el)
    query.append(item)
    iq.append(query)
    iq['to'] = jid
    if callback:
        return iq.send(block=False, callback=callback)
    try:
        return iq.send()
    except Exception as e:
        return e.iq

def set_user_affiliation(xmpp, muc_jid, affiliation, nick=None, jid=None, reason=None, callback=None):
    """
    (try to) Set the affiliation of a MUC user
    """
    muc_jid = safeJID(muc_jid)
    query = ET.Element('{http://jabber.org/protocol/muc#admin}query')
    if nick:
        item = ET.Element('{http://jabber.org/protocol/muc#admin}item', {'affiliation':affiliation, 'nick':nick})
    else:
        item = ET.Element('{http://jabber.org/protocol/muc#admin}item', {'affiliation':affiliation, 'jid':str(jid)})

    if reason:
        reason_item = ET.Element('{http://jabber.org/protocol/muc#admin}reason')
        reason_item.text = reason
        item.append(reason_item)

    query.append(item)
    iq = xmpp.makeIqSet(query)
    iq['to'] = muc_jid
    if callback:
        return iq.send(block=False, callback=callback)
    try:
        return xmpp.plugin['xep_0045'].setAffiliation(str(muc_jid), str(jid) if jid else None, nick, affiliation)
    except:
        import traceback
        log.debug('Error setting the affiliation: %s', traceback.format_exc())
        return False
