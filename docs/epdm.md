# epdm.py

This package contains a deserialiser for EPDM (Sold Works) data.

The EDPM deserialiser, and the ECO() and ECOChild() classes shown below, inherit from the [Serial Class](serial.md "Serial Class").

See also: [Adding command line parameters to EPDM example](../transport/cl "Serial Class").

## Imports
```python
from MedatechUK.epdm import xmlTransactions

```

## Deserialse EPDM output:

EPDM data descibes a bill of materials, where each part can contain child parts in it's references node:
```xml
<xml>
  <transactions>
    <transaction date="1652880322" type="wf_export_document_attributes" vaultname="Testbox">
      <document aliasset="" id="BOM Test" idattribute="Number" idcfgname="Default" pdmweid="36368">
        <configuration name="Default" quantity="1">
          <attribute name="Number" value="BOM Test"/>
...
          <attribute name="Reference Count" value="1.0"/>
          <references>
            <document aliasset="" id="C200" idattribute="Number" idcfgname="Default" pdmweid="1016">
              <configuration name="Default" quantity="0.6">
                <attribute name="Number" value="C200"/>
...
                <attribute name="Reference Count" value="0.59999999999999998"/>
              </configuration>
            </document>
            <document aliasset="" id="EK960" idattribute="Number" idcfgname="Default" pdmweid="1327">
              <configuration name="Default" quantity="1">
                <attribute name="Number" value="EK960"/>
...
                <attribute name="Reference Count" value="1.0"/>
              </configuration>
            </document>
          </references>
        </configuration>
      </document>
    </transaction>
  </transactions>
</xml>

```

Using the epdm package we can [deserialise](serial.md "Serial Class") the EPDM data from a file, and begin stepping through the heirarachy of documets.
```python
if __name__ == '__main__':    
       
    try:
        with open('example.xml', 'r') as the_file:        
            q = xmlTransactions(_xml=the_file)
            for t in q.transactions:
                recurse(t.document)

    except Exception as e:
        log.logger.critical(str(e))
		
```

Then we recurse through the heirarchy until we have a part with no child parts, and work up from there.

This ensures child parts are created before their parent parts.
```python
def recurse(document):

    if len(document.configuration.references) > 0 :
        for d in document.configuration.references :
            recurse(d)
        readConfig(document.configuration)
    else:
        readConfig(document.configuration)  
		
```

Now, with our part, we create a [serial loading](serial.md "Serial Class") using the ECO() and any required ECOChild() classes, that we send to Priority.
```python
def readConfig(configuration):

    q = ECO(**configuration.kwargs())
    if len(configuration.references) > 0 :
        for s in configuration.references :
            q.child.append(ECOChild(**s.configuration.kwargs()))
    
    # Create an object to hold the result    
    r = Response()    
    # region Send to Priority
    q.toPri(                    # Send this object to Priority        
        Config(                 # Using this configuration
            env="wlnd" ,            # the Priority environment
            path=os.getcwd()        # the location of the config file
        ) , 
        q.toFlatOdata ,         # Method to generate oData Commands
                                    # toFlatOdata - send to oData load form
                                    # toOdata - send to nested Priority forms
                                    # OR a custom method.        
        response=r              # the apy request/response object. Use:
                                    # for command:      response=Response   (a new response is used)
                                    # for apy usage:    request=request     (the request.response is used)
    )

    #endregion
    
    # Display the result
    print( "[{}]: {}".format( r.Status , r.Message ))
    print( "response : " + json.dumps( r.data , sort_keys=False, indent=4 ))

```	

## Serialising EPDM transactions for Priority:

The ECO() and ECOChild() classes define what fields are sent to Priority.
See also: [Serial Class](serial.md "Serial Class").

