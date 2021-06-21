# applepy
Apple ][ emulator written in pure Python and Tkinter.

It runs slow as molasses with normal CPython, so use PyPy3 for similar speed of a real Apple!

    sudo apt install pypy3 pypy3-tk
    cd applepy
    pypy3 a2.py

The emulator does not implement clock-cycles so it is always running at fullspeed. Text screen uses 'curses' and graphics screen uses 'tkinter' and are rendered on separate windows.

Example Session

Start the emulator with:

    python3 a2.py
    
The emulator will boot but will not do anything without a disk inserted. Enter CLI (command line interface) mode with the '~' key and load a binary file at memory location $2000 (Hi-Res page 1) followed by a video refresh:

    bload bin/wc.pic $2000
    hgr1

Let's go back to the emulator with the 'c' command (for 'continue') and stop the booting process with the reset button '|'. It will give us Applesoft BASIC. Let's write a short program and run it:

    10 PRINT "HELLO WORLD! ";
    20 GOTO 10
    RUN

Stop the execution with CTRL-C. Enter CLI mode and press 'q' to quit the emulator.

## Windows

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
