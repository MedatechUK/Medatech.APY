# cl.py

This package contains commandline utilities.

## Imports
```python
from MedatechUK.cl import folderWatch , clArg

```

## clArg:
This package extends the [sys.argv](https://docs.python.org/3/library/sys.html "sys.argv") function in Python, for capturing parameters from the command line.

### Named Arguments
A named argument can be passed with a - or / prefixed key. 
```
progname.exe -arg value -arg2 "value two"
```

These are accessed by the .byName() method, which accepts an array of possible names:
```
arg.byName(['arg','a']) = "value"
arg.byName(['arg2','a2']) = "value two"
arg.byName(['arg3','a3']) = None
```
Note that a missing argument returns None.

### Positional Arguments
We can also pass positional arguments:
```
progname.exe "C:\SOMEFILE.TXT" "SOME VALUE"
```

These are accessed by the .args() method:
```
arg.args()[0] = "C:\SOMEFILE.TXT"
arg.args()[1] = "SOME VALUE"
```

### Combining named and positional arguments
```python    
arg = clArg()

# Read command line paramaters as a kwargs.
print(arg.kwargs())

# Get unnamed arguments by [number]
print(arg.args()[0])

# Get a named argument, with alternate param names.
print(arg.byName(['arg1','a1']))
	
```

### Using in a service.
When using this clArg in a service, you need to pass the args paramater of the service constructor as a paramater to clArg.
```python
class MyService(win32serviceutil.ServiceFramework):
    
    def __init__(self,args):
		
		a = clArg(args=args)
	
```

## folderWatch:

This package checks a folder for files:
- in the specified folder
- of a specified type
- that is not open by the file system	
```python
    fs = folderWatch(
		folder="M:\\python\\apy\\SolidWorks\\" , 
		ext="xml" ,
		handler="M:\\python\\apy\\solidworks.exe" , 
		env="wlnd"  
        
    )
```
Then we can run the check method to process the folder. For each file found:
- we run the handler.exe with:
	- the file found
	- set environment
	- log the file
```python	
    fs.check()
	
    def check(self, cwd):
        for f in self.files():   
            self.log.logger.debug(               
                self.CMD(cwd , f)
            )         
						
            subprocess.call(
                self.CMD(cwd , f)
                , shell=False
            )	
```
The subprocess call runs the following statement:
			
```
\\walrus\nas\PriorityMobile\python\apy\solidworks.exe -e wlnd -cwd C:\pyedi\ \\walrus\nas\PriorityMobile\python\apy\SolidWorks\example.xml
```

Then we use the **logFile** method of the [logging package](log.md "logging package") to move the file to the \log folder.
```python
		self.log.logFile(self.filePath(f))

```