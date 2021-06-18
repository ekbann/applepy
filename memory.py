#class Memory:
# 64K memory class

import video
import hires
import drive

mem = bytearray(65536)
bank1 = bytearray(0x1000)
bank2 = bytearray(0x1000)
ram = bytearray(0x1000)
rom = bytearray(0x1000)

ram_read = 0
ram_write = 0
bank2_enable = 0

def loadVector(a):
    return (mem[a] | (mem[a + 1] << 8))

def read(address):
    #print (hex(address)[2:].zfill(4) + ":", hex(mem[address])[2:].zfill(2))
    if ((address & 0xff00) == 0xc000):      # process 0xc0 page
        return io_space(address)
    return mem[address]

def io_space(a):
    if (a < 0xc010):                    # 0xc000 - 0xc00f
        return mem[0xc000]
    elif a == 0xc010:                   # STROBE
        mem[0xc000] &= 0x7f             # clear MSB
        return 0                        # what should this be?
    elif (a >= 0xc0e0) and (a <= 0xc0e7):
        drive.step_motor(a)
        return 0
    elif a == 0xc0ea:                   # select drive 1
        drive.drive = 0
        return 0
    elif a == 0xc0eb:                   # select drive 2
        drive.drive = 1
        return 0
    elif a == 0xc0ec:                   # shift data register
        if not(drive.diskname[drive.drive]):
            return (0xff)
        if drive.write_mode:
            drive.raw_disk_write()
            return 0
        return drive.read_track()
    elif a == 0xc0ed:                   # load data register
        return 0
    elif a == 0xc0ee:                   # read mode
        drive.write_mode = False
        if drive.write_prot[drive.drive]:
            return 0xff
        return 0
    elif a == 0xc0ef:                   # write mode
        drive.write_mode = True
        return 0
    else:
        return 0                        # catch-all return value, or crash

def write(address, value):
    #mem[address] = value
    if address < 0xc000:    # RAM
        mem[address] = value
        if (address < 0x04000) and (address >= 0x2000):
            hires.update_hires1(address, value)
        if (address < 0x0800) and (address >= 0x0400):
            video.update_screen(address)
    elif address < 0xd000:  # I/O space
        io_space(address)
    else:
        pass                # ROM (do nothing)

def bload(filename, address):
   v = memoryview(mem)
   f = open(filename, 'rb')
   f.readinto(v[address:])
   f.close()
    
def bsave(filename, address, length):
    v = memoryview(mem)
    f = open(filename, 'wb')
    f.write(v[address:(address+length)])
    f.close()

def dump(address):
   if (address > 0xffff): return
   count = 0
   for j in range(16):          # 16 rows
      print (hex(address)[2:].zfill(4) + ": ", end='')
      for i in range(16):       # 16 bytes per row
         print (hex(mem[address + i])[2:].zfill(2), end=' ')
         if (address + i + 1 > 0xffff):
            print ()
            return
         count += 1
         if (count == 8): print (" ", sep='', end='')
         if (count == 16):
            print()
            count = 0
            address += 16
         
#with open(FILENAME, 'rb') as f:
#    data = bytearray(os.path.getsize(FILENAME))
#    f.readinto(data)