### The ECO class
```python
class ECO(SerialBase):

    #region Properties
    @property
    def child(self): 
        return self._child
    @child.setter
    def child(self, value):
        self._child = []
        for i in range(len(value)):
            if len(value) > 1 :
                self._child.append(ECOChild(**value[i]))
            else :
                self._child.append(ECOChild(**value))

    @property
    def Number(self): 
        return self._Number
    @Number.setter
    def Number(self, value):
        self._Number = value    

... Other epdm properties

    #endregion

    #region "ctor"
    def __init__(self,  **kwargs): 

        #region "Property defaults"
        self._Number = ''        
        self._Part_Family = ''     
        self._Part_Type = ''
        self._Description = ''
        self._Buy__Sell_Unit = ''
        self._Reference_Count = 0.0
        self._Conversion_Ratio = 0.0
        self._Assigned_To = ''
        self._State = ''
        self._Code = ''
        self._Factory_Unit = ''
        self._ECO_Reason = ''
        self._ECO_Details = ''
        self._PDFLocation = ''
        self._Revision = ''
        self._child = []
        
        #endregion

        #region "Set Meta info"
        SerialBase.__init__(self , SerialF(fname="ZODA_TRANS", rt=1 , typename="SW") , **kwargs)  

        SerialT(self, "rt")
        SerialT(self, "bubbleid")
        SerialT(self, "typename")        
        SerialT(self, "Revision" , pCol="TEXT1" )
        SerialT(self, "Number" , pCol="TEXT2" )
        SerialT(self, "Description" , pCol="TEXT3" )
   
        #endregion
    
    #endregion
	
```
### The ECO child class
```Python	
class ECOChild(SerialBase):

    #region Properties
    @property
    def Number(self): 
        return self._Number
    @Number.setter
    def Number(self, value):
        self._Number = value    

... Other epdm properties

    #endregion

    #region "ctor"
    def __init__(self,  **kwargs): 

        #region "Property defaults"
        self._Number = ''        
        self._Part_Family = ''     
        self._Part_Type = ''
        self._Description = ''
        self._Buy__Sell_Unit = ''
        self._Reference_Count = 0.0
        self._Conversion_Ratio = 0.0
        self._Assigned_To = ''
        self._State = ''
        self._Code = ''
        self._Factory_Unit = ''
        self._ECO_Reason = ''
        self._ECO_Details = ''
        self._PDFLocation = ''
        self._Revision = ''
        
        #endregion

        #region "Set Meta info"
        SerialBase.__init__(self , SerialF(fname="child", rt=2 ) , **kwargs)  

        SerialT(self, "rt")
        SerialT(self, "Number" , pCol="TEXT1" )
        SerialT(self, "Reference_Count" , pCol="REAL1" , pType="REAL")            
   
        #endregion
    
    #endregion

```

## Program Log File

