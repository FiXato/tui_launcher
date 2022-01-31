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
    ('button', 'white', 'dark green'),
    ('focused_button', 'yellow', 'dark green'),
    ('activated_button', 'italics,yellow', 'dark green'),
    ('header', 'dark green,bold,underline', 'black'),
    ('status_line', 'light gray', 'black'),
    ('command_output', 'dark green', 'black'),
    ('footer', 'dark green,bold', 'black'),
    ('dynamic_label', 'dark red,bold', 'yellow'),
    ('last_toot_header', 'yellow,bold', 'dark red'),
    ('item_header', 'white,bold', 'dark blue'),
]
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
  'Get current datetime': ['date', '+%Y%m%d%H%M.%S'],
  'date_dynamic_label': f"""while true; do date "+%Y%m%d%H%M.%S"; sleep 1; done""",
  'tail_dynamic_label': ['tail', '-f', '-n1', 'watch.txt'],
  'tail_header_dynamic_label': ['echo', 'following tail for watch.txt:'],
  'lastfm_dynamic_label': """while true; do curl --silent https://www.last.fm/user/FiXato | pup '#recent-tracks-section .chartlist-row:first-child .chartlist-artist a, #recent-tracks-section .chartlist-row:first-child .chartlist-name a text{}' | paste -s | sed 's/\t/ — /'; sleep 60; done""",
  'get recent scrobbles': '''curl --silent https://www.last.fm/user/FiXato | pup '#recent-tracks-section .chartlist-row json{}' | jq '.[] | "\(.children[4]| .children[]["text"]) — \(.children[3]| .children[]["text"])"' ''',
  '''FiXato's most recent toots''': '''curl --silent https://toot.cat/@FiXato.rss | xq -r '.rss .channel .item[0:5][] | .description | gsub("</?(br|p) ?/?>"; "") | gsub("$"; "<br />")' | html2text --ignore-links --no-wrap-links -b 0 ''',
  'last_toot_dynamic_label': """while true; do curl --silent https://toot.cat/@FiXato.rss | xq -r '.rss .channel .item[0] .description' | html2text --ignore-links --no-wrap-links -b 0; sleep 300; done""",
  'last_toot_header_dynamic_label': 'echo "Last toot by @FiXato@toot.cat"'
}

layout_file = Path('layouts/dynamic_labels.txt')
