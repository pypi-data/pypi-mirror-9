#!/usr/bin/env python3
# Copyright 2010-2011 Florent Le Coz <louiz@louiz.org>
#
# This file is part of Poezio.
#
# Poezio is free software: you can redistribute it and/or modify
# it under the terms of the zlib license. See the COPYING file.

"""
Functions to interact with the keyboard
Mainly, read keys entered and return a string (most
of the time ONE char, but may be longer if it's a keyboard
shortcut, like ^A, M-a or KEY_RESIZE)
"""

import curses
import curses.ascii
import logging
log = logging.getLogger(__name__)

def get_next_byte(s):
    """
    Read the next byte of the utf-8 char
    ncurses seems to return a string of the byte
    encoded in latin-1. So what we get is NOT what we typed
    unless we do the conversion…
    """
    try:
        c = s.getkey()
    except:
        return (None, None)
    if len(c) >= 4:
        return (None, c)
    return (ord(c), c.encode('latin-1')) # returns a number and a bytes object

def get_char_list_old(s):
    """
    Kept for compatibility for python versions without get_wchar()
    (introduced in 3.3) Read one or more bytes, concatenate them to create a
    unicode char. Also treat special bytes to create special chars (like
    control, alt, etc), returns one or more utf-8 chars

    see http://en.wikipedia.org/wiki/UTF-8#Description
    """
    ret_list = []
    # The list of all chars. For example if you paste a text, the list the chars pasted
    # so that they can be handled at once.
    (first, char) = get_next_byte(s)
    while first is not None or char is not None:
        if not isinstance(first, int): # Keyboard special, like KEY_HOME etc
            return [char]
        if first == 127 or first == 8:
            ret_list.append("KEY_BACKSPACE")
            break
        s.timeout(0)            # we are now getting the missing utf-8 bytes to get a whole char
        if first < 127:  # ASCII char on one byte
            if first <= 26:         # transform Ctrl+* keys
                char = chr(first + 64)
                ret_list.append("^"+char)
                (first, char) = get_next_byte(s)
                continue
            if first == 27:
                second = get_char_list_old(s)
                if not second: # if escape was pressed, a second char
                                   # has to be read. But it timed out.
                    return []
                res = 'M-%s' % (second[0],)
                ret_list.append(res)
                (first, char) = get_next_byte(s)
                continue
        if 194 <= first:
            (code, c) = get_next_byte(s) # 2 bytes char
            char += c
        if 224 <= first:
            (code, c) = get_next_byte(s) # 3 bytes char
            char += c
        if 240 <= first:
            (code, c) = get_next_byte(s) # 4 bytes char
            char += c
        try:
            ret_list.append(char.decode('utf-8')) # return all the concatened byte objets, decoded
        except UnicodeDecodeError:
            return None
        # s.timeout(1)            # timeout to detect a paste of many chars
        (first, char) = get_next_byte(s)
    return ret_list

def get_char_list_new(s):
    ret_list = []
    while True:
        try:
            key = s.get_wch()
        except curses.error:
            # No input, this means a timeout occurs.
            return ret_list
        except ValueError: # invalid input
            log.debug('Invalid character entered.')
            return ret_list
        s.timeout(0)
        if isinstance(key, int):
            ret_list.append(curses.keyname(key).decode())
        else:
            if curses.ascii.isctrl(key):
                key = curses.unctrl(key).decode()
                # Here special cases for alt keys, where we get a ^[ and then a second char
                if key == '^[':
                    try:
                        part = s.get_wch()
                    except curses.error:
                        pass
                    except ValueError: # invalid input
                        log.debug('Invalid character entered.')
                        pass
                    else:
                        key = 'M-%s' % part
                    # and an even more special case for keys like
                    # ctrl+arrows, where we get ^[, then [, then a third
                    # char.
                    if key == 'M-[':
                        try:
                            part = s.get_wch()
                        except curses.error:
                            pass
                        except ValueError:
                            log.debug('Invalid character entered.')
                            pass
                        else:
                            key = '%s-%s' % (key, part)
            if key == '\x7f' or key == '\x08':
                key = '^?'
            elif key == '\r':
                key = '^M'
            ret_list.append(key)

class Keyboard(object):
    def __init__(self):
        self.get_char_list = get_char_list_new
        self.escape = False

    def escape_next_key(self):
        """
        The next key pressed by the user should be escaped. e.g. if the user
        presses ^N, keyboard.get_user_input() will return ["^", "N"] instead
        of ["^N"]. This will display ^N in the input, instead of
        interpreting the key binding.
        """
        self.escape = True

    def get_user_input(self, s, timeout=1000):
        """
        Returns a list of all the available characters to read (for example it
        may contain a whole text if there’s some lag, or the user pasted text,
        or the user types really really fast).  Also it can return None, meaning
        that it’s time to do some other checks (because this function is
        blocking, we need to get out of it every now and then even if nothing
        was entered).
        """
        s.timeout(timeout) # The timeout for timed events to be checked every second
        try:
            ret_list = self.get_char_list(s)
        except AttributeError:
            # caught if screen.get_wch() does not exist. In that case we use the
            # old version, so this exception is caught only once. No efficiency
            # issue here.
            log.debug("get_wch() missing, switching to old keyboard method")
            self.get_char_list = get_char_list_old
            ret_list = self.get_char_list(s)
        if not ret_list:
            # nothing at all was read, that’s a timed event timeout
            return None
        if len(ret_list) != 1:
            if ret_list[-1] == '^M':
                ret_list.pop(-1)
            ret_list = [char if char != '^M' else '^J' for char in ret_list]
        if self.escape:
            # Modify the first char of the list into its escaped version (i.e one or more char)
            key = ret_list.pop(0)
            for char in key[::-1]:
                ret_list.insert(0, char)
            self.escape = False
        return ret_list

keyboard = Keyboard()

if __name__ == '__main__':
    s = curses.initscr()
    curses.noecho()
    curses.cbreak()
    s.keypad(1)

    while True:
        chars = keyboard.get_user_input(s)
        for char in chars if chars else '':
            s.addstr('%s ' % (char))
