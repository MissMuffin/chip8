import tkinter
from tkinter.filedialog import askopenfilename
from screen import Screen
import pygame
from pygame.locals import *
from utils import Utils
from random import randint
import pdb
import time


class Chip8:

    def __init__(self):

        self.counter = 0

        self.rom_path = None
        self.running = False
        self.screen = Screen()
        self.init_system()
        self.load_font()

    def init_system(self):

        self.memory = [0] * 4096
        self.stack = [0] * 16

        # program counter
        # most programs start at 0x200
        # lower memory space is reserved for interpreter
        self.pc = 512

        # stack pointer
        self.sp = 0

        # timers
        self.delay_timer = 0
        self.sound_timer = 0

        # registers
        self.v = [0] * 16
        self.i = 0

        # we have 16 keys as input
        # 1|2|3|C
        # 4|5|6|D
        # 7|8|9|E
        # A|0|B|F
        # doing array here instead of dict because
        # then we can simply query for keys[{hex_val}]
        # keys[0xf]
        # which will translate into an array index
        self.keys = [False] * 16

        self.draw_flag = True

        # self.screen.clear() # TODO does this work here?

    def load_font(self):
        # load font set into memory
        # first 80 elements of memory will be font set
        for i, val in enumerate(Utils.get_font()):
            self.memory[i] = val

    def start(self):
        self.screen.start()
        self.run()
        self.shutdown()

    def run(self):
        self.running = True

        while self.running:

            self.handle_events()

            # get current opcode
            opcode = (self.memory[self.pc] << 8) | self.memory[self.pc + 1]

            # execute opcode
            self.execute_opcode(opcode)
            self.counter += 1
            oc = hex(opcode)

            # do draw/timer update 60 times pers second
            # we do 1024 isntruction per second
            # 1024/60 = draw/timer update every 17 instructions
            if self.counter == 17:
                if self.draw_flag:
                    self.screen.refresh()
                    # print(f"{self.counter}: draw flag in run")
                    self.draw_flag = False

                # update timers
                if self.delay_timer > 0:
                    self.delay_timer -= 1
                
                if self.sound_timer > 0:
                    # if sound_timer == 1:
                    print("BEEP!")
                    self.sound_timer -= 1
                self.counter = 0

            # slow down emulation to 1024 instructions per second
            time.sleep(round(1/1024))

    def execute_opcode(self, opcode):
        ident = opcode & 0xF000

        if ident == 0x0000:
            param = opcode & 0x000F

            if param == 0x0000:
                # display clear
                self.screen.clear()
                # print("screen clear")
                self.draw_flag = True
                self.pc += 2

            elif param == 0x000E:
                # return from subroutine
                if self.sp > 0:
                    self.sp -= 1
                    self.pc = self.stack[self.sp] & 0x00FFFF
                    self.pc += 2

            else:
                # opcode is 0NNN, not necessary for most roms
                pass

        elif ident == 0x1000:
            # jump to address NNN
            addr = opcode & 0x0FFF
            self.pc = addr & 0x00FFFF

        elif ident == 0x2000:
            # calls subroutine at address NNN
            self.stack[self.sp] = self.pc
            if self.sp < 0xF:
                self.sp += 1 
            addr = opcode & 0x0FFF
            self.pc = addr & 0x00FFFF

        elif ident == 0x3000:
            # skips next instr if V[X] == NN
            x = (opcode & 0x0F00) >> 8
            nn = opcode & 0x00FF
            if self.v[x] == nn:
                self.pc += 2
            self.pc += 2

        elif ident == 0x4000:
            # skips next instr if VX != NN
            x = (opcode & 0x0F00) >> 8
            nn = opcode & 0x00FF
            if self.v[x] != nn:
                self.pc += 2
            self.pc += 2

        elif ident == 0x5000:
            # skips next instr if VX == VY
            x = (opcode & 0x0F00) >> 8
            y = (opcode & 0x00F0) >> 4
            if self.v[x] == self.v[y]:
                self.pc += 2
            self.pc += 2

        elif ident == 0x6000:
            # sets VX to NN
            x = (opcode & 0x0F00) >> 8
            nn = opcode & 0x00FF
            self.v[x] = nn & 0x00FF
            self.pc += 2

        elif ident == 0x7000:
            # adds NN to VX (carry flag not changed)
            x = (opcode & 0x0F00) >> 8
            nn = opcode & 0x00FF
            self.v[x] = (self.v[x] + nn)& 0x00FF
            self.pc += 2

        elif ident == 0x8000:
            param = opcode & 0x000F

            if param == 0x0000:
                # Sets VX to the value of VY
                x = (opcode & 0x0F00) >> 8
                y = (opcode & 0x00F0) >> 4
                self.v[x] = self.v[y]
                self.pc += 2

            elif param == 0x0001:
                # Sets VX to VX or VY. (Bitwise OR operation)
                x = (opcode & 0x0F00) >> 8
                y = (opcode & 0x00F0) >> 4
                self.v[x] = (self.v[x] | self.v[y]) & 0x00FF
                self.pc += 2

            elif param == 0x0002:
                # Sets VX to VX and VY. (Bitwise AND operation)
                x = (opcode & 0x0F00) >> 8
                y = (opcode & 0x00F0) >> 4
                self.v[x] = (self.v[x] & self.v[y]) & 0x00FF
                self.pc += 2

            elif param == 0x0003:
                # Sets VX to VX xor VY.
                x = (opcode & 0x0F00) >> 8
                y = (opcode & 0x00F0) >> 4
                self.v[x] = (self.v[x] ^ self.v[y]) & 0x00FF
                self.pc += 2

            elif param == 0x0004:
                # Adds VY to VX. VF is set to 1 when there's a
                # carry, and to 0 when there isn't.
                x = (opcode & 0x0F00) >> 8
                y = (opcode & 0x00F0) >> 4
                vx = self.v[x]
                vy = self.v[y]

                self.v[0xF] = 0
                if (vy + vx) > 0xFF:
                    self.v[0xF] = 1

                self.v[x] = (vx + vy) & 0x000FF
                self.pc += 2

            elif param == 0x0005:
                # VY is subtracted from VX. VF is set to 0 when
                # there's a borrow, and 1 when there isn't
                x = (opcode & 0x0F00) >> 8
                y = (opcode & 0x00F0) >> 4
                vx = self.v[x]
                vy = self.v[y]

                self.v[0xF] = 1
                if vy > vx:
                    self.v[0xF] = 0
                
                self.v[x] = (vx - vy) & 0x000FF # TODO is correct?
                self.pc += 2

            elif param == 0x0006:
                # Stores the least significant bit of VX in VF
                # and then shifts VX to the right by 1.
                x = (opcode & 0x0F00) >> 8
                vx = self.v[x]
                self.v[0xF] = Utils.get_LSB(vx)
                self.v[x] = (vx >> 1) & 0x00FF
                self.pc += 2

            elif param == 0x0007:
                # Sets VX to VY minus VX. VF is set to 0 when
                # there's a borrow, and 1 when there isn't.
                x = (opcode & 0x0F00) >> 8
                y = (opcode & 0x00F0) >> 4
                vx = self.v[x]
                vy = self.v[y]
                
                self.v[0xF] = 1
                if vx > vy:
                    self.v[0xF] = 0
                
                self.v[x] = (vy - vx) & 0x000FF # TODO is correct?
                self.pc += 2

            elif param == 0x000E:
                # Stores the most significant bit of VX in VF
                # and then shifts VX to the left by 1
                x = (opcode & 0x0F00) >> 8
                vx = self.v[x]
                self.v[0xF] = Utils.get_MSB(vx)
                self.v[x] = (vx << 1) & 0x00FF
                self.pc += 2

        elif ident == 0x9000:
            # skips next instr if VX != VY
            x = (opcode & 0x0F00) >> 8
            y = (opcode & 0x00F0) >> 4
            if self.v[x] != self.v[y]:
                self.pc += 2
            self.pc += 2

        elif ident == 0xA000:
            # Sets I to the address NNN
            nnn = opcode & 0x0FFF
            self.i = nnn
            self.pc += 2

        elif ident == 0xB000:
            # jumps to adress NNN plus V0
            nnn = opcode & 0x0FFF
            v0 = self.v[0]
            self.pc = (nnn + v0) & 0x000FFFF

        elif ident == 0xC000:
            # Sets VX to the result of a bitwise and operation on
            # a random number (Typically: 0 to 255) and NN
            x = (opcode & 0x0F00) >> 8
            nn = opcode & 0x00FF
            self.v[x] = (randint(0, 255) & nn) & 0x00FF
            self.pc += 2

        elif ident == 0xD000:
            # Dxyn
            # Display n-byte sprite starting at memory location I at (Vx, Vy), set VF = collision.

            # The interpreter reads n bytes from memory, starting at the address stored in I. 
            # These bytes are then displayed as sprites on screen at coordinates (Vx, Vy). 
            # Sprites are XORed onto the existing screen. If this causes any pixels to be erased, 
            # VF is set to 1, otherwise it is set to 0. If the sprite is positioned so part of it 
            # is outside the coordinates of the display, it wraps around to the opposite side of 
            # the screen. 

            x = (opcode & 0x0F00) >> 8
            y = (opcode & 0x00F0) >> 4
            n_rows = opcode & 0x000F

            x_coord = self.v[x]
            y_coord = self.v[y]

            # set to no collision initially
            self.v[0xF] = 0
            
            # draw 8 bits x n bits big sprite
            for row in range(n_rows):
                sprite_row = self.memory[self.i + row]
                if (y_coord + row) > 31:
                    self.pc += 2
                    return

                for idx in range(8):

                    if (x_coord + idx) > 63:
                        self.pc += 2
                        return
                    # check each bit in the sprite row
                    # start with MSB (left)
                    mask = 0x8 >> idx
                    if sprite_row & mask not 0:
                        # check for collision
                        old_pixel = self.screen.pixels[x_coord + idx][y_coord + row]
                        if old_pixel == 1:
                            self.v[0xF] = 1

                        self.screen.pixels[x_coord + idx][y_coord + row] = 1 ^ old_pixel
            # print(f"opcode: {opcode} I: {self.i} size: 8x{n_rows} x: {x} y: {y}")
                
            self.draw_flag = True
            self.pc += 2

        elif ident == 0xE000:
            param = opcode & 0x000F

            if param == 0x000E:
                # Skips the next instruction if the key stored in VX is pressed
                x = (opcode & 0x0F00) >> 8
                vx = self.v[x]
                if self.keys[vx]:
                    self.pc += 2
                self.pc += 2

            elif param == 0x0001:
                # Skips the next instruction if the key stored in VX isn't pressed
                x = (opcode & 0x0F00) >> 8
                vx = self.v[x]
                
                if not self.keys[vx]:
                    self.pc += 2
                self.pc += 2

        elif ident == 0xF000:
            param = opcode & 0x000F

            if param == 0x0007:
                # Sets VX to the value of the delay timer.
                x = (opcode & 0x0F00) >> 8
                self.v[x] = self.delay_timer & 0x00FF
                self.pc += 2

            elif param == 0x000A:
                # A key press is awaited, and then stored in VX. (Blocking
                # Operation. All instruction halted until next key event)
                if 1 in self.keys:  
                    # TODO according to https://retrocomputing.stackexchange.com/questions/358/how-are-held-down-keys-handled-in-chip-8
                    # this is wrong behavior?
                    idx = self.keys.index(1)
                    x = (opcode & 0x0F00) >> 8
                    self.v[x] = idx & 0x00FF
                    self.pc += 2
                else:
                    # repeat opcode until key has been pressed
                    self.pc -= 2

            elif param == 0x0005:
                param = opcode & 0x00F0

                if param == 0x0010:
                    # sets the delay timer to VX
                    x = (opcode & 0x0F00) >> 8
                    vx = self.v[x]
                    self.delay_timer = vx
                    self.pc += 2

                elif param == 0x0050:
                    # Stores V0 to VX (including VX) in memory starting at
                    # address I. The offset from I is increased by 1 for each
                    # value written
                    # I is set to I + X + 1 after operation
                    x = (opcode & 0x0F00) >> 8
                    for idx in range(x + 1): # +1 for inclusive
                        self.memory[self.i + idx] = self.v[idx] & 0x00FF
                    self.i = (self.i + x + 1) & 0x000FFFF # TODO is this correct or not? cowgood vs mattmik
                    self.pc += 2

                elif param == 0x0060:
                    # Fills V0 to VX (including VX) with values from memory
                    # starting at address I. The offset from I is increased
                    # by 1 for each value written
                    # I is set to I + X + 1 after operation
                    x = (opcode & 0x0F00) >> 8
                    for idx in range(x + 1): # +1 for inclusive
                        self.v[idx] = (self.memory[self.i + idx]) & 0x000FF
                    self.i = (self.i + x + 1) & 0x000FFFF # TODO is this correct or not? cowgood vs mattmik
                    self.pc += 2

            elif param == 0x0008:
                # Sets the sound timer to VX.
                x = (opcode & 0x0F00) >> 8
                vx = self.v[x]
                self.sound_timer = vx
                self.pc += 2

            elif param == 0x000E:
                # Adds VX to I
                x = (opcode & 0x0F00) >> 8
                vx = self.v[x]
                self.i = (self.i + vx) & 0x00FFFF # TODO is modulo here correct or not? test rom only passes without modulo. why??
                self.pc += 2

            elif param == 0x0009:
                # Sets I to the location of the sprite for the character in VX.
                # Characters 0-F (in hexadecimal) are represented by a 4x5 font.
                x = (opcode & 0x0F00) >> 8
                vx = self.v[x]
                self.i = (vx * 5) & 0x000FFFF  # times 5 because each char is 5 long
                self.pc += 2

            elif param == 0x0003:
                # Stores the binary-coded decimal representation of VX, with the
                # most significant of three digits at the address in I, the middle
                # digit at I plus 1, and the least significant digit at I plus 2.
                # (In other words, take the decimal representation of VX, place
                # the hundreds digit in memory at location in I, the tens digit
                # at location I+1, and the ones digit at location I+2.)
                x = (opcode & 0x0F00) >> 8
                # vx is 3 digit decimal number
                vx = self.v[x]
                # get hundreds
                self.memory[self.i] = vx // 100
                # get tens
                self.memory[self.i + 1] = (vx // 10) % 10
                # get ones
                self.memory[self.i + 2] = vx % 10
                self.pc += 2
                
        else:
            print(f"unknown ident: {hex(ident)} opcode: {hex(opcode)}")
            self.shutdown()

    def shutdown(self):
        self.screen.destroy()

    def reboot(self):
        self.init_system()
        self.load_rom()

    def load_rom(self):

        if not self.rom_path:
            root = tkinter.Tk()
            self.rom_path = askopenfilename()
            root.destroy()

        if not self.rom_path:
            # TODO draw nice screen instead w/ option to load rom
            exit()

        # programs start at 0x200 in memory
        i = 0x200
        with open(self.rom_path, "rb") as f:
            byte = f.read(1)
            while byte:
                self.memory[i] = int.from_bytes(byte, "big", signed=False)
                i += 1
                byte = f.read(1)

    def handle_events(self):
        for event in pygame.event.get():

            if event.type == QUIT:
                self.running = False

            elif event.type == KEYDOWN:

                if event.key == K_ESCAPE:
                    self.running = False

                if event.key == K_1:
                    self.keys[0x1] = True
                if event.key == K_2:
                    self.keys[0x2] = True
                if event.key == K_3:
                    self.keys[0x3] = True
                if event.key == K_4:
                    self.keys[0xC] = True

                if event.key == K_q:
                    self.keys[0x4] = True
                if event.key == K_w:
                    self.keys[0x5] = True
                if event.key == K_e:
                    self.keys[0x6] = True
                if event.key == K_r:
                    self.keys[0xD] = True

                if event.key == K_a:
                    self.keys[0x7] = True
                if event.key == K_s:
                    self.keys[0x8] = True
                if event.key == K_d:
                    self.keys[0x9] = True
                if event.key == K_f:
                    self.keys[0xE] = True

                if event.key == K_z:
                    self.keys[0xA] = True
                if event.key == K_x:
                    self.keys[0x0] = True
                if event.key == K_c:
                    self.keys[0xB] = True
                if event.key == K_v:
                    self.keys[0xF] = True
            elif event.type == KEYUP:

                if event.key == K_1:
                    self.keys[0x1] = False
                if event.key == K_2:
                    self.keys[0x2] = False
                if event.key == K_3:
                    self.keys[0x3] = False
                if event.key == K_4:
                    self.keys[0xC] = False

                if event.key == K_q:
                    self.keys[0x4] = False
                if event.key == K_w:
                    self.keys[0x5] = False
                if event.key == K_e:
                    self.keys[0x6] = False
                if event.key == K_r:
                    self.keys[0xD] = False

                if event.key == K_a:
                    self.keys[0x7] = False
                if event.key == K_s:
                    self.keys[0x8] = False
                if event.key == K_d:
                    self.keys[0x9] = False
                if event.key == K_f:
                    self.keys[0xE] = False

                if event.key == K_z:
                    self.keys[0xA] = False
                if event.key == K_x:
                    self.keys[0x0] = False
                if event.key == K_c:
                    self.keys[0xB] = False
                if event.key == K_v:
                    self.keys[0xF] = False

def main():
    emu = Chip8()

    # emu.rom_path = "BC_test.ch8"
    emu.rom_path = "roms/Space Invaders [David Winter].ch8"
    # emu.rom_path = "roms/Brix [Andreas Gustafsson, 1990].ch8"

    # root = tkinter.Tk() 					# Creating a Tkinter window to use the file browser
    # emu.rom_path = askopenfilename() 	# Displaying the file browser and getting the selecting file
    # root.destroy() 					# Destroying Tkinter
    i = 512
    with open(emu.rom_path, "rb") as f:
        byte = f.read(1)
        while byte:
            emu.memory[i] = int.from_bytes(byte, "big", signed=False)
            i += 1
            byte = f.read(1)

    emu.start()


if __name__ == "__main__":
    main()
