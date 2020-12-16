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

# How to support:
Want to buy me a beer? Or toss a few coins to your code-witcher for new hardware?
I accept [PayPal donations](https://www.paypal.com/donate/?hosted_button_id=ZR6T84CGV53V2).

If you prefer to support the development of this project, or [one of my many other projects](https://fixato.org/now.html), in some other way, feel free to contact me, for example though [mastodon](https://mastodon.social/@FiXato), or [any of my other contact methods](https://contact.fixato.org/).
