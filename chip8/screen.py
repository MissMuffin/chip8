import tkinter
import pygame
from pygame.locals import *
import csv


class Screen:

    def __init__(self):

        self.x_size = 64
        self.y_size = 32

        self.upscaling = 10
        self.window = None

        self.window_size_x = 0
        self.window_size_y = 0

        self.margin_x = 0
        self.margin_y = 70

        # colors for pygame
        self.white = (255, 255, 255)
        self.black = (0, 0, 0)

        self.pixels = None
        self.clear()

        pygame.init()
        self.font = pygame.font.Font(pygame.font.get_default_font(), 14)

    def start(self):

        self.window_size_x = (self.x_size * self.upscaling) + self.margin_x
        self.window_size_y = (self.y_size * self.upscaling) + self.margin_y

        pygame.display.set_caption("Chip8 Emulator")

        self.window = pygame.display.set_mode((self.window_size_x, self.window_size_y), RESIZABLE)

        self.show_menu()

    def clear(self):
        # pixels[x][y]
        self.pixels = [[0]*self.y_size for i in range(self.x_size)]

    def dump(self):

        fname = "dump_screen.csv"        
        transposed = list(zip(*self.pixels))

        with open(fname, 'w') as f:
            writer = csv.writer(f, delimiter=' ')
            writer.writerows(transposed)

        return fname

    def show_menu(self):

        # erase entire pygame surface
        pygame.display.get_surface().fill(pygame.Color("black"))

        x = 20
        y = self.y_size * self.upscaling + 20

        offset_x = x
        offset_y = y

        pygame.draw.line(
            self.window,
            self.white,
            (0, self.y_size * self.upscaling),
            (self.window_size_x, self.y_size * self.upscaling)
        )

        offset_y += self.render_text("ESC: Quit", offset_x, offset_y)[1]
        offset_x += self.render_text("F1: Change ROM", offset_x, offset_y)[0]

        offset_y = y
        offset_x += 30
        offset_y += self.render_text("F2: Reboot ROM", offset_x, offset_y)[1]
        offset_x += self.render_text("F3: Pause / Unpause", offset_x, offset_y)[0]

        offset_y = y
        offset_x += 30
        offset_y += self.render_text("F4: Dump screen", offset_x, offset_y)[1]
        offset_x += self.render_text("F5: Dump memory & registers", offset_x, offset_y)[0]

        self.refresh()

    def show_paused(self, paused):

        if paused:
            text = "PAUSED"
            size = self.font.size(text)
            x = self.window_size_x - size[0]
            y = self.window_size_y - size[1]
            self.window.blit(self.font.render(text, True, self.white), (x, y))
            self.refresh()
        else:
            self.show_menu()


    def render_text(self, text, x, y):

        self.window.blit(self.font.render(text, True, self.white), (x, y))
        return self.font.size(text)

    def refresh(self):
        for x in range(self.x_size):
            for y in range(self.y_size):

                col = self.black
                if self.pixels[x][y] == 1:
                    col = self.white

                pygame.draw.rect(
                    self.window,
                    col,
                    (
                        self.upscaling * x,
                        self.upscaling * y,
                        self.upscaling,
                        self.upscaling
                    )
                )
        # update full display
        pygame.display.flip()

    def destroy(self):
        pygame.quit()

def main():
    x = Screen()
    x.start()
    running = True
    while running:

        pygame.event.pump()

        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
                elif event.key == K_F3:
                    # toggle pause
                    x.show_paused()
            elif event.type == QUIT:
                running = False

        x.refresh()
    x.destroy()


if __name__ == "__main__":
    main()
