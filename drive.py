import video
import cpu

# NIB:  416 bytes per sector, 232960 bytes per disk
# DSK:  256 bytes per sector, 143360 bytes per disk

#disk1 = bytearray(232960)
#disk2 = bytearray(232960)
disk = [bytearray(232960), bytearray(232960)]

#dsk = bytearray(143360)

write_mode = False  # default: read raw nibble 0xC0EC (shift data register)

cur_track = [0, 0]  # current track for drive 1/2
cur_pos = [0, 0]    # current position on track for drive 1/2
drive = 0           # default drive = 1 or A
diskname = ['', ''] # disk filenames for drive 1/2
write_prot = [True, True]   # disk write-protect status
disk_crc = [0, 0]   # disk checksum

def loadNib(filename, drivenum):
    v = memoryview(disk[drivenum])
    f = open(filename, 'rb')
    size = f.readinto(v)
    f.close()
    if size != 232960:
        print ("FILE ERROR:", filename)
    else:
        checksum = 0
        for i in range(232960):
            checksum += int(disk[drivenum][i])
        #print ("Checksum =", hex(checksum)[2:])
        print ("Drive ", (drivenum + 1), ": ", filename, sep="", end="")
        if write_prot[drivenum]:
            print("#", sep="", end="")  # '#' means write-protected
        print (" (CRC=", hex(checksum)[2:], ")", sep="")
        diskname[drivenum] = filename
        disk_crc[drivenum] = checksum

def step_motor(a):      # a = softswitch
    #step_motor.mag = [[0,0,0,0], [0,0,0,0]]
    #step_motor.pmag = [[0,0,0,0], [0,0,0,0]]       # previous
    #step_motor.ppmag = [[0,0,0,0], [0,0,0,0]]      # previous previous
    #step_motor.pnum = [0,0]
    #step_motor.ppnum = [0,0]
    #step_motor.track_pos = [0,0]

    a &= 7
    magnet_number = a >> 1

    step_motor.ppmag[drive][step_motor.ppnum[drive]] = step_motor.pmag[drive][step_motor.ppnum[drive]]
    step_motor.ppnum[drive] = step_motor.pnum[drive]

    step_motor.pmag[drive][step_motor.pnum[drive]] = step_motor.mag[drive][step_motor.pnum[drive]]
    step_motor.pnum[drive] = magnet_number

    if ((a & 1) == 0):
        step_motor.mag[drive][magnet_number] = 0    #False
    else:
        if (step_motor.ppmag[drive][(magnet_number + 1) & 3]):
            step_motor.track_pos[drive] -= 1
            if (step_motor.track_pos[drive] < 0):
                step_motor.track_pos[drive] = 0    # recalibrate drive head
        if (step_motor.ppmag[drive][(magnet_number - 1) & 3]):
            step_motor.track_pos[drive] += 1
            if (step_motor.track_pos[drive] > 140):
                step_motor.track_pos[drive] = 140
        step_motor.mag[drive][magnet_number] = 1    #True
    cur_track[drive] = int((step_motor.track_pos[drive] + 1) / 2)   # BUG? int()?

step_motor.mag = [[0,0,0,0], [0,0,0,0]]
step_motor.pmag = [[0,0,0,0], [0,0,0,0]]       # previous
step_motor.ppmag = [[0,0,0,0], [0,0,0,0]]      # previous previous
step_motor.pnum = [0,0]
step_motor.ppnum = [0,0]
step_motor.track_pos = [0,0]

def read_track():
    track_start = cur_track[drive] * 6656
    track_end = track_start + 6655

    nibble = disk[drive][int(track_start + cur_pos[drive])]
    cur_pos[drive] += 1
    if ((track_start + cur_pos[drive]) == track_end):
        cur_pos[drive] = 0

    sector = hex(int(cur_pos[drive] / 416))[2:].zfill(2)
    msg = "[T"+hex(cur_track[drive])[2:].zfill(2)+"][S"+sector+"]"+" "
    video.info(25,msg)

    return (nibble)

def raw_disk_write():
    track_start = cur_track[drive] * 6656
    track_end = track_start + 6655

    #nibble = disk1[int(track_start + cur_pos[drive])]
    disk[drive][int(track_start + cur_pos[drive])] = cpu.A
    cur_pos[drive] += 1
    if ((track_start + cur_pos[drive]) == track_end):
        cur_pos[drive] = 0

    sector = hex(int(cur_pos[drive] / 416))[2:].zfill(2)
    msg = "[T"+hex(cur_track[drive])[2:].zfill(2)+"][S"+sector+"]"+"*"
    video.info(25,msg)
