# serial.py

This package extends the basic [property](https://docs.python.org/3/library/functions.html?highlight=property#property "python property") function in Python for:
- serialisation of objects
- adding data translations
- Loading into Priority

## Imports
```python
from MedatechUK.Serial import SerialBase , SerialT , SerialF

```

## Serialisation?

Serialisation is converting an object to a text representation of itself.

De-Serialisation is converting the text representation back into an object.

## Object?

An object is an heirarchy of properties, that defines the structure and content of the data being shared.

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

## Sub Objects

Our order class needs to have some items. 

Our order item will contain the following properties:
- part name
- quantity
- due date

We can define our item like so:

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

We can set he default values for our properties in our classes constructor method "__init__".

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

For each property we want to send to Priority oData, we also need to add a SerialT class (Serial Type), which contains the properties:
- Priority column name
- Length
- Type

```python
	def __init__(self,  **kwargs): 
	
	...
	
	SerialT(self, "PROPERTY_NAME" , pCol="PRIORITY_COLUMN" , Len=LENGTH , pType="PRIORITY_TYPE")
	
```
| Property      |Description                            |
|---------------|---------------------------------------|
| PROPERTY_NAME        |The (case sensitive) name of the property in the class   |
| PRIORITY_COLUMN        |  The column name in Priority |
| LENGTH        |The maximun length (optonal)|
| PRIORITY_TYPE        |The Priority data type of the data e.g. TEXT, INT, REAL|

## Custom Business Objects

```python
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
        self._orderitems = value
        for i in range(len(self._orderitems)):
            self._orderitems[i] = orderitems(**self._orderitems[i])

    #endregion

    #region "ctor"
    def __init__(self,  **kwargs): 

        #region "Property defaults"
        self.custname = 0
        self.ordname = ""
        self.orderitems = []  

        #endregion  

        #region "Set Meta info"
        SerialBase.__init__(self , SerialF(fname="ZODA_TRANS", rt=1, typename="ORD"), **kwargs)  
        SerialT(self, "rt")
        SerialT(self, "bubbleid")
        SerialT(self, "typename")
        SerialT(self, "custname" , pCol="TEXT1" , Len=20 , pType="CHAR")
        SerialT(self, "ordname" , pCol="TEXT2" , Len=20 , pType="CHAR")

        #endregion
    
    #endregion

class orderitems(SerialBase) :

    #region properties
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

    # Readonly calculated property
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

    #endregion

    #region "ctor"
    def __init__(self,  **kwargs): 

        #region "Property defaults"
        self.partname = ''
        self.qty=0
        self.duedate = ''     
        
        #endregion

        #region "Set Meta info"
        SerialBase.__init__(self , SerialF(fname="ORDERITEMS", rt=2) , **kwargs)   
        SerialT(self, "rt")
        SerialT(self, "partname" , pCol="TEXT1" , Len=10 , pType="CHAR")
        SerialT(self, "qty" , pCol="REAL1" , pType="REAL")
        
        # pridate is a readonly function that converts the dudate to a Priority integer
        SerialT(self, "pridate" , pCol="INT2" , pType="INT")

        #endregion
    
    #endregion

```