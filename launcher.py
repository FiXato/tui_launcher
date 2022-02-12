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
from os import environ as ENV
import argparse
import urwid
import subprocess
import functools
import re
import unicodedata
#from IPython import embed
urwid.set_encoding("utf8")
arg_parser = argparse.ArgumentParser(description='TUI-based Launcher that allows you to launch apps and run commands by clicking on self-defined buttons.')
arg_parser.add_argument('--config-file', nargs=1)
arg_parser.add_argument('--term-width', nargs=1)
arg_parser.add_argument('--layout-file', nargs=1)
arg_parser.add_argument('--header-text', nargs=1)
arg_parser.add_argument('--footer-text', nargs=1)
args = arg_parser.parse_args()
warnings = []

def warn(*message):
    logger.warning(message)
    warnings.append(message)

def error(*message):
    logger.error(message)
    warnings.append(f"""!! ERROR !!: {message}""")

def debug(*message):
    if 'DEBUG' in ENV and ENV['DEBUG']:
        warn([*message])

def format_exception(message, exception):
  return '\n\t'.join([message, str(type(exception)), str(exception.args), str(exception)])

config_path = Path('default.py')
if args.config_file and args.config_file[0]:
    config_path=Path(args.config_file[0])
    try:
        relative_config_path = config_path.resolve().relative_to(Path('.').resolve())
        if relative_config_path.exists():
            module_name = relative_config_path.with_suffix('').as_posix().replace('/', '.')
            #print(f"""Loading module from {module_name}""")
            Config = import_module(module_name)
        else:
            exit(f"""Could not find config at: {relative_config_path}""")
    except Exception as inst:
        error(format_exception(f"""Error loading config: {args.config_file[0]}""", inst))

        exit("error while loading config. Perhaps the config is not relative to the current path?")
else:
    import configs.default as Config

Config.active_widget = None
# backwards compatibility hack as I want to rename the 'highlight' palette key to 'focused_button'
Config.palette_keys = [key for (key, fg, bg) in Config.PALETTE]
if 'focused_button' not in Config.palette_keys:
    if 'highlight' not in Config.palette_keys:
        warn("PALETTE in your config is missing a 'focused_button' markup item")
    else:
        warn("PALETTE in your config is missing a 'focused_button' markup item, but has the deprecated 'highlight' item; we'll use that, but please update your config to rename 'highlight' to 'focused_button'")
        highlight_item = [item for item in Config.PALETTE if item[0] == 'highlight'][0]
        Config.PALETTE.append(('focused_button', highlight_item[1], highlight_item[2]))

if args.layout_file and args.layout_file[0]:
    Config.layout_file=Path(args.layout_file[0])
elif hasattr(Config, 'layout_file'):
    pass
else:
  Config.layout_file=Path('layout.txt')

if Config.layout_file and not Config.layout_file.exists():
    exit(f"""Config file {str(Config.layout_file)} does not exist""")

if not hasattr(Config, 'dynamic_labels'):
  Config.dynamic_labels={}

if args.term_width and args.term_width[0]:
  TERM_WIDTH=args.term_width[0]
else:
  TERM_WIDTH=None
BUTTON_ROWS = []

def find_command(command_key):
    palette_formatter, command_key = re.search(r'(?:\{([^}]+)\})?(.+)', command_key).groups()
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
                      button_row.append(item.strip())
                  else:
                      exit(f"""could not find command key: {item.strip()}""")
            BUTTON_ROWS.append(button_row)

if not BUTTON_ROWS:
    BUTTON_ROWS.append(Config.commands.keys())

def show_or_exit(key):
    if key in ('q', 'Q', 'esc'):
        raise urwid.ExitMainLoop()

class Borders():
    def __init__(self,):
        default_border_config = {
            'top_vertical_padding_character': ' ',
            'bottom_vertical_padding_character': ' ',
            'middle_padding_left_character': ' ',
            'middle_padding_right_character': ' ',
            'top_left': '╭',
            'top_right': '╮',
            'top_center': '━',
            'middle_left': '│',
            'middle_right': '│',
            'bottom_left': '╰',
            'bottom_right': '╯',
            'bottom_center': '━',
        }
        for key, value in default_border_config.items():
            setattr(self, key, (Config.BORDERS[key] if Config and 'BORDERS' in Config.__dict__ and key in Config.BORDERS else value))
            debug([key, getattr(self, key)])

    def top(self, center_width):
        return self.top_left + (self.top_center * center_width) + self.top_right

    def bottom(self, center_width):
        return self.bottom_left + (self.bottom_center * center_width) + self.bottom_right

    def top_vertical_padding(self, center_width):
        return self.middle_left + (self.top_vertical_padding_character * center_width) + self.middle_right

    def bottom_vertical_padding(self, center_width):
        return self.middle_left + (self.bottom_vertical_padding_character * center_width) + self.middle_right

