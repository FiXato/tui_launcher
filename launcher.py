#!/usr/bin/env python3
# encoding: utf-8
from math import floor
import argparse
import urwid
import asyncio
urwid.set_encoding("utf8")
arg_parser = argparse.ArgumentParser(description='Launch tools via buttons.')
arg_parser.add_argument('--term-width', nargs=1)
args = arg_parser.parse_args()
PALETTE = [
    ('normal', '', ''),
    ('bold', 'bold', ''),
    ('blue', 'bold', 'dark blue'),
    ('highlight', 'black', 'dark blue'),
]
TERM_WIDTH=args.term_width[0]

def show_or_exit(key):
    if key in ('q', 'Q', 'esc'):
        raise urwid.ExitMainLoop()

# Code based on https://stackoverflow.com/a/52262369 by Elias Dorneles, licensed as https://creativecommons.org/licenses/by-sa/4.0/, modified by Filip H.F. "FiXato" Slagter
class BoxButton(urwid.WidgetWrap):
    _border_char = u'─'
    def __init__(self, label, on_press=None, user_data=None, width=None):
        left_decoration = u'│  '
        right_decoration = u'  │'
        if not width:
          inner_padding_length = 0
        else:
          inner_padding_length = floor((width - len(label) - len(left_decoration) - len(right_decoration)) / 2)
        inner_padding = ' ' *  inner_padding_length
        padded_label = f"""{inner_padding}{label}{inner_padding}"""
        padding_size = 2
        border = self._border_char * (len(padded_label) + padding_size * 2)
        cursor_position = len(border) + padding_size

        self.top = u'┌' + border + u'┐\n'
        self.blank = f"""{left_decoration}{' ' * len(padded_label)}{right_decoration}\n"""
        self.middle = f"""{left_decoration}{padded_label}{right_decoration}\n"""
        self.bottom = u'└' + border + u'┘'

        self.widget = urwid.Pile([
            urwid.Text(self.top[:-1]),
            urwid.Text(self.blank[:-1]),
            urwid.Text(self.middle[:-1]),
            urwid.Text(self.blank[:-1]),
            urwid.Text(self.bottom),
        ])

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

async def launch(cmd, output_widget):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()

    output = f'[{cmd!r} exited with {proc.returncode}]'
    if stdout:
        output = f'[stdout]\n{stdout.decode()}'
    if stderr:
        output = f'[stderr]\n{stderr.decode()}'
    output_widget.set_text(output)



if __name__ == '__main__':
    # CHANGEME: Change these button labels and their commands to do what you want them to say and do.
    # I use echo commands just for testing, as I don't control my media player via cli, so I don't know what you want to call. ;)
    # just replace the "echo "playing" >> commands.log" part between the single quotes with the play command you use.
    commands = {
      'Play': 'echo "playing" >> commands.log',
      'Stop': 'echo "stopping" >> commands.log',
      'Pause': 'echo "pausing" >> commands.log',
      'Skip': 'echo "Skipping to next track" >> commands.log',
      'Rewind': 'echo "Rewinding to start of track" >> commands.log',
      'Explore': 'explorer.exe',
    }
    header = urwid.Text('TUI launcher')
    footer = urwid.Text('Proof of Concept by Filip H.F. "FiXato" Slagter')
    command_output = urwid.Text('')
    onclick = lambda widget: (footer.set_text('clicked: %r' % widget), asyncio.run(launch(commands[widget.label], output_widget=command_output)))
    #launch(widget, command_output))
    button_texts = commands.keys()
    widget_width = None
    if TERM_WIDTH:
      widget_width = int(int(TERM_WIDTH) / len(button_texts))
    widget = urwid.Pile([
        header, # comment this out with a # at the beginning if you don't want a header line
        urwid.Columns([
            BoxButton(text, on_press=onclick, width=widget_width) for text in button_texts
        ]),
        command_output, #comment this out if you don't want to output the return code and the stderr/stdout text of the commands you run
        footer, #comment this out to hide the footer
    ])
    widget = urwid.Filler(widget, 'top')
    loop = urwid.MainLoop(widget, PALETTE, unhandled_input=show_or_exit)
    loop.run()
