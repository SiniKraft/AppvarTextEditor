# AppvarTextEditor
This utility is designed to make developping Programs on the [TI 83 Premium CE](https://en.wikipedia.org/wiki/TI-83_Premium_CE) / [TI 84 Plus CE](https://en.wikipedia.org/wiki/TI-84_Plus_series#TI-84_Plus_CE_and_TI-84_Plus_CE-T) easier !  
The TI only has 256ko RAM and only 156ko is usable by your program (nearly 100ko is used by the system)  
A lot of utilities already exists to keep the programm's size as small as possible.  
**And here's come AppvarTextEditor !**  
Strings can take a lot of space in your program.  
ATE allows you to store a lot of text without increasing the program's size !  
## How ?
You can store any data on an AppVar (files on the calculator) including strings.  
But, if the file is stored in the Archive (FLASH), you don't need any extra RAM to read the data !  
- ATE provides you two C sources you can easily include in your program which provides ONE fuction to load a string!  
- ATE has a **graphical interface** to make the creation of these Appvars easier : edit text, import and export easily on your PC!  
You can even preview the default GFX font or use your own !
## Get Started
Start by adding these two files into your project : [string_loader.c](https://github.com/SiniKraft/AppvarTextEditor/blob/master/string_loader.c) and [string_loader.h](https://github.com/SiniKraft/AppvarTextEditor/blob/master/string_loader.h).  
Then add, at the beginning of you source code ``#include "string_loader.h"`` where you need to get your strings.
You just have to use the function ``get_string_pointer(const char file_name[9], const uint8_t index, const uint8_t header_string_length)`` :  
- ``file_name`` : AppVar on calc's name
- ``index`` : 0-255 index of the string to get (0 is first, 1, 2, ...)
- ``header_string_length`` : Can be 0 if no header string has been specified in ATE, or the length of the header string (not including \0 null terminator)  

<!-- end of the list -->

This functions returns a pointer of the desired string which can be used directly.
NOTE : 
- If the Appvar is in Archive (recommended), the pointer returned by this function is **READ ONLY** !  
Trying to write data at this pointer will causes a RAM reset and restarts the device !
- The pointer returned MAY BE NULL, expecially if the file doesn't exist !
- The function has been built to be the most optimized way, so it doesn't check if the index or header length passed are correct ! Putting wrong data in it will get the pointers corrupt !

<!-- end of the list -->

Here's an example of how it works :  
![ATE Explained.png](https://raw.githubusercontent.com/SiniKraft/AppvarTextEditor/master/ATE%20Explained.png)
# Using the ATE app
Designed to make adding or editing strings easily !
Go into the [releases](https://github.com/SiniKraft/AppvarTextEditor/releases) to install now !  
If you want to run it without installing, simply download and extract source code,  
make sure you meet the requirements (python 3 with PySide2) and run main.py !  
Once you  managed to run the app, and add a few lines of text, you can then save your work and File>Export it to save it as a 8xv !  
Then, just send this 8xv (Appvar) to your calculator !
