#pythonProp (3)
This folder is uded to contain code being tested as part of the porting exercise to move pythonProp tools to Python 3.  As part of this exercise, it is planned to refactor the code into a more modular structure, abstracting the file parsing from the graphical presentation, in order to support output from additional propagation engines.

##Developer Notes
The area file being used to test the plotting routine is around 40MB and contains 583490 of (mainly) CSV text.  The size of this file is theoretically unbounded so we need to make sure that we're not trying to read the whole file into memory.  A line-by-line approach may be more appropriate as we're not particuarly interested in speed (these files will be prepared once a month).
