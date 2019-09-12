# Chip8 Emulator in Python

# Keyboard

| 1 | 2 | 3 | C | → | 1 | 2 | 3 | 4 |
|---|---|---|---|----|---|---|---|---|
| 4 | 5 | 6 | D | → | q | w | e | r |
| 7 | 8 | 9 | E | → | a | s | d | f |
| A | 0 | B | F | → | z | x | c | v |

# Run

`python chip8/chip8.python`

# Ressources used
## Legacy
1. http://mattmik.com/files/chip8/mastering/chip8.html
2. http://www.cs.columbia.edu/~sedwards/classes/2016/4840-spring/designs/Chip8.pdf

## 2005
3. http://www.multigesture.net/articles/how-to-write-an-emulator-chip-8-interpreter/
4. http://devernay.free.fr/hacks/chip8/C8TECH10.HTM
5. https://en.wikipedia.org/wiki/CHIP-8

Note that the legacy resources reference the implementation from 1970. Most games written post 2005 use the new implemtation as described by Cowgod (4.)<sup>1</sup>.

Example: 8XY6

Legacy: Set VF = LSB(VY), then set VX = VY / 2

2005: Set VF = LSB(VX), then set VX = VX / 2

This project uses the 2005 implementation.

<sup>1</sup>https://www.reddit.com/r/EmuDev/comments/8cbvz6/chip8_8xy6/?utm_source=share&utm_medium=web2x
