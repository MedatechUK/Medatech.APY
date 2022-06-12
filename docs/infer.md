# Infering a serial class
(added 0.0.20)

This is a Python replacement tool for XSD.exe, which creates .net serial classes from xml schemas.

The tool infers the required classes to serialise json data, based on a JSON file input.

## The file "sql.json":
```json
{
    "custname": "CUST123",
    "ordname": "ORD1112233",
    "orderitems": [
        {
            "partname": "ABC",
            "qty": "1.1",
            "duedate": "01/01/2022"
        }
    ]
}
```

## [MakeProps.py](../package/tests/MakeProps.py "MakeProps.py")
The following script uses the infer object from the serial class to create a list of serial objects, add some test code and any required imports. 

```Python
from MedatechUK.Serial import infer

...

with open(arg.args()[0], 'r') as the_file: 		
	inf = infer(json.loads(the_file.read()) , name=arg.byName(["name"]))
	
	# inf.imp.append("import something else for test code...")
	
	Output.append("\n".join(inf.imp)) 				# Imports
	Output.append("")					
	Output.append("\n".join(inf.cls))				# Classes
	Output.append("\n".join(inf.preq))				# Process request Method
	Output.append("if __name__ == '__main__':")		# Main part
	Output.append("    with open(\"{}\", \"r\") as the_file:".format(arg.args()[0]))
	Output.append("        q = {}(_json=the_file)".format(arg.byName(["name"])))
	Output.append("        print(json.dumps(json.loads(q.toFlatOdata()),indent=4, sort_keys=False))")

print("\n".join(Output))
	
```

## Generate the classes
We run "MakeProps.py" like so, with a named parameter "name" for the class name, and positional arguments for the input file and (optionally) an output file.
```
py makeprops.py -name order sql.json sql.py
```

This generates the following "sql.py" file. Read more about the [order / orderitems class](serial.md "order / orderitems class").
```python
import json
from MedatechUK.Serial import SerialBase , SerialT , SerialF
from MedatechUK.mLog import mLog

class order(SerialBase) :

    #region Properties
    
    @property
    def custname(self):
       return self._custname 
    @custname.setter
    def custname(self, value):
       self._custname = value
        
    @property
    def ordname(self):
       return self._ordname 
    @ordname.setter
    def ordname(self, value):
       self._ordname = value
        
    @property
    def orderitems(self):
        return self._orderitems
    @orderitems.setter
    def orderitems(self, value):
        self._orderitems = [] 
        if isinstance(value, list):
            for i in range(len(value)):
                self._orderitems.append(orderitems(**value[i]))
        else:
            self._orderitems.append(orderitems(**value))
    
    #endregion

    #region "ctor"
    def __init__(self,  **kwargs): 
    
        #region "Property defaults"
        self.custname = ""
        self.ordname = ""
        self.orderitems = []
    
        #endregion
    
        #region "Set Meta info"
        SerialBase.__init__(self , SerialF(fname="ZODA_TRANS", rt=1, typename="ORD"), **kwargs)  
        SerialT(self, "rt")
        SerialT(self, "bubbleid")
        SerialT(self, "typename")
        SerialT(self, "custname" , pCol="TEXT1" , Len=7 , pType="CHAR")
        SerialT(self, "ordname" , pCol="TEXT2" , Len=10 , pType="CHAR")
    
        #endregion
    
    #endregion

class orderitems(SerialBase) :

    #region Properties
    
    @property
    def partname(self):
       return self._partname 
    @partname.setter
    def partname(self, value):
       self._partname = value
        
    @property
    def qty(self):
       return self._qty 
    @qty.setter
    def qty(self, value):
       self._qty = value
        
    @property
    def duedate(self):
       return self._duedate 
    @duedate.setter
    def duedate(self, value):
       self._duedate = value
    
    #endregion

    #region "ctor"
    def __init__(self,  **kwargs): 
    
        #region "Property defaults"
        self.partname = ""
        self.qty = 0.0
        self.duedate = ""
    
        #endregion
    
        #region "Set Meta info"
        SerialBase.__init__(self , SerialF(fname="ZODA_LOAD", rt=2), **kwargs)  
        SerialT(self, "rt")
        SerialT(self, "partname" , pCol="TEXT1" , Len=3 , pType="CHAR")
        SerialT(self, "qty" , pCol="REAL1" , pType="REAL")
        SerialT(self, "duedate" , pCol="TEXT2" , Len=10 , pType="CHAR")
    
        #endregion
    
    #endregion

def ProcessRequest(request) :
    log = mLog()
    try:
        q = order(**request.data) 
        q.toPri(
            Config(
                env=request.environment , 
                path=os.getcwd()
            ) , 
            q.toFlatOdata, 
            request=request 
        )        
    
    except Exception as e:
        log.logger.critical(str(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        request.response.Status = 500
        request.response.Message = "Internal Server Error"
        request.response.data ={ "error" :
            {
                "type": exc_type,
                "message": str(e),
                "script": fname,
                "line": exc_tb.tb_lineno
            }
        } 

if __name__ == '__main__':
    with open("sql.json", "r") as the_file:
        q = order(_json=the_file)
        print(json.dumps(json.loads(q.toFlatOdata()),indent=4, sort_keys=False))
		
```

## Testing the serialiser
When we run the "sql.py" file, the debug code deserialises our origional "sql.json" file and displays the data (without sending) as oData commands:
```json
{
    "BUBBLEID": "94dddff4-defe-4c76-99f1-ff859bcceb72",
    "TYPENAME": "ORD",
    "ZODA_LOAD_SUBFORM": [
        {
            "RECORDTYPE": "1",
            "TEXT1": "CUST123",
            "TEXT2": "ORD1112233"
        },
        {
            "RECORDTYPE": "2",
            "TEXT1": "ABC",
            "REAL1": 1.1,
            "TEXT2": "01/01/2022"
        }
    ]
}

```