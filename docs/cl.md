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
progname.exe -arg value /arg2 "value two"
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
```
progname.exe -arg1 "C:\SOMEFILE.TXT" "SOME VALUE"
```
We can combine names and positional parameters in our command line arguments, like so:
```python    
arg = clArg()

# Get positional arguments by [ordinal]
print(arg.args()[0]) = "SOME VALUE"

# Get a named argument, with alternate param names.
print(arg.byName(['arg1','a1'])) = "C:\SOMEFILE.TXT"
	
```

### Using in a service.
Note when using this clArg in the service context, you need to pass the args paramater of the service constructor as a paramater to clArg.
```python
class MyService(win32serviceutil.ServiceFramework):
    
    def __init__(self,args):
			
		a = clArg(args=args)
	
```

## folderWatch:

This package checks a folder for files:
- in the specified folder
- of a specified type
- that are not open in the file system (i.e. still being written to)

### Construct a folderWatch
```python
    fs = folderWatch(
	   folder="M:\\python\\apy\\SolidWorks\\" ,  	## The folder to monitor
	   ext="xml" ,					## For files of type
	   handler="M:\\python\\apy\\solidworks.exe" , 	## Run this handler exe
	   env="wlnd"  					## And pass this -env parameter
        
    )
```

### The check() method
Then we can run the check method to check for new files in the specified folder. 

Optionally, we can also specify the current working directory, which passes a -cwd parameter to the handler, so that the handler uses the services setting files and /log.
```python
fs.check({current_working_directory})

```

For each file found by the folderWatch, we want to run the handler exe with the following parameters:
- the file found
- the -env environment
And then move the file to the /log after processing

The check method spawns a handler process for each file found.
```python	   	
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
The subprocess call runs the the handler program with a shell command like:
```
{hander_exe} -e {environment} -cwd {current_working_directory} {file_to_process}, 
```
e.g.:
```
\\walrus\nas\PriorityMobile\python\apy\solidworks.exe -e wlnd -cwd C:\pyedi\ \\walrus\nas\PriorityMobile\python\apy\SolidWorks\example.xml
```

## Moving the processed file to the /log
Then folderWatch uses the **logFile** method of the [logging package](log.md "logging package") to move the processed file to the \log folder.
```python
            self.log.logFile(self.filePath(f))

```