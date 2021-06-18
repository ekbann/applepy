import curses
import sys
import memory
import cpu

#stdscr = 0
text1_map_y = bytearray(0x400)
text1_map_x = bytearray(0x400)

screen_map = [
        '@', 'A', 'B', 'C', 'D', 'E', 'F', 'G',
	'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O',
	'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W',
	'X', 'Y', 'Z', '[', '\\',']', '^', '_',
	' ', '!', '"', '#', '$', '%', '&', '\'',
	'(', ')', '*', '+', ',', '-', '.', '/',
	'0', '1', '2', '3', '4', '5', '6', '7',
	'8', '9', ':', ';', '<', '=', '>', '?',

	'@', 'A', 'B', 'C', 'D', 'E', 'F', 'G',
	'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O',
	'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W',
	'X', 'Y', 'Z', '[', '\\',']', '^', '_',
	' ', '!', '"', '#', '$', '%', '&', '\'',
	'(', ')', '*', '+', ',', '-', '.', '/',
	'0', '1', '2', '3', '4', '5', '6', '7',
	'8', '9', ':', ';', '<', '=', '>', '?',

	'@', 'a', 'b', 'c', 'd', 'e', 'f', 'g',
	'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o',
	'p', 'q', 'r', 's', 't', 'u', 'v', 'w',
	'x', 'y', 'z', '[', '\\',']', '^', '_',
	' ', '!', '"', '#', '$', '%', '&', '\'',
	'(', ')', '*', '+', ',', '-', '.', '/',
	'0', '1', '2', '3', '4', '5', '6', '7',
	'8', '9', ':', ';', '<', '=', '>', '?',

	'@', 'A', 'B', 'C', 'D', 'E', 'F', 'G',
	'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O',
	'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W',
	'X', 'Y', 'Z', '[', '\\',']', '^', '_',
	' ', 'a', 'b', 'c', 'd', 'e', 'f', 'g',
	'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o',
	'p', 'q', 'r', 's', 't', 'u', 'v', 'w',
	'x', 'y', 'z', ';', '<', '=', '>', '?'
        ]		

#init_text1_map()
stdscr = curses.initscr()

def checktty(): # needs 26 rows to add status line
    global stdscr
    size = stdscr.getmaxyx()
    #print ("col =", size[1], "- row =", size[0])
    #sys.stdin.read(1)
    if size[0] < 26:
        close()
        print("TTY has", size[0], "rows; 'a2.py' needs 26 rows")
        exit()

def open1():
    global stdscr

    curses.noecho()
    curses.raw()
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.keypad(True)

def open_delay():
    global stdscr

    curses.noecho()
    curses.raw()
    curses.curs_set(0)
    stdscr.nodelay(False)
    stdscr.keypad(True)

def close():
    global stdscr

    curses.echo()
    curses.noraw()
    stdscr.nodelay(False)
    stdscr.keypad(False)
    curses.endwin()

def init_text1_map():
    global text1_map_y
    global text1_map_x

    for i in range(0x400):
        text1_map_y[i] = 255
        text1_map_x[i] = 255

    text1 = [
        0x400, 0x480, 0x500, 0x580, 0x600, 0x680, 0x700, 0x780,
	0x428, 0x4A8, 0x528, 0x5A8, 0x628, 0x6A8, 0x728, 0x7A8,
	0x450, 0x4D0, 0x550, 0x5D0, 0x650, 0x6D0, 0x750, 0x7D0,
	0x478, 0x4F8, 0x578, 0x5F8, 0x678, 0x6F8, 0x778, 0x7F8
        ]

    for i in range(40):
        #sys.stdin.read(1)
        #print ("col=",i)
        for j in range(24):
            base = text1[j] - 0x400 + i
            #print ("base=", base)
            #print ("row=",j)
            text1_map_y[base] = j
            text1_map_x[base] = i

    #print ("text1_map_y[]=",text1_map_y)
    #print ("text1_map_x[]=",text1_map_x)

def update_screen(address):
    global text1_map_y
    global text1_map_x
    global screen_map
    global stdscr

    row = text1_map_y[address - 0x400]
    col = text1_map_x[address - 0x400]

    if row == 255:
        return

    stdscr.move(row, col)
    #stdscr.refresh()
    c = memory.mem[address]
    if c >= 0x80:
        stdscr.addch(screen_map[c])
    else:
        stdscr.addch(screen_map[c], curses.A_REVERSE)
    stdscr.refresh()

def info(line, message):
    global stdscr

    stdscr.move(line, 0)
    stdscr.addstr(message)
    stdscr.refresh()

def read_keyboard():
    global stdscr

    ch = stdscr.getch()
    if (ch != -1):
        #print ("ch=",ch,hex(ch))
        if ch == ord('~'):   # ASCII 126
            #close()
            #exit()
            return True		# Enter CLI
        elif ch == ord('|'):
            cpu.Pc = memory.loadVector(0xfffc)
        elif ch == ord('\n'):
            ch = ord('\r')
        elif ch == curses.KEY_BACKSPACE or ch == curses.KEY_DC or ch == 127:
            ch = 8      # CTRL-H is 0x88
        # The IF statement below is required for situations where GETCH() returns
        # KEY_RESIZE, KEY_BACKSPACE, KEY_LEFT, KEY_UP, etc.
        # Either we process them above or ignore them below.
        if ch < 256:
                ch = ord(chr(ch).upper())
                ch = ch | 0x80  # raise STROBE
                memory.mem[0xc000] = ch
                #print ("ch=",ch,hex(ch))
        return False
    return False

def save_term():
    curses.def_prog_mode()  # Save "program" mode (curses terminal)
    curses.endwin()         # End curses mode temporarily

def restore_term():
    global stdscr
    curses.reset_prog_mode()    # Return to previous saved "program" mode
    stdscr.refresh()            # ... stored by def_prog_mode()
