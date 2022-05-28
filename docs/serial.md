# serial.py

This package extends the basic [property](https://docs.python.org/3/library/functions.html?highlight=property#property "python property") function in Python for:
- serialisation of objects
- adding data translations
- Loading into Priority

## Serialisation?

Serialisation is converting an object to a text representation of itself.

De-Serialisation is converting the text representation back into an object.

## Object?

An object is an heirarchy of properties, that defines the structure and content of the data being shared.

Imagine a simple order class. An order has 2 properties:
- the customer
- their PO number

We can write this so that custname and ordname are properties of our order:

```python

class order() :

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
```		

## Imports
```python
from MedatechUK.Serial import SerialBase , SerialT , SerialF

```

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