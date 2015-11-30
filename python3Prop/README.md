#pythonProp (3)
This folder is uded to contain code being tested as part of the porting exercise to move pythonProp tools to Python 3.  As part of this exercise, it is planned to refactor the code into a more modular structure, abstracting the file parsing from the graphical presentation, in order to support output from additional propagation engines.

##Developer Notes
The area file being used to test the plotting routine is around 40MB and contains 583490 of (mainly) CSV text.  The size of this file is theoretically unbounded so we need to make sure that we're not trying to read the whole file into memory.  A line-by-line approach may be more appropriate as we're not particuarly interested in speed (these files will be prepared once a month).

##Installing and Running ITUHFPROP on Linux
The following procedure has been tested on Fedora 23.
Install wine with the command
    sudo dnf install wine
Create a directory 'iturec533' in your home folder
    mkdir ~/iturec533
Download the zip file containing the Windows binary from [https://www.itu.int/oth/R0A0400006F/en](https://www.itu.int/oth/R0A0400006F/en)
Extract the contents of the file into your iturec533 folder;
    unzip ./R0A0400006F0001ZIPE.zip -d ~/iturec533/

###Input file filepaths
The Bin directory contains a sample input file.  Replace the sample file paths (e.g. c:\provide_full_path_to\Reports\) with working filepaths.
    DataFilePath "\home\jwatson\iturec533\Data\"
Note that the antenna file path may also need to be changed to one that is available in your Data/Antenna directory.

###Running the Application
Run the application with the following command
    wine ./ITURHFProp.exe itu.in itu.out
