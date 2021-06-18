#!/usr/bin/python3

import cpu 
import memory
import sys
import video
import hires
import string
import drive
import disassemble

def is_hex(x):
    l = len(x)
    if x[0] == "$":         # hex prefix
        x = x[1:]
    elif x[:2] == "0x":     # hex prefix
        x = x[2:]
    elif x[l-1] == "h":     # hex suffix
        x = x[:l-1]
    else:                   # not hex
        if all(c in string.digits for c in x):
            return int(x)   # is int
        else:
            return (-1)     # not int
    if all(c in string.hexdigits for c in x):
        return int(x, 16)   # is hex
    else:
        return (-1)         # not hex

def cli():
    video.save_term()
    in_cli = True
    lpoint = cpu.Pc     # local Pc copy for memory manipulation
    while in_cli:
        s = input('>>> ')
        s = s.split()
        n = len(s)
        if n == 0:
            s = "."     # NULL yields "." command
        #for i in range(n):
        #    print(i, s[i])
        c = s[0]                # CLI command
        if c == ".":
            print (hex(lpoint)[2:].zfill(4), "-\t", sep="", end="")
            cpu.printRegs()
        if c == "status" or c == "s":
            cpu.printStatus()
        if c == "cont" or c == "c":
            in_cli = False
        if c == "quit" or c == "exit" or c == "q":
            video.close()
            exit()
        if c == "hgr1":
            hires.refresh_hires1()
        if c == "reset" or c == "r":
            cpu.Pc = memory.loadVector(0xfffc)
        if c == "disks":
            if drive.diskname[0]:
                s = "Drive 1:"
                if drive.drive == 0:
                    s = "[*] " + s
                else:
                    s = "[ ] " + s
                s += " " + drive.diskname[0]
                if drive.write_prot[0]:
                    s += "#"
                s += " (CRC=" + hex(drive.disk_crc[0])[2:] + ") "
                s += "[T" + hex(drive.cur_track[0])[2:].zfill(2) + "]"
                print (s)
            if drive.diskname[1]:
                s = "Drive 2:"
                if drive.drive == 1:
                    s = "[*] " + s
                else:
                    s = "[ ] " + s
                s += " " + drive.diskname[1]
                if drive.write_prot[1]:
                    s += "#"
                s += " (CRC=" + hex(drive.disk_crc[1])[2:] + ") "
                s += "[T" + hex(drive.cur_track[1])[2:].zfill(2) + "]"
                print (s)
        if c == "eject":
            d = 1   # default drive 1 or "A"
            if n == 2:
                if s[1][0].upper() == "D":
                    d = int(s[1][1])
                else:
                    d = int(s[1][0])
                if d != 1 and d != 2:
                    print ("SYNTAX ERROR:", s[1])
                    d = 0   # do not eject
            if d:
                drive.diskname[d-1] = ""
        if c == "wp" or c == "write":
            d = 1   # default drive 1 or "A"
            if n == 2:
                if s[1][0].upper() == "D":
                    d = int(s[1][1])
                else:
                    d = int(s[1][0])
                if d != 1 and d != 2:
                    print ("SYNTAX ERROR:", s[1])
                    d = 0   # do not eject
            if d:
                d -= 1  # reduce to 0/1
                if drive.diskname[d]:           # disk exists
                    if drive.write_prot[d]:     # disk write-protected
                        drive.write_prot[d] = False     # disk not W-P
                    else:
                        drive.write_prot[d] = True      # disk W-P
        if c == "insert":
            d = 1   # default drive 1 or "A"
            if n == 3:
                if s[2][0].upper() == "D":
                    d = int(s[2][1])
                else:
                    d = int(s[2][0])
                if d != 1 and d != 2:
                    print ("SYNTAX ERROR:", s[2])
                    d = 0   # do not load
            if d:
                drive.loadNib(s[1], d-1)
        if c == "dump" or c == "d":
            if n == 1:
                memory.dump(lpoint)
                if (lpoint + 256) > 0xffff:
                    lpoint = 0
                else:
                    lpoint = (lpoint + 256) & 0xffff
            elif n == 2:
                h = is_hex(s[1])
                if (h < 0):             # -1, not HEX/INT
                    print ("SYNTAX ERROR:", c)
                else:
                    lpoint = h
                    memory.dump(lpoint)
                    if (lpoint + 256) > 0xffff:
                        lpoint = 0
                    else:
                        lpoint = (lpoint + 256) & 0xffff
            else:
                print ("SYNTAX ERROR:", c)
        if c == "dis" or c == "list" or c == "l":
            if n == 1:
                for i in range(21):
                    #if (lpoint + i) <= 0xffff:
                    count = disassemble.dis(lpoint)
                    lpoint = (lpoint + count) & 0xffff
                    #if lpoint > 0xffff:
                    #    lpoint = 0
            elif n == 2:
                h = is_hex(s[1])
                if h < 0:
                    print ("SYNTAX ERROR:", s[1])
                else:
                    lpoint = h
                    for i in range(21):
                        #if (lpoint + i) <= 0xffff:
                        count = disassemble.dis(lpoint)
                        lpoint = (lpoint + count) & 0xffff
                        #if lpoint > 0xffff:
                        #    lpoint = 0
        if c == "bload":
            if n == 3:      # bload <file> <address>
                a = is_hex(s[2])
                if (a < 0):     # not hex/int
                    print ("SYNTAX ERROR:", s[2])
                else:
                    memory.bload(s[1], a)
        if c == "bsave":
            if n == 4:      # bsave <file> <address> <length>
                a = is_hex(s[2])
                l = is_hex(s[3])
                if (a < 0) or (l < 0):
                    print("SYNTAX ERROR:", s[2], s[3])
                else:
                    memory.bsave(s[1], a, l)
        if c == "ssave" or c == "ss":   # save state: memory except registers
            if n == 2:
                memory.bsave(s[1], 0, 65536)
        if c == "sload" or c == "sl":   # load state: memory
            if n == 2:      # sload <file>
                memory.bload(s[1], 0)
    video.restore_term()

#memory.bload("bin/a.out", 0x300)
#memory.bload("bin/lads.bin", 0x79fd)
memory.bload("rom/apple2plus.rom", 0xd000)
#memory.bload("rom/apple2o.rom", 0xd000)
memory.bload("rom/disk.rom", 0xc600)

cpu.setPc(cpu.loadVector(0xfffc))

video.checktty()
video.init_text1_map()
video.open1()
hires.init_hgr1_map()

while 1:
    if video.read_keyboard():
        cli()
    cpu.run()

