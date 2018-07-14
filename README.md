RICOCHET ROBOT - PERIODIC EDITION
===============================

This is a python only robot solver with bumpers, optional silver robot, 
new robot and periodic board boundaries.

Requirements
------------
- Python 3.6+
- wxPython 4+

Installation
------------
Should run with Anaconda python distro with `conda install wxpython`

Launch the program with: python main_set.py

Option
- Random Seed (int)
- Periodic Boundaries (0 or 1)
- Number of Robots (4 or 5)
- Boards like (B3,R1,G4,Y3)

example:
```
python main_set.py 42 1 5 B3,R1,G4,Y3
```

Controls
--------
To move a robot, select one by color and then use the arrow keys on the keyboard.

- R - Red
- G - Green
- B - Blue
- Y - Yellow
- L - Silver

Other program controls are listed below.

- N - Next Token
- S - Solve
- U - Undo
- Esc - Quit