# Code based on https://stackoverflow.com/a/52262369 by Elias Dorneles, licensed as https://creativecommons.org/licenses/by-sa/4.0/, modified by Filip H.F. "FiXato" Slagter
class BoxButton(urwid.WidgetWrap):

    def __init__(self, label, on_press=None, user_data=None, width=None, vertical_padding=None, horizontal_padding=None, alignment=None):
        borders = Borders()
        number_of_wide_chars = len([char for char in list(label) if unicodedata.east_asian_width(char) == 'W'])
        if horizontal_padding == None:
            horizontal_padding = 'auto'
        if not width:
            horizontal_padding = [0, 0]
        if horizontal_padding == 'auto':
            label_length = len(label)
            # Emoji tend to be wide characters, which screw up the padding and amount of border characters. A suggestion from Joe Ferndz at https://stackoverflow.com/a/63473262 fixes it for plain emoji, but compound ones such as a country flag (e.g.: 🇳🇱) still fail. Should have a look at counting graphemes instead perhaps (https://stackoverflow.com/questions/43146528/how-to-extract-all-the-emojis-from-text)
            label_length += number_of_wide_chars
            debug(label, 'label len', len(label), 'number_of_wide_chars', number_of_wide_chars, 'total label len', label_length)
            half_width = (width - label_length - len(borders.middle_left) - len(borders.middle_right)) / 2
            inner_padding_length = [ceil(half_width), floor(half_width)]
        else:
            inner_padding_length = horizontal_padding

        if isinstance(vertical_padding, int):
            vertical_padding = [vertical_padding, vertical_padding]
        elif isinstance(vertical_padding, list) and len(vertical_padding) == 2 and isinstance(vertical_padding[0], int) and isinstance(vertical_padding[1], int):
            pass
        else:
            vertical_padding = [1, 1]
        padded_label = f"""{borders.middle_padding_left_character * inner_padding_length[0]}{label}{borders.middle_padding_right_character * inner_padding_length[1]}"""
        #cursor_position = len(border) + padding_size

        button_lines = []
        button_width = len(borders.middle_left + padded_label + borders.middle_right)
        center_width = len(padded_label) + number_of_wide_chars
        debug('padded label len:', len(padded_label), 'button width:', button_width, 'max widget width:', width, 'inner pad len', inner_padding_length, 'center_width', center_width, 'nr of wide chars:', number_of_wide_chars)
        button_lines.append(borders.top(center_width))
        for _ in range(vertical_padding[0]):
            button_lines.append(borders.top_vertical_padding(center_width))
        button_lines.append(borders.middle_left + padded_label + borders.middle_right)
        for _ in range(vertical_padding[1]):
            button_lines.append(borders.bottom_vertical_padding(center_width))
        button_lines.append(borders.bottom(center_width))

        self.widget = urwid.Pile([urwid.Text(button_line) for button_line in button_lines])

        self.widget = apply_markup(self.widget, 'button', 'focused_button')

        # here is a lil hack: use a hidden button for evt handling
        self._hidden_btn = urwid.Button('%s' % label, on_press, user_data)
        self._hidden_btn.wgt = self.widget

        super(BoxButton, self).__init__(self.widget)
        self.original_label = label

    def selectable(self):
        return True

    def keypress(self, *args, **kw):
        return self._hidden_btn.keypress(*args, **kw)

    def mouse_event(self, *args, **kw):
        return self._hidden_btn.mouse_event(*args, **kw)

