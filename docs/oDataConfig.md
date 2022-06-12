# [oDataConfig.py](../package/src/MedatechUK/oDataConfig.py "oDataConfig.py")

This package returns a **Config Object** containing settings for Priority Odata.

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

## Methods
### Config(env=ENVIRONMENT , path=PATH) RETURNS a Config Object
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

### CheckEnviroment() 
(added 0.0.20)
Returns a boolean indicating if the configurations environment is valid.
```
if self.environment != "" and self.cont() :   
    ## Is it a valid environment?
    if not self.config.CheckEnviroment():
        self.log.logger.critical("Invalid environment {}".format(self.config.environment))
        self.Response.Status = 500
        self.Response.Message = "Internal Server Error"
        self.Response.data = {"error" : "Invalid environment [{}]".format(self.config.environment)} 
		
```

### cnxn()
(added 0.0.20)
Returns a pyodbc connection using the detaiuls in the config file:
```python
cnxn = self.config.cnxn()
crsr = cnxn.cursor()

```

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
