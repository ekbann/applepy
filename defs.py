import memory
import cpu

def assert2(p):
    if (not(p)):
        print ("assertion failure")
    else:
        pass

def low(x):
    #print ("low:", hex(x & 0xff))
    return (x & 0xff)

def high(x):
    #print ("high:", hex((x >> 8) & 0xff))
    return ((x >> 8) & 0xff)

def join(low, high):
    return (low | (high << 8))

#
# Used with BCD arithmetic: ADC/SBC
#
def tobinary(v):    # 0x32 => 32
    return ((v >> 4) * 10 + (v & 0xf))

def tobcd(v):       # 32 => 0x32
    return ((v % 10) | (int(v / 10) << 4))

def dCARRY(x):
    cpu.C = ((x) > 99)
#
# Epple BCD routines
#
def dSBC(op1, op2):
    tmp = (op1 & 0xf) - (op2 & 0xf) - int(not(cpu.C))
    if (tmp & 0x10) != 0:
        tmp -= 6
    cpu.A = tmp
    tmp = (op1 & 0xf0) - (op2 & 0xf0) - (cpu.A & 0x10)
    if (tmp & 0x100) != 0:
        tmp -= 96
    cpu.A = (cpu.A & 0xf) | tmp
    cpu.A &= 0xff
    tmp = op1 - op2 - int(not(cpu.C))
    cpu.C = (0 <= tmp) and (tmp < 0x100)
#
# End of BCD functions
#

def push(s):
    memory.mem[0x100 | cpu.Sp] = s
    SPDEC()

def pop():
    SPINC()
    return (memory.mem[0x100 | cpu.Sp])

def SIGN(x):
    cpu.N = (x & 0x80)

def ZERO(x):
    cpu.NZ = x

def OVERFLOW(x):        # EKB added; necessary?
    cpu.V = (x & 0x40)

def CARRY(x):
    cpu.C = (x > 0xff)

def INC(x):     # general 8-bit x++ with wraparound
    return ((x + 1) & 0xff)

def DEC(x):     # gerenal 8-bit x-- with wraparound
    return ((x - 1) & 0xff)

def SPINC():
    cpu.Sp = (cpu.Sp + 1) & 0xff    # 8-bit

def SPDEC():
    cpu.Sp = (cpu.Sp - 1) & 0xff

def PCINC():
    cpu.Pc = (cpu.Pc + 1) & 0xffff  # 16-bit

def ABSOL():
    l = memory.mem[cpu.Pc]
    PCINC()
    h = memory.mem[cpu.Pc]
    PCINC()
    return (join(l, h))

def ABSY():
    ptr = memory.read(cpu.Pc)
    PCINC()
    ptr |= memory.read(cpu.Pc) << 8
    PCINC()
    ptr += cpu.Y
    return ptr

def ABSX():
    ptr = memory.read(cpu.Pc)
    PCINC()
    ptr |= memory.read(cpu.Pc) << 8
    PCINC()
    ptr += cpu.X
    return ptr

def BRANCH():
    val = memory.read(cpu.Pc)
    PCINC()
    if val & 0x80:
        cpu.Pc += val - 256
    else:
        cpu.Pc += val

def SETptr(ptr, v):
    memory.write(ptr, v)

def REFimm():
    tmp = memory.mem[cpu.Pc]
    PCINC()
    return tmp

def INDX():
    stmp = memory.read(cpu.Pc) + cpu.X
    PCINC()
    ptr = memory.read(stmp)
    stmp += 1
    ptr |= memory.read(stmp) << 8
    return ptr

def INDY():
    stmp = memory.read(cpu.Pc)
    PCINC()
    ptr = memory.read(stmp)
    stmp += 1
    ptr |= memory.read(stmp) << 8
    ptr += cpu.Y
    return ptr

def REFptr(a):
    return memory.read(a)

def REF(a):
    return memory.read(a)

def rZEROP():
    ptr = memory.read(memory.read(cpu.Pc))
    PCINC()
    return ptr

def ZEROP():
    ptr = memory.read(cpu.Pc)
    PCINC()
    return ptr

def ZEROX():
    ptr = (memory.read(cpu.Pc) + cpu.X) & 0xff
    PCINC()
    return ptr

def ZEROY():
    ptr = (memory.read(cpu.Pc) + cpu.Y) & 0xff
    PCINC()
    return ptr

def rZEROX():
    ptr = memory.read((memory.read(cpu.Pc) + cpu.X) & 0xff)
    PCINC()
    return ptr

def rZEROY():
    ptr = memory.read((memory.read(cpu.Pc) + cpu.Y) & 0xff)
    PCINC()
    return ptr

def REFzero(a):
    return memory.read(a)

def SETzero(ptr, v):
    memory.write(ptr, v)
    #memory.write(ptr & 0xff, v)    # DO I NEED TO DO THIS???

def SET(a, v):
    memory.write(a, v)

def sZEROX(v):
    memory.write((memory.read(cpu.Pc) + cpu.X) & 0xff, v)
    PCINC()

def sZEROY(v):
    memory.write((memory.read(cpu.Pc) + cpu.Y) & 0xff, v)
    PCINC()

def ZIND():
    ptr = memory.read(memory.read(cpu.Pc))
    PCINC()
    return ptr

def sZEROP(v):
    memory.write(memory.read(cpu.Pc), v)
    PCINC()

def put_status(s):
    stmp = s
    cpu.N = stmp & 0x80
    cpu.V = stmp & 0x40
    cpu.B = stmp & 0x10
    cpu.D = stmp & 0x08
    cpu.I = stmp & 0x04
    cpu.NZ = int(not(stmp & 0x02))
    cpu.C = stmp & 0x01
