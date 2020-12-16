#!/usr/bin/env python3
# encoding: utf-8
from pathlib import Path

# Formatting options, see: http://urwid.org/manual/displayattributes.html#standard-foreground-colors
# The first value is the key name, which is used with urwid.AttrMap to apply to a widget
# The second is foreground formatting
# The third is background formatting
PALETTE = [
    ('normal', '', ''),
    ('bold', 'bold', ''),
    ('blue', 'bold', 'dark blue'),
    ('highlight', 'black', 'dark blue'),
    ('header', 'dark green,bold,underline', 'black'),
    ('status_line', 'light gray', 'black'),
    ('command_output', 'dark green', 'black'),
    ('footer', 'dark green,bold', 'black'),
]
HEADER_TEXT = 'TUI launcher'
FOOTER_TEXT = 'Proof of Concept Python TUI Launcher by Filip H.F. "FiXato" Slagter, https://fixato.org/now.html'
HIDE_HEADER = False
HIDE_STATUS_LINE = False
HIDE_COMMAND_OUTPUT = False #OPTIONAL: set this to True if you don't want to output the return code and the stderr/stdout text of the commands you run
HIDE_FOOTER = False

HEADER_TEXT = 'TUI launcher'
FOOTER_TEXT = 'Proof of Concept Python TUI Launcher by Filip H.F. "FiXato" Slagter, https://fixato.org/now.html'
HIDE_HEADER = False #OPTIONAL: set this to True if you want to hide the header that displayed HEADER_TEXT
HIDE_STATUS_LINE = False #OPTIONAL: set this to True if you want to hide the status line that for example contains the last click button
HIDE_COMMAND_OUTPUT = False #OPTIONAL: set this to True if you don't want to output the stderr/stdout text of the commands you run
HIDE_FOOTER = False #OPTIONAL: set this to True if you don't want to display the FOOTER_TEXT at the bottom

# A dict of a commands, where the key will be used as the label for the button, and the value is the command that will be executed when you click on it.
# The command can be either a list of arguments, e.g.: ['curl', '--silent', '-v', '--location', 'https://site.example']
# or a string (in which case it will be executed within a /bin/sh shell): 'curl --silent -v --location https://site.example'
commands = {
  'Nemesis 2 boss battle': ['mpv', 'https://www.youtube.com/watch?v=I6aXt36VvQM'],
  'Deathroad to Canada aka DR2C': 'mpv https://www.youtube.com/watch?v=qlNQohU__vQ'
}

layout_file = Path('layouts/mpv.txt')