def build_box_button(text, onclick, widget_width):
    default_vertical_padding = [0, 0]
    default_horizontal_padding = 'auto'
    if 'VERTICAL_PADDING' not in Config.__dict__:
        warn(f"""'VERTICAL_PADDING' not specified in your config. Defaulting to {repr(default_vertical_padding)}. To remove this warning, add the following to your {config_path}:\nVERTICAL_PADDING = {repr(default_vertical_padding)} # first number is the amount of lines to pad at the top of the button, second number is amount at the bottom""")
        Config.VERTICAL_PADDING = default_vertical_padding

    if 'HORIZONTAL_PADDING' not in Config.__dict__:
        warn(f"""'HORIZONTAL_PADDING' not specified in your config. Defaulting to {repr(default_horizontal_padding)}. To remove this warning, add the following to your {config_path}:\nHORIZONTAL_PADDING = {repr(default_horizontal_padding)} # How much padding do you want to the left and right of your button label? Set to: 'auto' to equally distribute across the full width, 0 or False (without quotes) for a compact view without padding, or a pair of integers to define the left and right amount of padding (e.g. [5, 2] for 5 padding on the left and 2 on the right)""")
        Config.HORIZONTAL_PADDING = default_horizontal_padding

    if isinstance(Config.HORIZONTAL_PADDING, int):
        Config.HORIZONTAL_PADDING = [Config.HORIZONTAL_PADDING, Config.HORIZONTAL_PADDING]
    elif Config.HORIZONTAL_PADDING == 'auto' or (isinstance(Config.HORIZONTAL_PADDING, list) and len(Config.HORIZONTAL_PADDING) == 2 and isinstance(Config.HORIZONTAL_PADDING[0], int) and isinstance(Config.HORIZONTAL_PADDING[1], int)):
        pass
    else:
        warn(f"""HORIZONTAL_PADDING ({repr(Config.HORIZONTAL_PADDING)}) is not a valid value. Using default of {repr(default_horizontal_padding)}. Please update your {config_path} config:\nHORIZONTAL_PADDING = {repr(default_horizontal_padding)}""")
        Config.HORIZONTAL_PADDING = default_horizontal_padding

    return BoxButton(text, on_press=onclick, width=widget_width, vertical_padding=Config.VERTICAL_PADDING, horizontal_padding=Config.HORIZONTAL_PADDING)

def calculate_widget_width(index, item_count):
  if not TERM_WIDTH:
    return None
  width = int(TERM_WIDTH) / (1.0 * item_count)

  if index == 0: #FIXME: This should be ceil, but with 3 items it's still breaking the layout with HORIZONTAL_PADDING='auto'...
      return floor(width)
  else:
      return floor(width)

def append_output_widget(widget, label, input_text):
    lines = [line.strip() for line in widget.text.splitlines() if line.strip()]
    input_lines = input_text.decode('utf-8').splitlines()
    input_lines = [f"""[{label}] {line.strip()}""" for line in input_lines if line.strip()]
    new_text = '\n'.join((lines + input_lines)[-10:])
    widget.set_text(new_text)

def refresh_widget(widget, input_text):
    input_lines = input_text.decode('utf-8').splitlines()
    new_text = '\n'.join((input_lines)[-10:])
    widget.set_text(new_text)

def handle_click(status_widget, command_output_widget, clicked_widget):
    cmd = Config.commands[clicked_widget.label]
    status_widget.set_text(f"""Last clicked: {clicked_widget.label}""")
    if 'activated_button' in Config.palette_keys:
        if Config.active_widget:
            Config.active_widget.wgt.set_focus_map({None: 'focused_button'})
        clicked_widget.wgt.set_focus_map({None: 'activated_button'})
    else:
        warn("'activated_button' is missing from the PALETTE in your config.")
    Config.active_widget = clicked_widget

    try:
        dummy_stdin, _ = pipe()
        callback = functools.partial(append_output_widget, command_output_widget, clicked_widget.label)
        stdout = Config.loop.watch_pipe(callback)
        stderr = Config.loop.watch_pipe(callback)
        use_shell = (True if isinstance(cmd, str) else False)
        process = subprocess.Popen(cmd, stdin=dummy_stdin, stdout=stdout, stderr=stderr, shell=use_shell)
    except Exception as inst:
        logger.error(format_exception(f"""Error handling click:""", inst))

def create_column_item(text, onclick, widget_width):
    #print(text)
    palette_formatter, text = re.search(r'(?:\{([^}]+)\})?(.+)', text).groups()
    #print(palette_formatter, text, "\n")
    if not palette_formatter:
      palette_formatter = 'dynamic_label'
    if text.endswith('_dynamic_label'):
        label_widget = apply_markup(urwid.Text(text), palette_formatter)
        cmd_key = find_command(text)
        cmd = Config.dynamic_labels[text] = {'cmd': Config.commands[cmd_key] if cmd_key else None, 'widget': label_widget, 'label_text': text}
        return label_widget

    return build_box_button(find_command(text), onclick, widget_width)

