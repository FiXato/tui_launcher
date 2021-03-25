#!/usr/bin/env python3
# encoding: utf-8
# TUI-based launcher script by Filip H.F. "FiXato" Slagter
#
# Suggested way to launch so it gets the current terminal's width: `./launcher.py --term-width="$(tput cols)"`
# See README.md (https://github.com/FiXato/tui_launcher/blob/main/README.md) for more detailed launch and usage instructions.
#
# Want to buy me a beer? Or toss a few coins to your code-witcher for new hardware?
# I accept paypal donations: https://www.paypal.com/donate/?hosted_button_id=ZR6T84CGV53V2
#
from os import getenv, pipe
import logging
logger = logging.getLogger()

LOG_LEVEL = getenv('LOG_LEVEL')
if LOG_LEVEL and hasattr(logging, LOG_LEVEL):
  logger.setLevel(getattr(logging, LOG_LEVEL))
from math import floor, ceil
from pathlib import Path
from sys import exit
from importlib import import_module
import argparse
import urwid
import subprocess
import functools
urwid.set_encoding("utf8")
arg_parser = argparse.ArgumentParser(description='TUI-based Launcher that allows you to launch apps and run commands by clicking on self-defined buttons.')
arg_parser.add_argument('--config-file', nargs=1)
arg_parser.add_argument('--term-width', nargs=1)
arg_parser.add_argument('--layout-file', nargs=1)
arg_parser.add_argument('--header-text', nargs=1)
arg_parser.add_argument('--footer-text', nargs=1)
args = arg_parser.parse_args()

def format_exception(message, exception):
  return '\n\t'.join([message, str(type(exception)), str(exception.args), str(exception)])

if args.config_file and args.config_file[0]:
    config_path=Path(args.config_file[0])
    try:
        relative_config_path = config_path.resolve().relative_to(Path('.').resolve())
        if relative_config_path.exists():
            module_name = relative_config_path.with_suffix('').as_posix().replace('/', '.')
            print(f"""Loading module from {module_name}""")
            Config = import_module(module_name)
        else:
            exit(f"""Could not find config at: {relative_config_path}""")
    except Exception as inst:
        logger.error(format_exception(f"""Error loading config: {args.config_file[0]}""", inst))

        exit("error while loading config. Perhaps the config is not relative to the current path?")
else:
    import configs.default as Config

if args.layout_file and args.layout_file[0]:
    Config.layout_file=Path(args.layout_file[0])
elif hasattr(Config, 'layout_file'):
    pass
else:
  Config.layout_file=Path('layout.txt')

if Config.layout_file and not Config.layout_file.exists():
    exit(f"""Config file {str(Config.layout_file)} does not exist""")


if args.term_width and args.term_width[0]:
  TERM_WIDTH=args.term_width[0]
else:
  TERM_WIDTH=None
BUTTON_ROWS = []

def find_command(command_key):
    test_key = command_key.lower()
    for key in Config.commands.keys():
        if test_key in key.lower():
            return key
            return None

if Config.layout_file and Config.layout_file.exists():
    with Config.layout_file.open() as fp:
        for line_index, line in enumerate(fp):
            line = line.strip()
            # Skip commented out lines
            button_row = []
            if line:
              if line[0] == '#':
                continue
              for item in line.split(','):
                  command_key = find_command(item.strip())
                  if command_key:
                      button_row.append(command_key)
                  else:
                      exit(f"""could not find command key: {item.strip()}""")
            BUTTON_ROWS.append(button_row)

if not BUTTON_ROWS:
    BUTTON_ROWS.append(Config.commands.keys())

def show_or_exit(key):
    if key in ('q', 'Q', 'esc'):
        raise urwid.ExitMainLoop()

