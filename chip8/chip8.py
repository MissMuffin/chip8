import tkinter
from tkinter.filedialog import askopenfilename
from screen import Screen
import pygame
from pygame.locals import *
from utils import Utils
from random import randint

class Chip8:

    def __init__(self):

        self.rom_path = None
        self.rom_path_none_selected = "no_rom_selected.ch8"
        self.running = False
        self.screen = Screen()
        self.beep = pygame.mixer.Sound("beep.ogg")
        self.init_system()

    def init_system(self):

        self.counter = 0
        self.paused = False
        
        self.memory = [0] * 4096
        self.stack = [0] * 16

        # program counter
        # most programs start at 0x200 (==512)
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

        self.load_font()

        self.screen.clear()
        self.draw_flag = True

    def load_font(self):
        # load font set into memory
        # first 80 elements of memory will be font set
        for i, val in enumerate(Utils.get_font()):
            self.memory[i] = val

    def dump(self):
        fname = "dump_mem_reg.txt"
        op = (self.memory[self.pc] << 8) | self.memory[self.pc + 1]
        
        with open(fname, "w") as f:
            f.write(f"Instruction counter: {self.counter}\n")
            f.write(f"Opcode: {op}\n")
            f.write(f"I: {self.i}\n")
            f.write(f"PC: {self.pc}\n")
            f.write(f"SP: {self.sp}\n")
            f.write(f"sound timer: {self.sound_timer}\n")
            f.write(f"delay timer: {self.delay_timer}\n")

            f.write(f"\n-----------------------------------------------------------\n\n")
            for i, val in enumerate(self.stack):
                f.write(f"stack[{i}] : {val}\n")

            f.write(f"\n-----------------------------------------------------------\n\n")
            for i, val in enumerate(self.v):
                f.write(f"V[{i}] : {val}\n")

            f.write(f"\n-----------------------------------------------------------\n\n")
            for i, val in enumerate(self.memory):
                f.write(f"{hex(i)} : {val}\n")
        return fname

    def start(self):
        self.screen.start()
        self.run()
        self.shutdown()

    def run(self):
        self.running = True

        while self.running:

            self.handle_events()

            while self.paused and self.running:
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
                    if self.sound_timer == 1:
                        self.beep.play()
                    self.sound_timer -= 1
                self.counter = 0

            # slow down emulation to 1024 instructions per second
            pygame.time.delay(round((1/1024)*1000))

    def execute_opcode(self, opcode):
        ident = opcode & 0xF000

        if ident == 0x0000:
            param = opcode & 0x000F

            # 00E0
            if param == 0x0000:
                # display clear
                self.screen.clear()
                self.draw_flag = True
                self.pc += 2
            
            # 00EE
            elif param == 0x000E:
                # return from subroutine
                if self.sp > 0:
                    self.sp -= 1
                    self.pc = self.stack[self.sp] & 0x00FFFF
                    self.pc += 2

            else:
                # opcode is 0NNN, not necessary for most roms
                pass

        # 1NNN
        elif ident == 0x1000:
            # jump to address NNN
            addr = opcode & 0x0FFF
            self.pc = addr & 0x00FFFF

        # 2NNN
        elif ident == 0x2000:
            # calls subroutine at address NNN
            self.stack[self.sp] = self.pc
            if self.sp < 0xF:
                self.sp += 1 
            addr = opcode & 0x0FFF
            self.pc = addr & 0x00FFFF

        # 3XNN
        elif ident == 0x3000:
            # skips next instr if V[X] == NN
            x = (opcode & 0x0F00) >> 8
            nn = opcode & 0x00FF
            if self.v[x] == nn:
                self.pc += 2
            self.pc += 2

        # 4XNN
        elif ident == 0x4000:
            # skips next instr if VX != NN
            x = (opcode & 0x0F00) >> 8
            nn = opcode & 0x00FF
            if self.v[x] != nn:
                self.pc += 2
            self.pc += 2

        # 5XY0
        elif ident == 0x5000:
            # skips next instr if VX == VY
            x = (opcode & 0x0F00) >> 8
            y = (opcode & 0x00F0) >> 4
            if self.v[x] == self.v[y]:
                self.pc += 2
            self.pc += 2

        # 6XNN
        elif ident == 0x6000:
            # sets VX to NN
            x = (opcode & 0x0F00) >> 8
            nn = opcode & 0x00FF
            self.v[x] = nn & 0x00FF
            self.pc += 2

        # 7XNN
        elif ident == 0x7000:
            # adds NN to VX (carry flag not changed)
            x = (opcode & 0x0F00) >> 8
            nn = opcode & 0x00FF
            self.v[x] = (self.v[x] + nn)& 0x00FF
            self.pc += 2

        elif ident == 0x8000:
            param = opcode & 0x000F

            # 8XY0
            if param == 0x0000:
                # Sets VX to the value of VY
                x = (opcode & 0x0F00) >> 8
                y = (opcode & 0x00F0) >> 4
                self.v[x] = self.v[y]
                self.pc += 2

            # 8XY1
            elif param == 0x0001:
                # set VX to VX or VY. (bitwise OR operation)
                x = (opcode & 0x0F00) >> 8
                y = (opcode & 0x00F0) >> 4
                self.v[x] = (self.v[x] | self.v[y]) & 0x00FF
                self.pc += 2

            # 8XY2
            elif param == 0x0002:
                # set VX to VX and VY. (bitwise AND operation)
                x = (opcode & 0x0F00) >> 8
                y = (opcode & 0x00F0) >> 4
                self.v[x] = (self.v[x] & self.v[y]) & 0x00FF
                self.pc += 2

            # 8XY3
            elif param == 0x0003:
                # set VX to VX xor VY.
                x = (opcode & 0x0F00) >> 8
                y = (opcode & 0x00F0) >> 4
                self.v[x] = (self.v[x] ^ self.v[y]) & 0x00FF
                self.pc += 2

            # 8XY4
            elif param == 0x0004:
                # Adds VY to VX. VF is set to 1 when there is a
                # carry (meaning result > 0xFF (==255)) 
                # and to 0 when not
                x = (opcode & 0x0F00) >> 8
                y = (opcode & 0x00F0) >> 4
                vx = self.v[x]
                vy = self.v[y]

                self.v[0xF] = 0
                if (vy + vx) > 0xFF:
                    self.v[0xF] = 1

                self.v[x] = (vx + vy) & 0x000FF
                self.pc += 2

            # 8XY5
            elif param == 0x0005:
                # VY is subtracted from VX
                # VF is set to 0 when there is a borrow
                # and 1 when not
                x = (opcode & 0x0F00) >> 8
                y = (opcode & 0x00F0) >> 4
                vx = self.v[x]
                vy = self.v[y]

                self.v[0xF] = 1
                if vy > vx:
                    self.v[0xF] = 0
                
                self.v[x] = (vx - vy) & 0x000FF # TODO is correct?
                self.pc += 2

            # 8XY6
            elif param == 0x0006:
                # store the least significant bit of VX in VF
                # and then shift VX to the right by 1
                x = (opcode & 0x0F00) >> 8
                vx = self.v[x]
                self.v[0xF] = Utils.get_LSB(vx)
                self.v[x] = (vx >> 1) & 0x00FF
                self.pc += 2

            # 8XY7
            elif param == 0x0007:
                # set VX to VY minus VX
                # VF is set to 0 when there is a borrow
                # and 1 when not
                x = (opcode & 0x0F00) >> 8
                y = (opcode & 0x00F0) >> 4
                vx = self.v[x]
                vy = self.v[y]
                
                self.v[0xF] = 1
                if vx > vy:
                    self.v[0xF] = 0
                
                self.v[x] = (vy - vx) & 0x000FF # TODO is correct?
                self.pc += 2

            # 8XYE
            elif param == 0x000E:
                # store the most significant bit of VX in VF
                # and then shifts VX to the left by 1
                x = (opcode & 0x0F00) >> 8
                vx = self.v[x]
                self.v[0xF] = Utils.get_MSB(vx)
                self.v[x] = (vx << 1) & 0x00FF
                self.pc += 2

        # 9XY0
        elif ident == 0x9000:
            # skip next instr if VX != VY
            x = (opcode & 0x0F00) >> 8
            y = (opcode & 0x00F0) >> 4
            if self.v[x] != self.v[y]:
                self.pc += 2
            self.pc += 2

        # ANNN
        elif ident == 0xA000:
            # set I to the address NNN
            nnn = opcode & 0x0FFF
            self.i = nnn
            self.pc += 2

        # BNNN
        elif ident == 0xB000:
            # jump to adress NNN plus V0
            nnn = opcode & 0x0FFF
            v0 = self.v[0]
            self.pc = (nnn + v0) & 0x000FFFF

        # CXNN
        elif ident == 0xC000:
            # set VX to a random number (0 to 255) 
            # masked with NN
            x = (opcode & 0x0F00) >> 8
            nn = opcode & 0x00FF
            self.v[x] = (randint(0, 255) & nn) & 0x00FF
            self.pc += 2

        # DXYN
        elif ident == 0xD000:
            # draw sprite at position (VX, VY)
            # using N bytes of sprite data at the address stored in I 
            # sprites are XORed onto existing screen
            # if any pre-existing pixels are erasid in that process, the collision flag VF is set
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

                if (y_coord + row) >= 32:
                    continue

                for idx in range(8):

                    if (x_coord + idx) >= 64:
                        continue

                    # check each bit in the sprite row
                    # start with MSB (left)
                    mask = 0x80 >> idx
                    if (sprite_row & mask) != 0:

                        # check for collision
                        old_pixel = self.screen.pixels[x_coord + idx][y_coord + row]

                        if old_pixel == 1:
                            self.v[0xF] = 1

                        self.screen.pixels[x_coord + idx][y_coord + row] = old_pixel ^ 1
                
            self.draw_flag = True
            self.pc += 2

        elif ident == 0xE000:
            param = opcode & 0x000F

            # EX9E
            if param == 0x000E:
                # skip the next instruction if the key stored in VX is pressed
                x = (opcode & 0x0F00) >> 8
                vx = self.v[x]
                if self.keys[vx]:
                    self.pc += 2
                self.pc += 2

            # EXA1
            elif param == 0x0001:
                # skip the next instruction if the key stored in VX is not pressed
                x = (opcode & 0x0F00) >> 8
                vx = self.v[x]
                
                if not self.keys[vx]:
                    self.pc += 2
                self.pc += 2

        elif ident == 0xF000:
            param = opcode & 0x000F

            # FX07
            if param == 0x0007:
                # set VX to the value of the delay timer
                x = (opcode & 0x0F00) >> 8
                self.v[x] = self.delay_timer & 0x00FF
                self.pc += 2

            # FX0A
            elif param == 0x000A:
                # wait for key press and then store key in VX
                # this blocks until a key has been pressed
                if 1 in self.keys:  
                    idx = self.keys.index(1)
                    x = (opcode & 0x0F00) >> 8
                    self.v[x] = idx & 0x00FF
                    self.pc += 2
                else:
                    # repeat opcode until key has been pressed
                    self.pc -= 2

            elif param == 0x0005:
                param = opcode & 0x00F0

                # FX15
                if param == 0x0010:
                    # set the delay timer to VX
                    x = (opcode & 0x0F00) >> 8
                    vx = self.v[x]
                    self.delay_timer = vx
                    self.pc += 2

                # FX55
                elif param == 0x0050:
                    # store V0 to VX (including VX) in memory starting at
                    # address I
                    # [LEGACY] I is set to I + X + 1 after operation
                    x = (opcode & 0x0F00) >> 8
                    for idx in range(x + 1): # +1 for inclusive
                        self.memory[self.i + idx] = self.v[idx] & 0x00FF
                    # self.i = (self.i + x + 1) & 0x000FFFF # legacy
                    self.pc += 2

                # FX65
                elif param == 0x0060:
                    # fill V0 to VX (including VX) with values from memory
                    # starting at address I
                    # [LEGACY] I is set to I + X + 1 after operation
                    x = (opcode & 0x0F00) >> 8
                    for idx in range(x + 1): # +1 for inclusive
                        self.v[idx] = (self.memory[self.i + idx]) & 0x000FF
                    # self.i = (self.i + x + 1) & 0x000FFFF # legacy
                    self.pc += 2

            # FX18
            elif param == 0x0008:
                # set the sound timer to VX
                x = (opcode & 0x0F00) >> 8
                vx = self.v[x]
                self.sound_timer = vx
                self.pc += 2

            # FX1E
            elif param == 0x000E:
                # add VX to I
                x = (opcode & 0x0F00) >> 8
                vx = self.v[x]
                self.i = (self.i + vx) & 0x00FFFF # TODO is modulo here correct or not? test rom only passes without modulo. why??
                self.pc += 2

            # FX29
            elif param == 0x0009:
                # set I to the location of the sprite for the character in VX
                # characters 0-F are represented by a 4x5 font
                x = (opcode & 0x0F00) >> 8
                vx = self.v[x]
                self.i = (vx * 5) & 0x000FFFF  # times 5 because each char is 5 long
                self.pc += 2

            # FX33
            elif param == 0x0003:
                # Stores the binary-coded decimal representation of VX.)
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
            self.rom_path = self.rom_path_none_selected

        # programs start at 0x200 in memory
        i = 0x200
        with open(self.rom_path, "rb") as f:
            byte = f.read(1)
            while byte:
                self.memory[i] = int.from_bytes(byte, "big", signed=False)
                i += 1
                byte = f.read(1)

    def change_rom(self):
        self.init_system()
        self.rom_path = None
        self.load_rom()

    def handle_events(self):
        for event in pygame.event.get():

            if event.type == QUIT:
                self.running = False

            elif event.type == KEYDOWN:

                if event.key == K_ESCAPE:
                    self.running = False
                elif event.key == K_F1:
                    # change rom
                    self.change_rom()
                    pass
                elif event.key == K_F2:
                    # reboot
                    self.reboot()
                    pass
                elif event.key == K_F3:
                    # pause/unpause
                    self.paused = not self.paused
                    self.screen.show_paused(self.paused)
                    pass
                elif event.key == K_F4:
                    # dump screen to file
                    fname = self.screen.dump()
                    print(f"dumped screen to {fname}")
                    pass
                elif event.key == K_F5:
                    # dump memory and registers to file
                    fname = self.dump()
                    print(f"dumped memory and registers to {fname}")
                    pass

                if event.key == K_1:
                    self.keys[0x1] = True
                elif event.key == K_2:
                    self.keys[0x2] = True
                elif event.key == K_3:
                    self.keys[0x3] = True
                elif event.key == K_4:
                    self.keys[0xC] = True

                elif event.key == K_q:
                    self.keys[0x4] = True
                elif event.key == K_w:
                    self.keys[0x5] = True
                elif event.key == K_e:
                    self.keys[0x6] = True
                elif event.key == K_r:
                    self.keys[0xD] = True

                elif event.key == K_a:
                    self.keys[0x7] = True
                elif event.key == K_s:
                    self.keys[0x8] = True
                elif event.key == K_d:
                    self.keys[0x9] = True
                elif event.key == K_f:
                    self.keys[0xE] = True

                elif event.key == K_z:
                    self.keys[0xA] = True
                elif event.key == K_x:
                    self.keys[0x0] = True
                elif event.key == K_c:
                    self.keys[0xB] = True
                elif event.key == K_v:
                    self.keys[0xF] = True
            elif event.type == KEYUP:

                if event.key == K_1:
                    self.keys[0x1] = False
                elif event.key == K_2:
                    self.keys[0x2] = False
                elif event.key == K_3:
                    self.keys[0x3] = False
                elif event.key == K_4:
                    self.keys[0xC] = False

                elif event.key == K_q:
                    self.keys[0x4] = False
                elif event.key == K_w:
                    self.keys[0x5] = False
                elif event.key == K_e:
                    self.keys[0x6] = False
                elif event.key == K_r:
                    self.keys[0xD] = False

                elif event.key == K_a:
                    self.keys[0x7] = False
                elif event.key == K_s:
                    self.keys[0x8] = False
                elif event.key == K_d:
                    self.keys[0x9] = False
                elif event.key == K_f:
                    self.keys[0xE] = False

                elif event.key == K_z:
                    self.keys[0xA] = False
                elif event.key == K_x:
                    self.keys[0x0] = False
                elif event.key == K_c:
                    self.keys[0xB] = False
                elif event.key == K_v:
                    self.keys[0xF] = False

def main():
    emu = Chip8()

    # emu.rom_path = "BC_test.ch8"
    # emu.rom_path = "roms/Space Invaders [David Winter].ch8"
    # emu.rom_path = "roms/Chip8 Picture.ch8"
    # emu.rom_path = "roms/Brix [Andreas Gustafsson, 1990].ch8"

    emu.load_rom()
    emu.start()


if __name__ == "__main__":
    main()
