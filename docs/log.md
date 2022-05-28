# mLog

This package extends the basic python logger by creating a single log file per day and adding stack information to the log. 

This prevents log files becoming unusable due to size and is useful for issue tracing.

## Imports
```python
	from MedatechUK.mLog import mLog
```

## Creating a log
```python
    log = mLog()
    log.start( os.getcwd(), "DEBUG" )
    log.logger.debug("Starting {}".format(__file__))     
	
```
## Methods

### log.start( {Log Location} , {VERBOSITY} )

Use the start method ONCE, to initiaklise your log. 

| Property      |Description                            |
|---------------|---------------------------------------|
| Log Location        |The folder in which to store log files   |
| Verbosity	|The Verbosity of the log decides which messages are stored to the log (see Verbosity Settings below)|

### log.logger.{VERBOSITY}(Message)

Once initialised you can use the log.logger.{VERBOSITY} method anywhere on your code.

| Property      |Description                            |
|---------------|---------------------------------------|
| Verbosity	|The Verbosity of the message (see Verbosity Settings below) |
| Message	|The text to be written to the logfile |

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