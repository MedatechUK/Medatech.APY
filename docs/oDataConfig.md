# oDataConfig.py

Load a configuration file containg settings for connecting to Priority oData. This may be either from:
- the IIS web.config file
- a file called constants.py in the PATH folder.

This package standardises the required settings for connecting to priority oData, and can be used in:
- a web handler (where these settings are stored in the website configuration) 
- a command line (where these settings are stored in a file called constants.py in the PATH directory of your project).

## Imports
```python
	from MedatechUK.oDataConfig import Config
```

## Method: Config(env=ENVIRONMENT , path=PATH) RETURNS a Config Object
```python
    Config(
        env=request.environment , 
        path=os.getcwd()
    )   
	
```
| Property      |Description                            |
|---------------|---------------------------------------|
| ENVIRONMENT        |The SQL Database name of the Priority Company  |
| PATH	|The location of the web.config or constants.py setting.|
||Use path=os.getcwd() to use the current working directory at runtime.|s

## Config Object
| Property      |Description                            |
|---------------|---------------------------------------|
| oDataHost     | The URL of the oData service, eg: https://walrus.ntsa.uk |
| tabulaini     | The tabula.ini file to use for the connection |
| ouser         |The oData user, with API licence|
| opass         |The oData passsword|
| connstr       |The database connection string (to validate the environment).|