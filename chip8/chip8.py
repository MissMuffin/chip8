import tkinter
from tkinter.filedialog import askopenfilename
from screen import Screen
import pygame
from pygame.locals import *
from utils import Utils

class Chip8:

    def __init__(self):

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

        # self.screen.clear() # TODO does this work here?

    def load_font(self):
        # load font set into memory
        # first 80 elements of memory will be font set
        for i, val in enumerate(Utils.get_font()):
            self.memory[i] = val

    def start(self):
        # self.load_rom(self.rom_path)
        self.screen.start()
        self.running = True

        while self.running:
            
            self.listen()

            self.screen.refresh()
            # self.dispatch_event()
            # current_opcode = self.get_current_opcode()
            # self.execute_opcode(current_opcode)
            # timer delay

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

    def listen(self):
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.running = False
            elif event.type == QUIT:
                self.running = False

def main():
    emu = Chip8()
    
    emu.rom_path = "BC_test.ch8"
    i = 0x200
    with open(emu.rom_path, "rb") as f:
        byte = f.read(1)
        while byte:
            emu.memory[i] = int.from_bytes(byte, "big", signed=False)
            i += 1
            byte = f.read(1)


    emu.start()

if __name__ == "__main__":
    main()