# mLog.py

This package extends the [basic python logger](https://docs.python.org/3/library/logging.html "basic python logger") by:
- Creating a single log file per day in the format log\YYYY-MM\YYMMDD.log 
- Adding stack trace information to the log 

This prevents log files becoming unusable due to size and is useful for issue tracing.

This logging package is used consisently throughout the other packages in this repository.

## Imports
```python
	from MedatechUK.mLog import mLog
```

## Creating a log
This example uses [Command Line Arguments](cl.md "Command Line Arguments") to set the current working directory -cwd.
```python
    log = mLog()    
    if arg.byName(["cwd" , "path"]) != None:
        if not exists(arg.byName(["cwd" , "path"])):
            raise NameError("Specified working directory {} is missing.".format(arg.byName(["cwd" , "path"])))
        else:
            os.chdir(arg.byName(["cwd" , "path"]))
    
    log.start( os.getcwd() , "DEBUG" )            
    log.logger.debug("Starting {}".format(__file__))     
	
```
## Methods

### log.start( {Log Location} , {VERBOSITY} )

Use the start method *ONCE*, to initialise your log. 

| Property      |Description                            |
|---------------|---------------------------------------|
| Log Location        |The folder in which to store log files   |
| Verbosity	|The Verbosity of the log decisdes which Logging Levels are recorded (see Verbosity Settings below)|

### log.logger.{VERBOSITY}("Message")

Once initialised you can use the log.logger.{VERBOSITY} method anywhere on your code (see Verbosity Settings below).

| Property      |Description                            |
|---------------|---------------------------------------|
| Verbosity	|The Logging Level of the message (see Verbosity Settings below) |
| Message	|The text to be written to the logfile |

### log.logfile( {file_name} )

After processing a file we often want to keep a copy of that file.

This method moves the file to the log in the format log\YYYY-MM\DD\{filename}{-suffix}.{extention}.

If the filename already exists, a numeric suffix is added to the filename before moving.

See also: This method is implimented by the [folderWatch contrl](cl.md "folderWatch contrl").

## Logging Level Verbosity

From [Python Docs](https://docs.python.org/3/library/logging.html#levels "Python Docs").

|Level|Numeric value|
|-----|-------------|
|CRITICAL|50|
|ERROR|40|
|WARNING|30|
|INFO|20|
|DEBUG|10|
|NOTSET|0|