def apply_markup(widget, markup_name, focus_markup_name=None):
    if not markup_name in Config.palette_keys:
        warn(f"""'{markup_name}' is missing from the PALETTE in your config.""")
    if focus_markup_name and (focus_markup_name not in Config.palette_keys):
        warn(f"""'{focus_markup_name}' is missing from the PALETTE in your config.""")
    return urwid.AttrMap(widget, markup_name, focus_markup_name)

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
    if not 'HORIZONTAL_PADDING' in Config.__dict__:
        warn(f"""'HORIZONTAL_PADDING' not specified in your config. Defaulting to 'auto'. To remove this warning, add the following to your {config_path}:\nHORIZONTAL_PADDING = 'auto' # How much padding do you want to the left and right of your button label? Set to: 'auto' to equally distribute across the full width, 0 or False (without quotes) for a compact view without padding, or a pair of integers to define the left and right amount of padding (e.g. [5, 2] for 5 padding on the left and 2 on the right)""")
        Config.HORIZONTAL_PADDING = 'auto'

    header = apply_markup(urwid.Text(header_text), 'header')
    footer = apply_markup(urwid.Text(footer_text), 'footer')
    status_widget = apply_markup(urwid.Text(''), 'status_line')
    command_output = apply_markup(urwid.Text(''), 'command_output')
    onclick = lambda widget: (
      handle_click(
        status_widget=status_widget.original_widget,
        command_output_widget=command_output.original_widget,
        clicked_widget=widget
      )
    )
    displayed_widgets = []

    if args.header_text or not Config.HIDE_HEADER:
        displayed_widgets.append(header)

    for button_row in BUTTON_ROWS:
        columns = urwid.Columns([])
        for index, text in enumerate(button_row):
            label = find_command(text)
            number_of_wide_chars = len([char for char in list(label) if unicodedata.east_asian_width(char) == 'W'])
            col_width = (len(label) + 2 + number_of_wide_chars)
            if Config.HORIZONTAL_PADDING == 'auto':
                col_opts = columns.options('weight', 1)
            else:
                if not Config.HORIZONTAL_PADDING:
                    Config.HORIZONTAL_PADDING = [0, 0]
                if isinstance(Config.HORIZONTAL_PADDING, int):
                    Config.HORIZONTAL_PADDING = [Config.HORIZONTAL_PADDING, Config.HORIZONTAL_PADDING]
                if Config.HORIZONTAL_PADDING:
                    borders = Borders()
                    col_width += Config.HORIZONTAL_PADDING[0] * len(borders.middle_padding_left_character)
                    col_width += Config.HORIZONTAL_PADDING[1] * len(borders.middle_padding_right_character)
                col_opts = columns.options('given', col_width)
            debug('col opts', col_opts, 'col width', col_width, 'text', text, len(text), 'label', label)
            columns.contents.append(
                (create_column_item(label, onclick, calculate_widget_width(index, len(button_row))), col_opts)
            )
        displayed_widgets.append(columns)


    if not Config.HIDE_STATUS_LINE:
        displayed_widgets.append(status_widget)

    if not Config.HIDE_COMMAND_OUTPUT:
        displayed_widgets.append(command_output)

    if args.footer_text or not Config.HIDE_FOOTER:
        displayed_widgets.append(footer)

    widget = urwid.Pile(displayed_widgets)
    widget = urwid.Filler(widget, 'top')
    Config.loop = urwid.MainLoop(widget, Config.PALETTE, unhandled_input=show_or_exit)
    for label_key, dynamic_label in Config.dynamic_labels.items():
        cmd = dynamic_label.get('cmd')
        try:
            dummy_stdin, _ = pipe()
            callback = functools.partial(refresh_widget, dynamic_label['widget'].original_widget)
            stdout = Config.loop.watch_pipe(callback)
            stderr = Config.loop.watch_pipe(callback)
            use_shell = (True if isinstance(cmd, str) else False)
            process = subprocess.Popen(cmd, stdin=dummy_stdin, stdout=stdout, stderr=stderr, shell=use_shell)
        except Exception as inst:
            logger.error(format_exception(f"""Error handling dynamic label creation:""", inst))
    Config.loop.run()
    if warnings:
        print("Warnings during execution:")
        for warning in list(warnings):
            print(' - ' + str('\n'.join(warning)))
