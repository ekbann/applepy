#!/usr/bin/python3

import sys

nib = bytearray(232960)
dsk = bytearray(143360)

def loadDsk(filename):
    v = memoryview(dsk)
    f = open(filename, 'rb')
    size = f.readinto(v)
    f.close()
    if size != 143360:
        print("FILE ERROR:", filename)
    else:
        checksum = 0
        for i in range(143360):
            checksum += int(dsk[i])
        print("Checksum =", hex(checksum)[2:])

def saveNib(filename):
    f = open(filename, 'wb')
    f.write(nib)
    f.close()

# 4 by 4 nibble encoding functions
def nib1(a):
    return (((a) >> 1) | 0xaa)
def nib2(a):
    return ((a) | 0xaa)
def denib(a,b):
    return (((((a) & 0x55) << 1) & 0xff) | ((b) & 0x55))

def setup_sector():
    GAP = 0xff  # data gap byte
    # actual sector order on a physical diskette
    phys = [0x00, 0x0D, 0x0B, 0x09, 0x07, 0x05, 0x03, 0x01,
            0x0E, 0x0C, 0x0A, 0x08, 0x06, 0x04, 0x02, 0x0F]
    # list to deskew the DOS sectors
    dos = [0,7,14,6,13,5,12,4,11,3,10,2,9,1,8,15]
    # sectp points to beginning of nib array
    sectp = 0

    for track in range(35):
        for sector in range(16):
            physical_sector = sector
            for i in range(43):
                nib[sectp] = GAP
                #print("nib=",sectp," : ",nib[sectp])
                sectp += 1
            nib[sectp] = 0xd5   # address header
            sectp += 1
            nib[sectp] = 0xaa
            sectp += 1
            nib[sectp] = 0x96
            sectp += 1
            nib[sectp] = 0xff   # disk volume 254
            sectp += 1
            nib[sectp] = 0xfe
            sectp += 1
            nib[sectp] = nib1(track)
            sectp += 1
            nib[sectp] = nib2(track)
            sectp += 1
            nib[sectp] = nib1(sector)
            sectp += 1
            nib[sectp] = nib2(sector)
            sectp += 1
            checksum = 254 ^ track ^ sector
            nib[sectp] = nib1(checksum)
            sectp += 1
            nib[sectp] = nib2(checksum)
            sectp += 1
            nib[sectp] = 0xde   # address trailer
            sectp += 1
            nib[sectp] = 0xaa
            sectp += 1
            nib[sectp] = 0xeb
            sectp += 1
            for i in range(10):
                nib[sectp] = GAP
                sectp += 1
            nib[sectp] = 0xd5   # data header
            sectp += 1
            nib[sectp] = 0xaa
            sectp += 1
            nib[sectp] = 0xad
            sectp += 1
            # nibblize data
            encode_data(track, dos[sector], sectp)
            sectp += 343
            nib[sectp] = 0xde   # data trailer
            sectp += 1
            nib[sectp] = 0xaa
            sectp += 1
            nib[sectp] = 0xeb
            sectp += 1  # sectp should be 416 pointing to next NIB sector
                        # each NIB sector is 416 bytes long [0..415]

            #print ("sectp = ", sectp)
            #sys.stdin.read(1)

            # dump sector
#            count = 0
#            offset = sectp - 416
#            for i in range(416):
#                if not(count):
#                    print(str(i).zfill(4), " ", sep="", end="")
#                print(hex(nib[offset + i])[2:].zfill(2), " ", sep="",  end="")
#                count += 1
#                if count == 8:
#                    print(" ", sep="", end="")
#                if count == 16:
#                    print()
#                    count = 0
#            print()
#            sys.stdin.read(1)

def encode_data(track, sector, sectp):
    buf = bytearray(344)

    tab1 = [0x00, 0x08, 0x04, 0x0C, 0x20, 0x28, 0x24, 0x2C,
	    0x10, 0x18, 0x14, 0x1C, 0x30, 0x38, 0x34, 0x3C,
	    0x80, 0x88, 0x84, 0x8C, 0xA0, 0xA8, 0xA4, 0xAC,
	    0x90, 0x98, 0x94, 0x9C, 0xB0, 0xB8, 0xB4, 0xBC,
	    0x40, 0x48, 0x44, 0x4C, 0x60, 0x68, 0x64, 0x6C,
	    0x50, 0x58, 0x54, 0x5C, 0x70, 0x78, 0x74, 0x7C,
	    0xC0, 0xC8, 0xC4, 0xCC, 0xE0, 0xE8, 0xE4, 0xEC,
	    0xD0, 0xD8, 0xD4, 0xDC, 0xF0, 0xF8, 0xF4, 0xFC]

    tab2 = [0x96, 0x97, 0x9A, 0x9B, 0x9D, 0x9E, 0x9F, 0xA6, 
	    0xA7, 0xAB, 0xAC, 0xAD, 0xAE, 0xAF, 0xB2, 0xB3, 
	    0xB4, 0xB5, 0xB6, 0xB7, 0xB9, 0xBA, 0xBB, 0xBC, 
	    0xBD, 0xBE, 0xBF, 0xCB, 0xCD, 0xCE, 0xCF, 0xD3, 
	    0xD6, 0xD7, 0xD9, 0xDA, 0xDB, 0xDC, 0xDD, 0xDE, 
	    0xDF, 0xE5, 0xE6, 0xE7, 0xE9, 0xEA, 0xEB, 0xEC, 
	    0xED, 0xEE, 0xEF, 0xF2, 0xF3, 0xF4, 0xF5, 0xF6, 
	    0xF7, 0xF9, 0xFA, 0xFB, 0xFC, 0xFD, 0xFE, 0xFF]

    block = track * 16 + sector
    start = block * 256
    for i in range(256):
        buf[86 + i] = dsk[start + i]

    buf[342] = 0    # because (86*3)-256=2 left over C1:C0 pairs
    buf[343] = 0

    dest = 0            # dest = buf
    one = 86            # one = &buf[86]
    two = 86 + 0x56     # two = &buf[86 + 0x56]
    bump = two
    three = 86 + 0xac   # three = &buf[86 + 0xac]
    
    loop = True
    while loop:
        i = (buf[one] & 0x03) | ((buf[two] & 0x03) << 2) | ((buf[three] & 0x03) << 4)
        #print ("i=",i)
        #sys.stdin.read(1)
        if i > 63:
            print("i > 63")
            sys.stdin.read(1)
        buf[dest] = tab1[i]
        dest += 1
        one += 1
        two += 1
        three += 1
        if (one == bump):
            loop = False

    nib[sectp] = buf[0]
    #print("sectp=",sectp)
    #print("buf[0]=",hex(buf[0]))
    #print("buf[1]=",hex(buf[1]))
    #print("^=",hex(buf[0] ^ buf[1]))
    #sys.stdin.read(1)
    for i in range(1, 343):
        nib[sectp + i] = buf[i - 1] ^ buf[i]
    for i in range(343):
        if (nib[sectp + i] >> 2) > 63:
            print("i > 63")
            sys.stdin.read(1)
        nib[sectp + i] = tab2[nib[sectp + i] >> 2]
    #print("buf[0]=",hex(buf[0]))
    #sys.stdin.read(1)

fn = input("DSK/DO file to convert:")
loadDsk(fn)
setup_sector()
saveNib(fn+".nib")
