# Max Skinning Weight Tool for Maya![GitHub Logo](/icons/weight_tool.png)

This is a python tool similar to the weight tool in 3DSMAX. A model can be skinned using this script without using the maya paint tool. This script provides tools to select vertices and assign them weights. You can also copy, paste, and blend weights between vertices. Each vertex you select displays the objects contributing to its weighting in the dialog list.

Important: The controls on this dialog adjust vertex weighting with respect to the active bone; that is, the object highlighted in the Skin Joint list . When you select a vertex and then change its weighting, if the active bone does not already influence the vertex, the bone is added to the list of bones influencing the vertex. You can ensure that bone assignments don't change by highlighting the bone in the Weight Tool dialog list after selecting the vertex and before changing weighting. Also, the total weighting for all bones influencing a vertex is always 1.0, so if multiple bones influence a vertex and you change the weight value for one bone, the weight values for the others change as well.

Your Tool will be activated only in vertex mode and on a valid skinned mesh..

![GitHub Logo](/images/max_weight_tool.PNG)


# Features!

  - Adjust weights to vertices using preset buttons on the UI like 3dsmax
  - Transfer skin from one valid skinned object to another.
  - This tool has been refactored to python from the original mel tool
  - Load and Save skin data on selected mesh

This is a video demo from the old mel tool. https://youtu.be/UBhhcFxvHTg?t=41

[![Link to video](https://img.youtube.com/vi/UBhhcFxvHTg/0.jpg)](https://youtu.be/UBhhcFxvHTg?t=41)

## Installation

The Skinning Tool has been tested for Maya 2017 and above

```sh
# Copy the below script into your maya shelf through the script editor
# Make sure to replace the correct path into the 'path' variable

import sys
path = 'PATH_TO_TOOL/max-skinning-weight-tool/' #eg path = 'd:/max-skinning-weight-tool/'
sys.path.append(path)
import weight_tool as wt
wt.show()
```
## File structure
```
+ max-skinning-weight-tool/
|           (The main folder with all the scripts)
+-- __init__.py
|           
+-- weight_tool.py
|           The QWidget class with start() function to load the tool in maya
+-- config.py
|           Contains Tool name, version and paths
+-- core/
|   +-- ui_function.py
|           Contains QT functions for wrapping widget to maya and loading .ui file
|   +-- utilities.py
|           Contains functionality to get information required for the tool
|   +-- __init__.py
|           
+-- icons/ 
|   +-- weight_tool.png
| 
+-- images/ 
|   +-- max_weight_tool.png
|   +-- old_max_weight_tool.png
+-- ui/
|   +-- weight_tool.ui
|           The main ui file done using Qt Designer and also has stylesheet applied
```     

## History

This tool was originally developed by me way back in the late 2000 using MEL scripts and published on creativecrash (highend3d)
![GitHub Logo](/images/old_max_weight_tool.PNG) 
04.01.2020 - Added Load and Save skin weight feature on selected mesh from/to a specified directory

| Tool | Link |
| ------ | ------ |
| MAX Skinning Weight Tool for maYa 1.1.0 | https://www.highend3d.com/maya/script/max-skinning-weight-tool-for-maya |

## Todos

 - Check skin influence and change max skin vertex weight info

License
----

MIT


**Free Tool, Enjoy!**