# Code based on https://stackoverflow.com/a/52262369 by Elias Dorneles, licensed as https://creativecommons.org/licenses/by-sa/4.0/, modified by Filip H.F. "FiXato" Slagter
class BoxButton(urwid.WidgetWrap):
    _border_char = u'─'
    def __init__(self, label, on_press=None, user_data=None, width=None, vertical_padding=None):
        left_decoration = u'│  '
        right_decoration = u'  │'
        if not width:
            inner_padding_length = 0
        else:
            half_width = (width - len(label) - len(left_decoration) - len(right_decoration)) / 2
            inner_padding_length = [ceil(half_width), floor(half_width)]
        if isinstance(vertical_padding, int):
            vertical_padding = [ceil(vertical_padding / 2), floor(vertical_padding / 2)]
        elif isinstance(vertical_padding, list) and len(vertical_padding) == 2 and isinstance(vertical_padding[0], int) and isinstance(vertical_padding[1], int):
            pass
        else:
            vertical_padding = [1, 1]
        padded_label = f"""{' ' *  inner_padding_length[0]}{label}{' ' *  inner_padding_length[1]}"""
        padding_size = 2
        border = self._border_char * (len(padded_label) + padding_size * 2)
        cursor_position = len(border) + padding_size

        self.top = u'┌' + border + u'┐'
        self.blank = f"""{left_decoration}{' ' * len(padded_label)}{right_decoration}"""
        self.middle = f"""{left_decoration}{padded_label}{right_decoration}"""
        self.bottom = u'└' + border + u'┘'

        button_lines = []
        button_lines.append(self.top)
        for _ in range(vertical_padding[0]):
            button_lines.append(self.blank)
        button_lines.append(self.middle)
        for _ in range(vertical_padding[1]):
            button_lines.append(self.blank)
        button_lines.append(self.bottom)

        self.widget = urwid.Pile([urwid.Text(button_line) for button_line in button_lines])

        self.widget = urwid.AttrMap(self.widget, '', 'highlight')

        # here is a lil hack: use a hidden button for evt handling
        self._hidden_btn = urwid.Button('%s' % label, on_press, user_data)

        super(BoxButton, self).__init__(self.widget)
        self.original_label = label

    def selectable(self):
        return True

    def keypress(self, *args, **kw):
        return self._hidden_btn.keypress(*args, **kw)

    def mouse_event(self, *args, **kw):
        return self._hidden_btn.mouse_event(*args, **kw)

def build_box_button(text, onclick, widget_width):
  return BoxButton(text, on_press=onclick, width=widget_width)

def calculate_widget_width(item_count):
  if not TERM_WIDTH:
    return None
  return int(int(TERM_WIDTH) / item_count)

def append_output_widget(widget, label, input_text):
    lines = [line.strip() for line in widget.text.splitlines() if line.strip()]
    input_lines = input_text.decode('utf-8').splitlines()
    input_lines = [f"""[{label}] {line.strip()}""" for line in input_lines if line.strip()]
    new_text = '\n'.join((lines + input_lines)[-10:])
    widget.set_text(new_text)

def handle_click(status_widget, command_output_widget, clicked_widget):
    cmd = Config.commands[clicked_widget.label]
    status_widget.set_text(f"""Last clicked: {clicked_widget.label}""")
    try:
        dummy_stdin, _ = pipe()
        callback = functools.partial(append_output_widget, command_output_widget, clicked_widget.label)
        stdout = Config.loop.watch_pipe(callback)
        stderr = Config.loop.watch_pipe(callback)
        use_shell = (True if isinstance(cmd, str) else False)
        process = subprocess.Popen(cmd, stdin=dummy_stdin, stdout=stdout, stderr=stderr, shell=use_shell)
    except Exception as inst:
        logger.error(format_exception(f"""Error handling click:""", inst))

if __name__ == '__main__':
    # CHANGEME: Change these button labels and their commands to do what you want them to say and do.
    # I use echo commands just for testing, as I don't control my media player via cli, so I don't know what you want to call. ;)
    # just replace the "echo "playing" >> commands.log" part between the single quotes with the play command you use.
    if args.header_text and args.header_text[0]:
      header_text = args.header_text[0]
    else:
      header_text = Config.HEADER_TEXT

    if args.footer_text and args.footer_text[0]:
      footer_text = args.footer_text[0]
    else:
      footer_text = Config.FOOTER_TEXT
    header = urwid.AttrMap(urwid.Text(header_text), 'header')
    footer = urwid.AttrMap(urwid.Text(footer_text), 'footer')
    status_widget = urwid.AttrMap(urwid.Text(''), 'status_line')
    command_output = urwid.AttrMap(urwid.Text(''), 'command_output')
    onclick = lambda widget: (handle_click(status_widget=status_widget.original_widget, command_output_widget=command_output.original_widget, clicked_widget=widget))
    displayed_widgets = []

    if not Config.HIDE_HEADER:
        displayed_widgets.append(header)

    for button_row in BUTTON_ROWS:
        displayed_widgets.append(urwid.Columns([build_box_button(text, onclick, calculate_widget_width(len(button_row))) for text in button_row]))

    if not Config.HIDE_STATUS_LINE:
        displayed_widgets.append(status_widget)

    if not Config.HIDE_COMMAND_OUTPUT:
        displayed_widgets.append(command_output)

    if not Config.HIDE_FOOTER:
        displayed_widgets.append(footer)

    widget = urwid.Pile(displayed_widgets)
    widget = urwid.Filler(widget, 'top')
    Config.loop = urwid.MainLoop(widget, Config.PALETTE, unhandled_input=show_or_exit)
    Config.loop.run()
