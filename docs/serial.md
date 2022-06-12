# serial.py

This package extends the basic [property](https://docs.python.org/3/library/functions.html?highlight=property#property "python property") function in Python for:
- serialisation of objects
- adding data translations
- Loading into Priority

See also: [Serial Methods](serialmethod.md "Serial Methods").

See also: [Infering this class](infer.md "infer tool").

## Imports
```python
from MedatechUK.Serial import SerialBase , SerialT , SerialF

```

### Serialisation?

Serialisation is converting an object to a text representation of itself.

De-Serialisation is converting the text representation back into an object.

### Object?

An object is an heirarchy of properties, that defines both the structure and content of the data it will store.

Imagine a simple order class with 2 properties:
- the customer
- their PO number

We can write this so that custname and ordname are properties of our order:

```python

class order() :
    
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
```		

## Inheriting the serial base

This package provides a inheritable class for working with serialisable objects called *SerialBase*, which we inherit like this:

```python

class order(SerialBase) :

```

This seperates our code from our data, and means we can run any function from *SerialBase* on the data stored in our object.

See [Serial Methods](serialmethod.md "Serial Methods").

## Sub Objects

Now our order class needs to have some ordered items, so we'll create and order item class that will contain the following properties:
- part name
- quantity
- due date

We can define our order item class like so:

```python
class orderitems(SerialBase) :
    
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
```

Now we add a new property to the *order* class, defining a list of *orderitems*:

```python
class order(SerialBase) :

...

    @property
    def orderitems(self):    
        return self._orderitems
    @orderitems.setter
    def orderitems(self, value):        
        self._orderitems = value
        for i in range(len(self._orderitems)):
            self._orderitems[i] = orderitems(**self._orderitems[i])
```

## Default property values 

We must set the default values for our properties in our classes constructor method "__init__".

```python
    def __init__(self,  **kwargs): 
	        
        self.custname = 0
        self.ordname = ""
        self.orderitems = [] 
```

## Meta data

We call the base constructor with a SerialF class (Serial Form), which contains information including:
- the Priorty odata form name (mandatory)
- the record type (for loading into oData form)
- the typename (also for loading into oData form)

```python
	def __init__(self,  **kwargs): 
	
	...
	
	SerialBase.__init__(self , SerialF(fname="ZODA_TRANS", rt=1, typename="ORD"), **kwargs)
	
```

For each property we want to send to Priority oData, we also need to define a column with the SerialT class (Serial Type), which contains extra information about the property.
```python
	def __init__(self,  **kwargs): 
	
	...
	
	SerialT(self, "PROPERTY_NAME" , pCol="PRIORITY_COLUMN" , Len=LENGTH , pType="PRIORITY_TYPE")
	
```
| Property      |Description                            |
|---------------|---------------------------------------|
| PROPERTY_NAME        |The (case sensitive) name of the property in the class (Mandatory)  |
| PRIORITY_COLUMN        |  The column name in Priority (Mandatory)|
| PRIORITY_TYPE        |The Priority data type of the data e.g. TEXT, INT, REAL|
| LENGTH        |The maximun length (optonal)|

Additionally there are some predefined fields you can include in your load data:

| Field	|Description                            |
|---------------|---------------------------------------|
|SerialT(self, "bubbleid")|A unique identifier for the transaction|
|SerialT(self, "rt")| The record Type defined for the form (see FormF)|
|SerialT(self, "typename")|The load Type defined for the form (see FormF)|


## Property translation

Imagine we receive the following order:
```json
{
    "custname": "CUST123",
    "ordname": "ORD1112233",
    "orderitems": [
        {
            "partname": "ABC",
            "qty": 1.1,
            "duedate": "01/01/2022"
        },
        {
            "partname": "DEF",
            "qty": 2.2,
            "duedate": "02/01/2022"
        },
        {
            "partname": "GHI",
            "qty": 3.3,
            "duedate": "03/01/2022"
        }
    ]
}
```
The due date we receive is a string, wheras Priority dates are minutes past 01/01/1988.

In order to convert this we can add a calculated read only property like so:
```python
@property
def pridate(self):
    try :
        d = parse(self._duedate)    
        return int(
            (datetime(
                d.year, 
                d.month, 
                d.day, 
                d.hour, 
                d.minute) 
            - datetime(1988, 1, 1)).total_seconds() / 60
        )     
    except:
        return 0 

```
And add that as the SerialT, instead of Due Date:
```python
# pridate is a readonly function that converts the dudate to a Priority integer
SerialT(self, "pridate" , pCol="INT2" , pType="INT")
```

This converts the data sent to priority from text to a valid date:
```json
{
    "BUBBLEID": "979b9402-8f99-456d-9a7c-2fed769981d6",
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
            "INT2": 17883360
        },
        {
            "RECORDTYPE": "2",
            "TEXT1": "DEF",
            "REAL1": 2.2,
            "INT2": 17928000
        },
        {
            "RECORDTYPE": "2",
            "TEXT1": "GHI",
            "REAL1": 3.3,
            "INT2": 17968320
        }
    ]
}
```

## Order Class Full code listing

This code was created by the [Infer tool](infer.md "infer tool").
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