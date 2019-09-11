import tkinter
import pygame
from pygame.locals import *
import csv


class Screen:

    def __init__(self):

        # screen sizes
        self.x_size = 64
        self.y_size = 32

        self.upscaling = 10
        self.window = None

        # sizes for window to be displayed
        self.window_size_x = 0
        self.window_size_y = 0

        self.margin_x = 200
        self.margin_y = 105

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

        self.window = pygame.display.set_mode(
            (self.window_size_x, self.window_size_y), RESIZABLE)

        pygame.draw.lines(
            self.window,
            self.white,
            False,
            [
                (0, self.y_size*self.upscaling),
                (self.x_size*self.upscaling, self.y_size*self.upscaling),
                (self.x_size*self.upscaling, 0)
            ]
        )

        self.memY = self.initCommands()
        self.refresh()

    def dump(self):

        fname = "dump_screen.csv"        
        transposed = list(zip(*self.pixels))

        with open(fname, 'w') as f:
            writer = csv.writer(f, delimiter=' ')
            writer.writerows(transposed)

        return fname


    def clear(self):
        # pixels[x][y]
        self.pixels = [[0]*self.y_size for i in range(self.x_size)]

    def initCommands(self):

        # Initial X is on the right of the game screen
        initialX = self.x_size * self.upscaling + 10
        x = initialX 									# Sets the X cursor to the initial X value
        y = 10 											# Y cursor is on the top of the window

        # We draw the commands text and move the Y cursor by the text's size
        y += self.drawText("ESC: Quit", x, y)[1]
        y += self.drawText("F1: Change ROM", x, y)[1]
        y += self.drawText("F2: Reboot ROM", x, y)[1]
        y += self.drawText("F3: Pause / Unpause", x, y)[1]
        y += self.drawText("F4: Next step", x, y)[1]
        y += self.drawText("F5: Sound ON / OFF", x, y)[1]

        y += 10 																	# Move the cursor 10px downward
        pygame.draw.line(
            self.window,
            self.white,
            (x, y),
            (self.window_size_x - 10, y)) 	# To draw a separation line between commands and memory which is under

        return y+10 	# Return the Y position 10px under our drawn line

    def drawText(self, text, X, Y):  # Draw a text at X and Y position, and returns the size it takes

        # Renders the text and adds it to the window
        self.window.blit(self.font.render(text, True, self.white), (X, Y))
        return self.font.size(text) 										# Returns the text size

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
            elif event.type == QUIT:
                running = False

        x.refresh()
    x.destroy()


if __name__ == "__main__":
    main()
