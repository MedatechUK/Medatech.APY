# cl.py

This package contains commandline utilities.

## Imports
```python
from MedatechUK.cl import folderWatch , clArg

```

## clArg:
This package extends the [sys.argv](https://docs.python.org/3/library/sys.html "sys.argv") function in Python, for capturing parameters from the command line.

A named argument can be passed with a - or / prefixed key. 
```
progname.exe -arg value -arg2 "value two"
```

These are accessed by the .byName() method, which accepts an array of possible nameS:
```
arg.byName(['arg','a']) = "value"
arg.byName(['arg2','a2']) = "value two"
```

We can also pass unNamed arguments:
```
progname.exe "C:\SOMEFILE.TXT" "SOME VALUE"
```

These are accessed by the .args() method:
```
arg.args()[0] = "C:\SOMEFILE.TXT"
arg.args()[1] = "SOME VALUE"
```

And we can combine both types.
```python    
    arg = clArg()
	
	# Read command line paramaters as a kwargs.
    print(arg.kwargs())
	
	# Get unnamed arguments by [number]
    print(arg.args()[0])
	
	# Get a named argument, with alternate param names.
    print(arg.byName(['arg1','a1']))
	
```

## folderWatch:

This package checks a folder for files:
- in the specified folder
- of a specified type
- that is not open by the flie system

For each file found:
- we run the handler.exe with:
	- the file found
	- set environment
	
```python
    fs = folderWatch(
        folder="M:\\python\\apy\\SolidWorks\\" , 
		ext="xml" ,
        handler="M:\\python\\apy\\solidworks.exe" , 
        env="wlnd"  
        
    )
```

Then we can run the check method to process the folder.
```python	
    fs.check()
	
```