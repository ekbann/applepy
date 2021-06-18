import memory
from defs import *

Pc = 0      # program counter
Sp = 0xff   # stack pointer
A = 0       # accumulator
X = 0       # X register
Y = 0       # Y register

N = 0       # 7 - Sign
V = 0       # 6 - Overflow
            # 5 - Unused
B = 1       # 4 - Break
D = 0       # 3 - Decimal
I = 0       # 2 - Interrupt
NZ = 0      # 1 - Zero
C = 0       # 0 - Carry

def setPc(a):
    global Pc
    Pc = a

def loadVector(a):
    #return (memory.read(a) | (memory.read(a + 1) << 8))
    return (memory.mem[a] | (memory.mem[a + 1] << 8))

def get_status():
    return ((int(not(not(N)))<<7) |
        (int(not(not(V)))<<6) |
        (int(not(not(B)))<<4) |
        (int(not(not(D)))<<3) |
        (int(not(not(I)))<<2) |
        (int(not(NZ))<<1) |
        (int(not(not(C)))))

def printRegs():
    print ("A=", hex(A)[2:].zfill(2).upper()," X=",hex(X)[2:].zfill(2).upper()," Y=",hex(Y)[2:].zfill(2).upper()," S=",hex(Sp)[2:].zfill(2).upper()," P=",hex(get_status())[2:].zfill(2).upper()," Pc=",hex(Pc)[2:].zfill(4).upper(),sep="")

def printStatus():
    print ("NV_BDIZC")
    print (bin(get_status())[2:].zfill(8))