When we run the program we get the following [log file](log.md "logging").
```
08:43:15 DEBUG Solidworks.py Starting \\walrus\nas\PriorityMobile\python\apy\Solidworks.py
08:43:27 DEBUG Solidworks.py > oDataConfig.py Opening [\\walrus\nas\PriorityMobile\python\apy\web.config].
08:43:27 DEBUG Solidworks.py > Serial.py POSTing to [priority.ntsa.uk/odata/priority/tabula.ini/wlnd/ZODA_TRANS] 
08:43:27 DEBUG Solidworks.py > Serial.py Headers:
{
    "Authorization": "Basic YXBpdXNlcjoxMjM0NTY=",
    "Content-Type": "application/json",
    "User-Agent": "MedatechUK Python Client"
}
08:43:27 DEBUG Solidworks.py > Serial.py Data:
{
    "BUBBLEID": "267bb2c3-94f7-4618-96a9-d68fe75e1a30",
    "TYPENAME": "SW",
    "ZODA_LOAD_SUBFORM": [
        {
            "RECORDTYPE": "1",
            "TEXT2": "C200",
            "TEXT3": "EC Cramer CCC452",
            "TEXT1": "A03"
        }
    ]
}
08:43:31 DEBUG Solidworks.py > Serial.py [201] OK
08:43:31 DEBUG Solidworks.py > Serial.py PATCHing to [/odata/priority/tabula.ini/wlnd/ZODA_TRANS(BUBBLEID='267bb2c3-94f7-4618-96a9-d68fe75e1a30',LOADTYPE=10)] ... 
08:43:31 DEBUG Solidworks.py > Serial.py [200] OK
08:43:31 DEBUG Solidworks.py > Serial.py Result: {
    "@odata.context": "https://priority.ntsa.uk/odata/Priority/tabula.ini/wlnd/$metadata#ZODA_TRANS/$entity",
    "TYPENAME": "SW",
    "BUBBLEID": "267bb2c3-94f7-4618-96a9-d68fe75e1a30",
    "CREATEDATE": "2022-06-02T08:43:00+01:00",
    "COMPLETE": "Y",
    "COMPLETEDATE": "2022-06-02T08:43:00+01:00",
    "LOADED": null,
    "LOADDATE": null,
    "LINE": 353,
    "LOADTYPE": 10
}
08:43:33 DEBUG Solidworks.py > oDataConfig.py Opening [\\walrus\nas\PriorityMobile\python\apy\web.config].
08:43:33 DEBUG Solidworks.py > Serial.py POSTing to [priority.ntsa.uk/odata/priority/tabula.ini/wlnd/ZODA_TRANS] 
08:43:33 DEBUG Solidworks.py > Serial.py Headers:
{
    "Authorization": "Basic YXBpdXNlcjoxMjM0NTY=",
    "Content-Type": "application/json",
    "User-Agent": "MedatechUK Python Client"
}
08:43:33 DEBUG Solidworks.py > Serial.py Data:
{
    "BUBBLEID": "c686caa9-4eef-48eb-9424-7fc11970c874",
    "TYPENAME": "SW",
    "ZODA_LOAD_SUBFORM": [
        {
            "RECORDTYPE": "1",
            "TEXT2": "EK960",
            "TEXT3": "Hardener Momentive EK960",
            "TEXT1": "B01"
        }
    ]
}
08:43:34 DEBUG Solidworks.py > Serial.py [201] OK
08:43:34 DEBUG Solidworks.py > Serial.py PATCHing to [/odata/priority/tabula.ini/wlnd/ZODA_TRANS(BUBBLEID='c686caa9-4eef-48eb-9424-7fc11970c874',LOADTYPE=10)] ... 
08:43:34 DEBUG Solidworks.py > Serial.py [200] OK
08:43:34 DEBUG Solidworks.py > Serial.py Result: {
    "@odata.context": "https://priority.ntsa.uk/odata/Priority/tabula.ini/wlnd/$metadata#ZODA_TRANS/$entity",
    "TYPENAME": "SW",
    "BUBBLEID": "c686caa9-4eef-48eb-9424-7fc11970c874",
    "CREATEDATE": "2022-06-02T08:43:00+01:00",
    "COMPLETE": "Y",
    "COMPLETEDATE": "2022-06-02T08:43:00+01:00",
    "LOADED": null,
    "LOADDATE": null,
    "LINE": 354,
    "LOADTYPE": 10
}
08:43:34 DEBUG Solidworks.py > oDataConfig.py Opening [\\walrus\nas\PriorityMobile\python\apy\web.config].
08:43:34 DEBUG Solidworks.py > Serial.py POSTing to [priority.ntsa.uk/odata/priority/tabula.ini/wlnd/ZODA_TRANS] 
08:43:34 DEBUG Solidworks.py > Serial.py Headers:
{
    "Authorization": "Basic YXBpdXNlcjoxMjM0NTY=",
    "Content-Type": "application/json",
    "User-Agent": "MedatechUK Python Client"
}
08:43:34 DEBUG Solidworks.py > Serial.py Data:
{
    "BUBBLEID": "eb86bb06-0560-41f4-8cd7-7ba0fac0d715",
    "TYPENAME": "SW",
    "ZODA_LOAD_SUBFORM": [
        {
            "RECORDTYPE": "1",
            "TEXT2": "BOM Test",
            "TEXT3": "Test",
            "TEXT1": "A02"
        },
        {
            "RECORDTYPE": "2",
            "TEXT1": "C200",
            "REAL1": 0.6
        },
        {
            "RECORDTYPE": "2",
            "TEXT1": "EK960",
            "REAL1": 1.0
        }
    ]
}
08:43:34 DEBUG Solidworks.py > Serial.py [201] OK
08:43:34 DEBUG Solidworks.py > Serial.py PATCHing to [/odata/priority/tabula.ini/wlnd/ZODA_TRANS(BUBBLEID='eb86bb06-0560-41f4-8cd7-7ba0fac0d715',LOADTYPE=10)] ... 
08:43:34 DEBUG Solidworks.py > Serial.py [200] OK
08:43:34 DEBUG Solidworks.py > Serial.py Result: {
    "@odata.context": "https://priority.ntsa.uk/odata/Priority/tabula.ini/wlnd/$metadata#ZODA_TRANS/$entity",
    "TYPENAME": "SW",
    "BUBBLEID": "eb86bb06-0560-41f4-8cd7-7ba0fac0d715",
    "CREATEDATE": "2022-06-02T08:43:00+01:00",
    "COMPLETE": "Y",
    "COMPLETEDATE": "2022-06-02T08:43:00+01:00",
    "LOADED": null,
    "LOADDATE": null,
    "LINE": 355,
    "LOADTYPE": 10
}

```