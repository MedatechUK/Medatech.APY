# oDataConfig.py

This package returns a Config Object containinig settingd for Priority Odata.

It loads a configuration file containg the oData settings from *either*:
- the IIS web.config file
- a file called constants.py in the PATH folder.

This package standardises the storage of required settings for connecting to priority oData, and can be used in:
- a web handler (where these settings are stored in the website configuration) 
- a command line (where these settings are stored in a file called constants.py in the PATH directory).

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
||Use path=os.getcwd() to use the current working directory at runtime.|

## Config Object
| Property      |Description                            |
|---------------|---------------------------------------|
| oDataHost     | The URL of the oData service, eg: https://priority.ntsa.uk |
| tabulaini     | The tabula.ini file to use for the connection |
| ouser         |The oData user, with API licence|
| opass         |The oData passsword|
| connstr       |The database connection string (to validate the environment).|

## Example \web.Config
```xml
  <appSettings>
    <add key="oDataHost" value="https://priority.someurl" />
    <add key="tabulaini" value="***********" />
    <add key="ouser" value="***********" />
    <add key="opass" value="***********" />
  </appSettings>
  <connectionStrings>
    <add connectionString="Server=127.0.0.1\PRI,1433;Trusted_Connection=Yes;MultipleActiveResultSets=true;" name="priority" />

  </connectionStrings>
```  

## Example \constants.py
```python
oDataHost ="priority.someurl"
tabulaini ="***********"
ouser ="***********"
opass ="***********"    
connStr="Server=127.0.0.1\PRI,1433;Trusted_Connection=Yes;MultipleActiveResultSets=true;"
```
