# applepy
Apple ][ emulator written in pure Python and Tkinter.

Text-only screen is very fast. Graphics screen is slow as heck but it works. Text screen and graphics screen are rendered on separate windows.

Windows

Requires curses package. You can use curses cross-platform (Windows, MacOS, GNU/Linux) if you install manually for Windows or like other package in others.

Install wheel package. For more info about wheel: http://pythonwheels.com/

Go to this repository: http://www.lfd.uci.edu/~gohlke/pythonlibs/

Download a package with your python version, in example for python 3.8:

    curses‑2.2.1+utf8‑cp38‑cp38‑win_amd64.whl

Install it (this command if for windows, in GNU/Linux install like other package)

    python -m pip install curses‑2.2.1+utf8‑cp38‑cp38‑win_amd64.whl

Just include in your python script:

    import curses

You can also try this command:

    pip install windows-curses

Enjoy!
