#from tkinter import Tk, Canvas, PhotoImage, mainloop
from tkinter import *
import memory

WIDTH, HEIGHT = 280, 192

window = Tk()
canvas = Canvas(window, width=WIDTH, height=HEIGHT, bg="#000000")
canvas.pack()
img = PhotoImage(width=WIDTH, height=HEIGHT)
#img = PhotoImage(file="wiz.gif")
canvas.create_image((1, 1), image=img, anchor=NW)

# baseline: Hi-Res top line for each of the 24 text lines
# each baseline produces 8 individual lines from these offsets:
# $0000,$0400,$0800,$0c00,$1000,$1400,$1800,$1c00 (line 0-7)
baseline = (0x2000, 0x2080, 0x2100, 0x2180, 0x2200, 0x2280, 0x2300, 0x2380,
            0x2028, 0x20a8, 0x2128, 0x21a8, 0x2228, 0x22a8, 0x2328, 0x23a8,
            0x2050, 0x20d0, 0x2150, 0x21d0, 0x2250, 0x22d0, 0x2350, 0x23d0)

hgr1_map_y = [-1] * 0x2000
hgr1_map_x = [-1] * 0x2000

def init_hgr1_map():
    global hgr1_map_y
    global hgr1_map_x
    all_lines = []  # expand baseline into all 192 lines
    
    for i in range(24):
        base = baseline[i]
        all_lines.append(base)
        all_lines.append(base + 0x0400)
        all_lines.append(base + 0x0800)
        all_lines.append(base + 0x0c00)
        all_lines.append(base + 0x1000)
        all_lines.append(base + 0x1400)
        all_lines.append(base + 0x1800)
        all_lines.append(base + 0x1c00)

    #for i in range(0x2000):
    #    hgr1_map_y[i] = -1
    #    hgr1_map_x[i] = -1

    for row in range(192):
        base = all_lines[row] - 0x2000
        for col in range(40):   # each column has 7 active bits = 280 bits
            hgr1_map_y[base + col] = row
            hgr1_map_x[base + col] = col

def line():
    for x in range(HEIGHT):
        img.put("#ffffff", (x,x))

def dot(color, x , y):
    img.put(color, (x, y))

def refresh_hires1():
    for i in range(0x2000):
        update_hires1(0x2000 + i, memory.mem[0x2000 + i])

def update_hires1(address, byte):
    global hgr1_map_y
    global hgr1_map_x

    address -= 0x2000
    row = hgr1_map_y[address]
    col = hgr1_map_x[address] * 7
    #print("row=",row)
    #print("col=",col)

    if row < 0:
        return

    dots = bin(byte)[2:].zfill(8)[::-1]
    # 4F = 01001111 --> 11110010
    #print("dots=",dots)

    for i in range(7):
        if dots[i] == '1':
            dot("#ffffff", (col+i), row)
            #print("1",sep="",end="")
        else:
            dot("#000000", (col+i), row)
            #print("0",sep="",end="")
    #print()
    window.update()

#mainloop()
