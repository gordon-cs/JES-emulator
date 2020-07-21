# jes4py - a JES emulator for Python 3

[**JES**](https://github.com/gatech-csl/jes), the Jython Environment for Students, is an educational IDE used in the Media Computation curriculum developed by Mark Guzdial and Barbara Ericson at Georgia Tech. More details on the curriculum are available at http://www.mediacomputation.org/.  

[**Jython**](https://www.jython.org/) is a Java implementation of Python 2.x and was designed to allow rapid application development and scripting access to Java functionality.

The **jes4py** implements a subset of JES features that can be used in Python 3.x scripts.  The goal is to provide the pedogocial assets of JES without requiring Jython or needing to use JES's IDE.

## Prerequisites
1. An IDE (Integrated Development Environment) of your choice
    - [**Visual Studio Code**](https://code.visualstudio.com/) is recommended if you have no preference.
2. [**Python**](https://www.python.org/downloads/) 3.x Installed
3. **A Supported OS**:  Windows, Linux, macOS


## Installation of Dependencies

Several dependencies need to be installed before you can use jes4py:
* PIL (the Python Image Library) or Pillow (an updated fork of PIL)
* wxPython (GUI toolkit for the Python language)
* Simpleaudio (Audio toolkit for Python 3)

Instructions to do this are OS-dependent:

### Windows

Note: The pip and python command may vary between platforms and Python versions. Substitute the correct one for usages in these examples. Some possible variants are: python, python3, pip, pip3 and pip3.x

The following Python packages must be installed:

Simpleaudio
```
pip install simpleaudio
```

wxPython
```
pip install -U wxPython
```

Pillow (PIL: the Python Imaging Library)
* (This normally comes with wxPython so you should not need to install it separately)


### Mac OS-X

Note: The pip and python command may vary between platforms and Python versions. Substitute the correct one for usages in these examples. Some possible variants are: python, python3, pip, pip3 and pip3.x

Simpleaudio
```
pip install simpleaudio
```

wxPython
```
pip install -U wxPython
```

Pillow (PIL: the Python Imaging Library)
* (This normally comes with wxPython so you should not need to install it separately)

### Linux

Note: The pip and python command may vary between platforms and Python versions. Substitute the correct one for usages in these examples. Some possible variants are: python, python3, pip, pip3 and pip3.x
```
python3 -m pip install --upgrade pip
python3 -m pip install --upgrade simpleaudio
python3 -m pip install --upgrade wx
python3 -m pip install --upgrade Pillow
```

## Using jes4py

Users should include the following line at a Python 3.x command prompt
or in a Python 3.x script to make use of JES functions"
```
from jes4py import *
```
