# TUI Launcher
A proof of concept for a TUI-based launcher written in Python using [urwid](http://urwid.org/), initially written for [kelbot](https://fosstodon.org/@kelbot) based on his [query](https://fosstodon.org/@kelbot/105362817844648730) about 'a way to fire off a script via a "button" in a terminal'.

# How to launch:
Suggested way to launch so it gets the current terminal's width: `./launcher.py --term-width="$(tput cols)"`
This would use the default config at `configs/default.py` and default layout at `layouts/default.txt`.

# Creating your own config and layout:
While you could just edit [configs/default.py](configs/default.py) and [layouts/default.txt](layouts/default.txt), it's recommended to use them solely as a template by duplicating to for example `configs/media_controls.py` and `layouts/media_controls.txt` and to edit those instead.

You can then select this new config file with: `./launcher.py --term-width="$(tput cols)" --config-file ./configs/media_controls.py`.

The new layout can be specified with `--layout-file ./layouts/media_controls.txt`, but it's recommended to just specify the path with `layout_file = Path('layouts/media_controls.txt')` in the config file instead, as shown in the example [configs/default.py](configs/default.py).

For a quick reference of the command line arguments: `./launcher.py --help`

# How to upgrade from the initial script posted to Gist.GitHub.com?
If you used the [initial version of this script I posted to gist.github.com a few days ago](https://gist.github.com/FiXato/14b80d612896f6d008988983f3b47eff), then you'll first want to back up your script, or clone this new version in a different location, as the launcher.py would otherwise be overwritten, and you'd lose your config.

This is one of the major reasons behind this update: the separation of config and script.

## Step by step instructions:

1. Clone the repository: `git clone https://github.com/FiXato/tui_launcher.git`
2. Move into the new directoyr: `cd tui_launcher`
3. Create a new config: `cp configs/default.py configs/media_controls.py`
4. Create a new layout: `cp layouts/default.txt layouts/media_controls.txt`
5. Edit your new config and copy the contents of the commands variable from your previous install, over to the commands variable of the new config.
6. Instead of manually calling `button_rows.append()` as in the initial script to add rows of buttons, you can now put the contents of the keys of your `commands` hash in your `layouts/media_controls.txt` file, separating the buttons with commas, one row per line.
For example, if in your previous install you had:
```
button_rows.append(['Play', 'Stop', 'Pause'])
button_rows.append(['Rewind', 'Skip'])
button_rows.append(['Explore'])
```
You can now just add this to `layouts/media_controls.txt`:
```
play, stop, pause
rewind, skip
Explore
```
You don't need to include the entire key; just a unique part of it would suffice. It's also case-insensitive, so you don't have to worry about matching capitals.
7. Reference this layout file by using the proper path for `layout_file` in your config file `configs/media_controls.py`-
8. Launch the script with:  `./launcher.py --term-width="$(tput cols)" --config-file ./configs/media_controls.py`.

# How to support:
Want to buy me a beer? Or toss a few coins to your code-witcher for new hardware?
I accept [PayPal donations](https://www.paypal.com/donate/?hosted_button_id=ZR6T84CGV53V2).

If you prefer to support the development of this project, or [one of my many other projects](https://fixato.org/now.html), in some other way, feel free to contact me, for example though [mastodon](https://mastodon.social/@FiXato), or [any of my other contact methods](https://contact.fixato.org/).
