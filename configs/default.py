#!/usr/bin/env python3
# encoding: utf-8
from pathlib import Path

# Formatting options, see: http://urwid.org/manual/displayattributes.html#standard-foreground-colors
# The first value is the key name, which is used with urwid.AttrMap to apply to a widget
# The second is foreground formatting
# The third is background formatting
PALETTE = [
    ('bold', 'bold', ''),
    ('blue', 'bold', 'dark blue'),
    ('button', 'dark green', ''),
    ('activated_button', 'italics,yellow', ''),
    ('focused_button', 'yellow', ''),
    ('header', 'dark green,bold,underline', 'black'),
    ('status_line', 'light gray', 'black'),
    ('command_output', 'dark green', 'black'),
    ('footer', 'dark green,bold', 'black'),
]
VERSION = '1.0'
RELEASE_DATE = '20201216.0340'
HEADER_TEXT = 'TUI launcher'
FOOTER_TEXT = f"""Proof of Concept Python TUI Launcher by Filip H.F. "FiXato" Slagter, v{VERSION} ({RELEASE_DATE})\nhttps://fixato.org/now.html\n\nExit by pressing q or Esc."""
HIDE_HEADER = False #OPTIONAL: set this to True if you want to hide the header that displayed HEADER_TEXT
HIDE_STATUS_LINE = False #OPTIONAL: set this to True if you want to hide the status line that for example contains the last click button
HIDE_COMMAND_OUTPUT = False #OPTIONAL: set this to True if you don't want to output the stderr/stdout text of the commands you run
HIDE_FOOTER = False #OPTIONAL: set this to True if you don't want to display the FOOTER_TEXT at the bottom
HORIZONTAL_PADDING = 'auto' # How much padding do you want to the left and right of your button label? Set to: 'auto' to equally distribute across the full width, 0 or False (without quotes) for a compact view without padding, or a pair of integers to define the left and right amount of padding (e.g. [5, 2] for 5 padding on the left and 2 on the right)
VERTICAL_PADDING = [1,1] # first number is the amount of lines to pad at the top of the button, second number is amount at the bottom

BORDERS = {
    'top_vertical_padding_character': ' ',
    'bottom_vertical_padding_character': ' ',
    'middle_padding_left_character': ' ',
    'middle_padding_right_character': ' ',
    'top_left': '┌',
    'top_right': '┐',
    'top_center': '─',
    'middle_left': '│',
    'middle_right': '│',
    'bottom_left': '└',
    'bottom_right': '┘',
    'bottom_center': '─',
}
# Alternative set of borders, using more rounded corners:
# BORDERS = {
#     'top_vertical_padding_character': ' ',
#     'bottom_vertical_padding_character': ' ',
#     'middle_padding_left_character': ' ',
#     'middle_padding_right_character': ' ',
#     'top_left': '╭',
#     'top_right': '╮',
#     'top_center': '━',
#     'middle_left': '│',
#     'middle_right': '│',
#     'bottom_left': '╰',
#     'bottom_right': '╯',
#     'bottom_center': '━',
# }

# A dict of a commands, where the key will be used as the label for the button, and the value is the command that will be executed when you click on it.
# The command can be either a list of arguments, e.g.: ['curl', '--silent', '-v', '--location', 'https://site.example']
# or a string (in which case it will be executed within a /bin/sh shell): 'curl --silent -v --location https://site.example'
# This default example set of commands does things like append a string to a commands.log, run Windows explorer from Windows Subsystem for Linux, curl an example site, or open my intro video in MPV.
commands = {
  '▶ Play': 'echo "playing" >> commands.log',
  '⏹ Stop': 'echo "stopping" >> commands.log',
  '⏸ Pause': 'echo "pausing" >> commands.log',
  'Skip': 'echo "Skipping to next track" >> commands.log',
  'Rewind': 'echo "Rewinding to start of track" >> commands.log',
  'Explore': 'explorer.exe',
  'CURL': ['curl', 'https://site.example'],
  f"""Watch FiXato's View""": f"""mpv 'https://www.youtube.com/watch?v=FwVWDLxWx2U'"""
}

# Path to a layout file which will be used to determine which buttons to show where.
# See layouts/default.txt for a description of its format
# Can also be set to None to use the keys of the commands all on a single row:
# layout_file = None
layout_file = Path('layouts/default.txt')