def run():
    global Pc
    global Sp
    global A
    global X
    global Y
    global N
    global V
    global B
    global D
    global I
    global NZ
    global C

    opcode = memory.mem[Pc]
    Pc += 1
    #print ("Opcode =", hex(opcode))

    if opcode == 0x00:          # BRK
        PCINC()
        push(high(Pc))
        push(low(Pc))
        B = 1   # set I flag?
        push(get_status())
        Pc = join(memory.mem[0xfffe], memory.mem[0xffff])
    elif opcode == 0x01:        # ORA (indirect, X)
        ptr = INDX()
        A |= REFptr(ptr)
        SIGN(A)
        ZERO(A)
    elif opcode == 0x05:        # ORA zero page
        A |= rZEROP()
        SIGN(A)
        ZERO(A)
    elif opcode == 0x06:        # ASL zero page
        ptr = ZEROP()
        val = REFzero(ptr) << 1
        CARRY(val)
        val &= 0xff
        SETzero(ptr, val)
        SIGN(val)
        ZERO(val)
    elif opcode == 0x08:        # PHP
        push(get_status())
    elif opcode == 0x09:        # ORA immediate
        A |= REFimm()
        SIGN(A)
        ZERO(A)
    elif opcode == 0x0a:        # ASL accumulator
        A = A << 1
        CARRY(A)
        A &= 0xff
        SIGN(A)
        ZERO(A)
    elif opcode == 0x0d:        # ORA absolute
        ptr = ABSOL()
        A |= REFptr(ptr)
        SIGN(A)
        ZERO(A)
    elif opcode == 0x0e:        # ASL absolute
        ptr = ABSOL()
        val = REFptr(ptr) << 1
        CARRY(val)
        val &= 0xff
        SETptr(ptr, val)
        SIGN(val)
        ZERO(val)
    elif opcode == 0x10:        # BPL
        if N:
            PCINC()
        else:
            BRANCH()
    elif opcode == 0x11:        # ORA (indirect), Y
        ptr = INDY()
        A |= REFptr(ptr)
        SIGN(A)
        ZERO(A)
    elif opcode == 0x15:        # ORA zero page, X
        A |= rZEROX()
        SIGN(A)
        ZERO(A)
    elif opcode == 0x16:        # ASL zero page, X
        ptr = ZEROX()
        val = REFzero(ptr) << 1
        CARRY(val)
        val &= 0xff
        SETzero(ptr, val)
        SIGN(val)
        ZERO(val)
    elif opcode == 0x18:        # CLC
        C = 0
    elif opcode == 0x19:        # ORA absolute, Y
        A |= REFptr(ABSY())
        SIGN(A)
        ZERO(A)
    elif opcode == 0x1d:        # ORA absolute, X
        A |= REFptr(ABSX())
        SIGN(A)
        ZERO(A)
    elif opcode == 0x1e:        # ASL absolute, X
        ptr = ABSX()
        val = REFptr(ptr) << 1
        CARRY(val)
        val &= 0xff
        SETptr(ptr, val)
        SIGN(val)
        ZERO(val)
    elif opcode == 0x20:        # JSR
        ptmp = REFimm()
        ptmp |= memory.mem[Pc] << 8
        push(high(Pc))
        push(low(Pc))
        Pc = ptmp
    elif opcode == 0x21:        # AND (indirect, X)
        A &= REFptr(INDX())
        SIGN(A)
        ZERO(A)
    elif opcode == 0x24:        # BIT zero page
        tmp = rZEROP()
        ZERO(A & tmp)
        #N = tmp & 0x80      # BUG? Does not yield 0 or 1...
        SIGN(tmp)
        #V = tmp & 0x40      # BUG? Same as above... affects get_status
        OVERFLOW(tmp)
    elif opcode == 0x25:        # AND zero page
        A &= rZEROP()
        SIGN(A)
        ZERO(A)
    elif opcode == 0x26:        # ROL zero page
        ptr = ZEROP()
        val = REFzero(ptr)
        tmp = C
        val = val << 1
        CARRY(val)
        val = (val & 0xff) | tmp
        SETzero(ptr, val)
        SIGN(val)
        ZERO(val)
    elif opcode == 0x28:        # PLP
        put_status(pop())
    elif opcode == 0x29:        # AND immediate
        A &= REFimm()
        SIGN(A)
        ZERO(A)
    elif opcode == 0x2a:        # ROL accumulator
        tmp = C
        A = A << 1
        CARRY(A)
        A = (A & 0xff) | tmp
        SIGN(A)
        ZERO(A)
    elif opcode == 0x2c:        # BIT absolute
        tmp = REFptr(ABSOL())
        ZERO(A & tmp)
        #N = tmp & 0x80         # ORIG CODE
        SIGN(tmp)               # NEW CODE (1 or 0)
        #V = tmp & 0x40         # ORIG CODE
        OVERFLOW(tmp)           # NEW CODE / NEW DEF
    elif opcode == 0x2d:        # AND absolute
        A &= REFptr(ABSOL())
        SIGN(A)
        ZERO(A)
    elif opcode == 0x2e:        # ROL absolute
        ptr = ABSOL()
        val = REFptr(ptr)
        tmp = C
        val = val << 1
        CARRY(val)
        val = (val & 0xff) | tmp
        SETptr(ptr, val)
        SIGN(val)
        ZERO(val)
    elif opcode == 0x30:        # BMI
        if N:
            BRANCH()
        else:
            PCINC()
    elif opcode == 0x31:        # AND (indirect), Y
        A &= REFptr(INDY())
        SIGN(A)
        ZERO(A)
    elif opcode == 0x35:        # AND zero page, X
        A &= rZEROX()
        SIGN(A)
        ZERO(A)
    elif opcode == 0x36:        # ROL zero page, X
        ptr = ZEROX()
        val = REFzero(ptr)
        tmp = C
        val = val << 1
        CARRY(val)
        val = (val & 0xFF) | tmp
        SETzero(ptr, val)
        SIGN(val)
        ZERO(val)
    elif opcode == 0x38:        # SEC
        C = 1
    elif opcode == 0x39:        # AND absolute, Y
        A &= REFptr(ABSY())
        SIGN(A)
        ZERO(A)
    elif opcode == 0x3d:        # AND absolute, X
        A &= REFptr(ABSX())
        SIGN(A)
        ZERO(A)
    elif opcode == 0x3e:        # ROL absolute, X
        ptr = ABSX()
        val = REFptr(ptr)
        tmp = C
        val = val << 1
        CARRY(val)
        val = (val & 0xff) | tmp
        SETptr(ptr, val)
        SIGN(val)
        ZERO(val)
    elif opcode == 0x40:        # RTI
        put_status(pop())
        Pc = pop()
        Pc |= pop() << 8
    elif opcode == 0x41:        # EOR (indirect, X)
        ptr = INDX()
        A ^= REFptr(ptr)
        SIGN(A)
        ZERO(A)
    elif opcode == 0x45:        # EOR zero page#
        A ^= rZEROP()
        SIGN(A)
        ZERO(A)
    elif opcode == 0x46:        # LSR zero page
        ptr = ZEROP()
        tmp = REFzero(ptr)
        C = (tmp & 0x01)
        tmp = tmp >> 1
        SETzero(ptr, tmp)
        N = 0
        ZERO(tmp)
    elif opcode == 0x48:        # PHA
        push(A)
    elif opcode == 0x49:        # EOR immediate
        A ^= REFimm()
        SIGN(A)
        ZERO(A)
    elif opcode == 0x4a:        # LSR accumulator
        C = (A & 0x01)
        A = A >> 1
        N = 0
        ZERO(A)
    elif opcode == 0x4c:        # JMP absolute
        ptmp = REFimm()
        ptmp |= REFimm() << 8
        Pc = ptmp
        #if (jmp_tbl[Pc])
        #       jump(jmp_tbl[Pc]);
    elif opcode == 0x4d:        # EOR absolute
        ptr = ABSOL()
        A ^= REFptr(ptr)
        SIGN(A)
        ZERO(A)
    elif opcode == 0x4e:        # LSR absolute
        ptr = ABSOL()
        tmp = REFptr(ptr)
        C = (tmp & 0x01)
        tmp = tmp >> 1
        SETptr(ptr, tmp)
        N = 0
        ZERO(tmp)
    elif opcode == 0x50:        # BVC
        if (V):
                PCINC()
        else:
                BRANCH()
    elif opcode == 0x51:        # EOR (indirect), Y
        A ^= REFptr(INDY())
        SIGN(A)
        ZERO(A)
    elif opcode == 0x55:        # EOR zero page, X
        A ^= rZEROX()
        SIGN(A)
        ZERO(A)
    elif opcode == 0x56:        # LSR zero page, X
        ptr = ZEROX()
        tmp = REFzero(ptr)
        C = (tmp & 0x01)
        tmp = tmp >> 1
        SETzero(ptr, tmp)
        N = 0
        ZERO(tmp)
    elif opcode == 0x58:        # CLI
        I = 0
    elif opcode == 0x59:        # EOR absolute, Y
        A ^= REFptr(ABSY())
        SIGN(A)
        ZERO(A)
    elif opcode == 0x5d:        # EOR absolute, X
        A ^= REFptr(ABSX())
        SIGN(A)
        ZERO(A)
    elif opcode == 0x5e:        # LSR absolute, X
        ptr = ABSX()
        tmp = REFptr(ptr)
        C = (tmp & 0x01)
        tmp = tmp >> 1
        SETptr(ptr, tmp)
        N = 0
        ZERO(tmp)
    elif opcode == 0x60:        # RTS
        Pc = pop()
        Pc |= pop() << 8
        #Pc += 1
        PCINC()
    elif opcode == 0x61:        # ADC (indirect, X)
        ptr = INDX()
        val = REFptr(ptr)
        tmp = A & 0x80
        stmp = val & 0x80
        if (D):
            num = tobinary(val)
            val = tobinary(A)
            val += num + C
            dCARRY(val)
            while (val >= 100):
                val -= 100
            A = tobcd(val)
        else:
            A += val + C
            CARRY(A)
            A &= 0xFF
        ZERO(A)
        SIGN(A)
        V = (tmp == stmp) and (tmp != N)
    elif opcode ==  0x65:       # ADC zero page
        val = rZEROP()
        tmp = A & 0x80
        stmp = val & 0x80
        if (D):
            num = tobinary(val)
            val = tobinary(A)
            val += num + C
            dCARRY(val)
            while (val >= 100):
                val -= 100
            A = tobcd(val)
        else:
            A += val + C
            CARRY(A)
            A &= 0xFF
        ZERO(A)
        SIGN(A)
        V = (tmp == stmp) and (tmp != N)
    elif opcode == 0x66:        # ROR zero page
        ptr = ZEROP()
        val = REFzero(ptr)
        tmp = C
        C = val & 0x01
        val = val >> 1
        val |= tmp << 7
        SETzero(ptr, val)
        SIGN(val)
        ZERO(val)
    elif opcode == 0x68:        # PLA
        A = pop()
        SIGN(A)
        ZERO(A)
    elif opcode == 0x69:        # ADC immediate
        val = REFimm()
        tmp = A & 0x80
        stmp = val & 0x80
        if (D):
            num = tobinary(val)
            val = tobinary(A)
            val += num + C
            dCARRY(val)
            while (val >= 100):
                val -= 100
            A = tobcd(val)
        else:
            A += val + C
            CARRY(A)
            A &= 0xFF
        ZERO(A)
        SIGN(A)
        V = (tmp == stmp) and (tmp != N)
    elif opcode == 0x6A:        # ROR accumulator
        tmp = C
        C = A & 0x01
        A = A >> 1
        A |= tmp << 7
        SIGN(A)
        ZERO(A)
    elif opcode == 0x6C:        # JMP indirect
        ptmp = REFimm()
        ptmp |= REFimm() << 8
        Pc = memory.mem[ptmp]
        ptmp = (ptmp + 1) & 0xffff      # BUG BUG BUG FIXED!
        Pc |= memory.mem[ptmp] << 8
        #if (jmp_tbl[Pc])
        #       jump(jmp_tbl[Pc]);
    elif opcode == 0x6D:        # ADC absolute
        ptr = ABSOL()
        val = REFptr(ptr)
        tmp = A & 0x80
        stmp = val & 0x80
        if (D):
            num = tobinary(val)
            val = tobinary(A)
            val += num + C
            dCARRY(val)
            while (val >= 100):
                    val -= 100
            A = tobcd(val)
        else:
            A += val + C
            CARRY(A)
            A &= 0xFF
        ZERO(A)
        SIGN(A)
        V = (tmp == stmp) and (tmp != N)
    elif opcode == 0x6E:        # ROR absolute
        ptr = ABSOL()
        val = REFptr(ptr)
        tmp = C
        C = val & 0x01
        val = val >> 1
        val |= tmp << 7
        SETptr(ptr, val)
        SIGN(val)
        ZERO(val)
    elif opcode == 0x70:        # BVS
        if (V):
            BRANCH()
        else:
            PCINC()
 
    elif opcode == 0x71:    # ADC (indirect),Y
        ptr = INDY()
        val = REFptr(ptr)
        tmp = A & 0x80
        stmp = val & 0x80
        if (D):
            num = tobinary(val)
            val = tobinary(A)
            #val += num + C     # C is boolean
            val += num + C
            dCARRY(val)
            while (val >= 100):
                val -= 100
            A = tobcd(val)
        else:
            A += val + C        # C is boolean
            CARRY(A)
            A &= 0xFF
        ZERO(A)
        SIGN(A)
        V = (tmp == stmp) and (tmp != N)
        
    elif opcode == 0x75:    # ADC zero page, X
        val = rZEROX()
        tmp = A & 0x80
        stmp = val & 0x80
        if (D):
            num = tobinary(val)
            val = tobinary(A)
            val += num + C
            dCARRY(val)
            while (val >= 100):
                val -= 100
            A = tobcd(val)
        else:
            A += val + C
            CARRY(A)
            A &= 0xFF
        ZERO(A)
        SIGN(A)
        V = (tmp == stmp) and (tmp != N)

    elif opcode == 0x76:    # ROR zero page, X
        ptr = ZEROX()
        val = REFzero(ptr)
        tmp = C
        C = val & 0x01
        val = val >> 1
        val |= tmp << 7
        SETzero(ptr, val)
        SIGN(val)
        ZERO(val)

    elif opcode == 0x78:    # SEI
        I = 1

    elif opcode == 0x79:    # ADC absolute, Y
        ptr = ABSY()
        val = REFptr(ptr)
        tmp = A & 0x80
        stmp = val & 0x80
        if (D):
            num = tobinary(val)
            val = tobinary(A)
            val += num + C
            dCARRY(val)
            while (val >= 100):
                val -= 100
            A = tobcd(val)
        else:
            A += val + C
            CARRY(A)
            A &= 0xFF
        ZERO(A)
        SIGN(A)
        V = (tmp == stmp) and (tmp != N)

    elif opcode == 0x7D:    # ADC absolute, X
        ptr = ABSX()
        val = REFptr(ptr)
        tmp = A & 0x80
        stmp = val & 0x80
        if (D):
            num = tobinary(val)
            val = tobinary(A)
            val += num + C
            dCARRY(val)
            while (val >= 100):
                val -= 100
            A = tobcd(val)
        else:
            A += val + C
            CARRY(A)
            A &= 0xFF
        ZERO(A)
        SIGN(A)
        V = (tmp == stmp) and (tmp != N)

    elif opcode == 0x7E:    # ROR absolute, X
        ptr = ABSX()
        val = REFptr(ptr)
        tmp = C
        C = val & 0x01
        val = val >> 1
        val |= tmp << 7
        SETptr(ptr, val)
        SIGN(val)
        ZERO(val)
    elif opcode == 0x81:        # STA (indirect, X)
        ptr = INDX()
        SETptr(ptr, A)
    elif opcode == 0x84:        # STY zero page
        sZEROP(Y)
    elif opcode == 0x85:        # STA zero page
        sZEROP(A)
    elif opcode == 0x86:        # STX zero page
        sZEROP(X)
    elif opcode == 0x88:        # DEY
        #Y -= 1
        Y = DEC(Y)
        SIGN(Y)
        ZERO(Y)
    elif opcode == 0x8A:        # TXA
        A = X
        SIGN(A)
        ZERO(A)
    elif opcode == 0x8C:        # STY absolute
        ptr = ABSOL()
        SETptr(ptr, Y)
    elif opcode == 0x8D:        # STA absolute
        ptr = ABSOL()
        SETptr(ptr, A)
    elif opcode == 0x8E:        # STX absolute
        ptr = ABSOL()
        SETptr(ptr, X)
    elif opcode == 0x90:        # BCC
        if (C):
            PCINC()
        else:
            BRANCH()
    elif opcode == 0x91:        # STA (indirect), Y
        ptr = INDY()
        SETptr(ptr, A)
    elif opcode == 0x94:        # STY zero page, X
        sZEROX(Y)
    elif opcode == 0x95:        # STA zero page, X
        sZEROX(A)
    elif opcode == 0x96:        # STX zero page, Y
        sZEROY(X)
    elif opcode == 0x98:        # TYA
        A = Y
        SIGN(A)
        ZERO(A)
    elif opcode == 0x99:        # STA absolute, Y
        ptr = ABSY()
        SETptr(ptr, A)
    elif opcode == 0x9A:        # TXS
        Sp = X
    elif opcode == 0x9D:        # STA absolute, X
        ptr = ABSX()
        SETptr(ptr, A)
    elif opcode == 0xA0:         # LDY immediate
        Y = REFimm()
        SIGN(Y)
        ZERO(Y)
    elif opcode == 0xA1:        # LDA (indirect, X)
        ptr = INDX()
        A = REFptr(ptr)
        SIGN(A)
        ZERO(A)
    elif opcode == 0xA2:        # LDX immediate
        X = REFimm()
        SIGN(X)
        ZERO(X)
    elif opcode == 0xA4:         # LDY zero page
        Y = rZEROP()
        SIGN(Y)
        ZERO(Y)
    elif opcode == 0xA5:        # LDA zero page
        A = rZEROP()
        SIGN(A)
        ZERO(A)
    elif opcode == 0xA6:        # LDX zero page
        X = rZEROP()
        SIGN(X)
        ZERO(X)
    elif opcode == 0xA8:        # TAY
        Y = A
        SIGN(Y)
        ZERO(Y)
    elif opcode == 0xA9:        # LDA immediate
        A = REFimm()
        SIGN(A)
        ZERO(A)
    elif opcode == 0xAA:        # TAX
        X = A
        SIGN(X)
        ZERO(X)
    elif opcode == 0xAC:        # LDY absolute
        ptr = ABSOL()
        Y = REFptr(ptr)
        SIGN(Y)
        ZERO(Y)
    elif opcode == 0xAD:        # LDA absolute
        ptr = ABSOL()
        A = REFptr(ptr)
        SIGN(A)
        ZERO(A)
    elif opcode == 0xAE:        # LDX absolute
        ptr = ABSOL()
        X = REFptr(ptr)
        SIGN(X)
        ZERO(X)
    elif opcode == 0xB0:        # BCS
        if (C):
            BRANCH()
        else:
            PCINC()
    elif opcode == 0xB1:        # LDA (indirect), Y
        ptr = INDY()
        A = REFptr(ptr)
        SIGN(A)
        ZERO(A)
    elif opcode == 0xB4:        # LDY zero page, X
        Y = rZEROX()
        SIGN(Y)
        ZERO(Y)
    elif opcode == 0xB5:        # LDA zero page, X
        A = rZEROX()
        SIGN(A)
        ZERO(A)
    elif opcode == 0xB6:        # LDX zero page, Y
        X = rZEROY()
        SIGN(X)
        ZERO(X)
    elif opcode == 0xB8:        # CLV
        V = 0
    elif opcode == 0xB9:        # LDA absolute, Y
        ptr = ABSY()
        A = REFptr(ptr)
        SIGN(A)
        ZERO(A)
    elif opcode == 0xBA:        # TSX
        X = Sp
        SIGN(X)
        ZERO(X)
    elif opcode == 0xBC:        # LDY absolute, X
        ptr = ABSX()
        Y = REFptr(ptr)
        SIGN(Y)
        ZERO(Y)
    elif opcode == 0xBD:        # LDA absolute, X
        ptr = ABSX()
        A = REFptr(ptr)
        SIGN(A)
        ZERO(A)
    elif opcode == 0xBE:        # LDX absolute, Y
        ptr = ABSY()
        X = REFptr(ptr)
        SIGN(X)
        ZERO(X)
    elif opcode == 0xC0:        # CPY immediate
        tmp = REFimm()
        C = (Y >= tmp)
        tmp = (Y - tmp) & 0xFF
        SIGN(tmp)
        ZERO(tmp)
    elif opcode == 0xC1:        # CMP (indirect, X)
        ptr = INDX()
        tmp = REFptr(ptr)
        C = (A >= tmp)
        tmp = (A - tmp) & 0xFF
        SIGN(tmp)
        ZERO(tmp)
    elif opcode == 0xC4:        # CPY zero page
        tmp = rZEROP()
        C = (Y >= tmp)
        tmp = (Y - tmp) & 0xFF
        SIGN(tmp)
        ZERO(tmp)
    elif opcode == 0xC5:        # CMP zero page
        tmp = rZEROP()
        C = (A >= tmp)
        tmp = (A - tmp) & 0xFF
        SIGN(tmp)
        ZERO(tmp)
    elif opcode == 0xC6:        # DEC zero page
        ptr = ZEROP()
        
        #stmp = REFzero(ptr) - 1    # original code
        tmp = REFzero(ptr)          # BUG FIX
        #if tmp == 0:
        #    stmp = 0xff
        #else:
        #    stmp = tmp - 1
        stmp = DEC(tmp)             # BUG FIX ALTERNATIVE

        SETzero(ptr, stmp)
        SIGN(stmp)
        ZERO(stmp)
    elif opcode == 0xC8:        # INY
        #Y += 1
        Y = INC(Y)
        SIGN(Y)
        ZERO(Y)
    elif opcode == 0xC9:        # CMP immediate
        tmp = REFimm()
        #C = int(A >= tmp)
        C = (A >= tmp)
        tmp = (A - tmp) & 0xFF
        SIGN(tmp)
        ZERO(tmp)
    elif opcode == 0xCA:        # DEX
        #X -= 1
        X = DEC(X)
        SIGN(X)
        ZERO(X)
    elif opcode == 0xCC:        # CPY absolute
        ptr = ABSOL()
        tmp = REFptr(ptr)
        C = (Y >= tmp)
        tmp = (Y - tmp) & 0xFF
        SIGN(tmp)
        ZERO(tmp)
    elif opcode == 0xCD:        # CMP absolute
        ptr = ABSOL()
        tmp = REFptr(ptr)
        C = (A >= tmp)
        tmp = (A - tmp) & 0xFF
        SIGN(tmp)
        ZERO(tmp)
    elif opcode == 0xCE:        # DEC absolute
        ptr = ABSOL()
        #stmp = REFptr(ptr) - 1  # BUG
        tmp = REFptr(ptr)
        stmp = DEC(tmp)
        SETptr(ptr, stmp)
        SIGN(stmp)
        ZERO(stmp)
    elif opcode == 0xD0:        # BNE
        if (NZ):
            BRANCH()
        else:
            PCINC()
    elif opcode == 0xD1:        # CMP (indirect), Y
        ptr = INDY()
        tmp = REFptr(ptr)
        C = (A >= tmp)
        tmp = (A - tmp) & 0xFF
        SIGN(tmp)
        ZERO(tmp)
    elif opcode == 0xD5:        # CMP zero page, X
        tmp = rZEROX()
        C = (A >= tmp)
        tmp = (A - tmp) & 0xFF
        SIGN(tmp)
        ZERO(tmp)
    elif opcode == 0xD6:        # DEC zero page, X
        ptr = ZEROX()
        #stmp = REFzero(ptr) - 1 # BUG
        tmp = REFzero(ptr)
        stmp = DEC(tmp)
        SETzero(ptr, stmp)
        SIGN(stmp)
        ZERO(stmp)
    elif opcode == 0xD8:        # CLD
        D = 0
    elif opcode == 0xD9:        # CMP absolute, Y
        ptr = ABSY()
        tmp = REFptr(ptr)
        C = (A >= tmp)
        tmp = (A - tmp) & 0xFF
        SIGN(tmp)
        ZERO(tmp)
    elif opcode == 0xDD:        # CMP absolute, X
        ptr = ABSX()
        tmp = REFptr(ptr)
        C = (A >= tmp)
        tmp = (A - tmp) & 0xFF
        SIGN(tmp)
        ZERO(tmp)
    elif opcode == 0xDE:        # DEC absolute, X
        ptr = ABSX()
        #stmp = REFptr(ptr) - 1 # BUG
        tmp = REFptr(ptr)
        stmp = DEC(tmp)
        SETptr(ptr, stmp)
        SIGN(stmp)
        ZERO(stmp)
    elif opcode == 0xE0:        # CPX immediate
        tmp = REFimm()
        C = (X >= tmp)
        tmp = (X - tmp) & 0xFF
        SIGN(tmp)
        ZERO(tmp)
    elif opcode == 0xE1:        # SBC (indirect, X)
        ptr = INDX()
        val = REFptr(ptr)
        tmp = A & 0x80
        stmp = val & 0x80
        if (D):
            #assert2(False)
            dSBC(A, val)
        else:
            foo = A - (val + int(not(C)))
            C = (foo >= 0)
            A = foo & 0xFF
        ZERO(A)
        SIGN(A)
        V = (tmp != stmp) and (tmp != N)
    elif opcode == 0xE4:        # CPX zero page
        tmp = rZEROP()
        C = (X >= tmp)
        tmp = (X - tmp) & 0xFF
        SIGN(tmp)
        ZERO(tmp)
    elif opcode == 0xE5:        # SBC zero page
        val = rZEROP()
        tmp = A & 0x80
        stmp = val & 0x80
        if (D):
            #assert2(False)
            dSBC(A, val)
        else:
            foo = A - (val + int(not(C)))
            C = (foo >= 0)
            A = foo & 0xFF
        ZERO(A)
        SIGN(A)
        V = (tmp != stmp) and (tmp != N)
    elif opcode == 0xE6:        # INC zero page
        ptr = ZEROP()
        #stmp = REFzero(ptr) + 1
        stmp = (REFzero(ptr) + 1) & 0xff    # FIXED BUG
        SIGN(stmp)
        ZERO(stmp)
        SETzero(ptr, stmp)
    elif opcode == 0xE8:        # INX
        #X += 1
        X = INC(X)
        SIGN(X)
        ZERO(X)
    elif opcode == 0xE9:        # SBC immediate
        val = REFimm()
        tmp = A & 0x80
        stmp = val & 0x80
        if (D):
            #assert2(False)
            #num = tobinary(val)
            #val = tobinary(A)
            #val -= num - int(not(C))
            #C = (val >= 0)
            #while (val < 0):
            #    val += 100
            #A = tobcd(val)
            dSBC(A, val)
        else:
            foo = A - (val + int(not(C)))
            C = (foo >= 0)
            A = foo & 0xFF
        ZERO(A)
        SIGN(A)
        V = (tmp != stmp) and (tmp != N)
    elif opcode == 0xEA:        # NOP
        pass
    elif opcode == 0xEC:        # CPX absolute
        ptr = ABSOL()
        tmp = REFptr(ptr)
        C = (X >= tmp)
        tmp = (X - tmp) & 0xFF
        SIGN(tmp)
        ZERO(tmp)
    elif opcode == 0xED:        # SBC absolute
        ptr = ABSOL()
        val = REFptr(ptr)
        tmp = A & 0x80
        stmp = val & 0x80
        if (D):
            #assert2(False)
            dSBC(A, val)
        else:
            foo = A - (val + int(not(C)))
            C = (foo >= 0)
            A = foo & 0xFF
        ZERO(A)
        SIGN(A)
        V = (tmp != stmp) and (tmp != N)
    elif opcode == 0xEE:        # INC absolute
        ptr = ABSOL()
        #stmp = REFptr(ptr) + 1
        tmp = REFptr(ptr)
        stmp = INC(tmp)
        SETptr(ptr, stmp)
        SIGN(stmp)
        ZERO(stmp)
    elif opcode == 0xF0:        # BEQ
        if (NZ):
            PCINC()
        else:
            BRANCH()
    elif opcode == 0xF1:        # SBC (indirect), Y
        ptr = INDY()
        val = REFptr(ptr)
        tmp = A & 0x80
        stmp = val & 0x80
        if (D):
            #assert2(False)
            dSBC(A, val)
        else:
            foo = A - (val + int(not(C)))
            C = (foo >= 0)
            A = foo & 0xFF
        ZERO(A)
        SIGN(A)
        V = (tmp != stmp) and (tmp != N)
    elif opcode == 0xF5:        # SBC zero page, X
        val = rZEROX()
        tmp = A & 0x80
        stmp = val & 0x80
        if (D):
            #assert2(False)
            dSBC(A, val)
        else:
            foo = A - (val + int(not(C)))
            C = (foo >= 0)
            A = foo & 0xFF
        ZERO(A)
        SIGN(A)
        V = (tmp != stmp) and (tmp != N)
    elif opcode == 0xF6:        # INC zero page, X
        ptr = ZEROX()
        #stmp = REFzero(ptr) + 1
        tmp = REFzero(ptr)
        stmp = INC(tmp)
        SETzero(ptr, stmp)
        SIGN(stmp)
        ZERO(stmp)
    elif opcode == 0xF8:        # SED
        D = 1
    elif opcode == 0xF9:        # SBC absolute, Y
        ptr = ABSY()
        val = REFptr(ptr)
        tmp = A & 0x80
        stmp = val & 0x80
        if (D):
            #assert2(False)
            dSBC(A, val)
        else:
            foo = A - (val + int(not(C)))
            C = (foo >= 0)
            A = foo & 0xFF
        ZERO(A)
        SIGN(A)
        V = (tmp != stmp) and (tmp != N)
    elif opcode == 0xFD:        # SBC absolute, X
        ptr = ABSX()
        val = REFptr(ptr)
        tmp = A & 0x80
        stmp = val & 0x80
        if (D):
            #assert2(False)
            dSBC(A, val)
        else:
            foo = A - (val + int(not(C)))
            C = (foo >= 0)
            A = foo & 0xFF
        ZERO(A)
        SIGN(A)
        V = (tmp != stmp) and (tmp != N)
    elif opcode == 0xFE:        # INC absolute, X
        ptr = ABSX()
        #stmp = REFptr(ptr) + 1
        tmp = REFptr(ptr)
        stmp = INC(tmp)
        SETptr(ptr, stmp)
        SIGN(stmp)
        ZERO(stmp)
#    else:
#        print ("unknown opcode:", hex(opcode))
