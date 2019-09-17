Write-up

Fun overall, main difficulties were the timing of the instructions and screen refreshing, and the actual screen drawing.
Minor difficulties ocurred when I discovered there are different specifications. This was when all opcodes were implemented but the roms didn't play correctly. Not the best surprise.

As for the timing, i couldn't get the correct screen refresh rate to work with the time.sleep() method, only pygame's time.delay() method. This deserves some further looking into, especially after I saw that the Octo IDE offers different cycles/frame speeds when running roms.

Overall a fun project, though debugging was kinda tedious.

Possible improvements:
* adjust cycles/frame speed
* offer upscaling option
