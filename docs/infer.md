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

## [makeprops.py](../package/tests/makeprops.py "makeprops.py")
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

## More Examples

### M:\python\apy>type gen1.json
```json
{
  "__VERSION__": "1-0-0",
  "order_reference": "PO22000584",
  "supplier": {
     "relation_type": "supplier",
     "reference": "CON50",
     "company_name": "CONTRACT EMBROIDERY LTD",
     "country_reference": "GB"
  },
  "order_lines": [
     {
        "line_reference": "1504875",
        "product_reference": "ASLTI-NVY-7/8",
        "packaging_reference": [],
        "quantity": "12"
     },
     {
        "line_reference": "1504876",
        "product_reference": "ASLTI-NVY-9/10",
        "packaging_reference": [],
        "quantity": "25"
     },
     {
        "line_reference": "1504877",
        "product_reference": "ASLTI-NVY-L",
        "packaging_reference": [],
        "quantity": "6"
     },
     {
        "line_reference": "1504878",
        "product_reference": "ASLTI-NVY-M",
        "packaging_reference": [],
        "quantity": "10"
     },
     {
        "line_reference": "1504879",
        "product_reference": "ASLTI-NVY-S",
        "packaging_reference": [],
        "quantity": "15"
     },
     {
        "line_reference": "1504880",
        "product_reference": "ASLTI-NVY-XL",
        "packaging_reference": [],
        "quantity": "3"
     },
     {
        "line_reference": "1504881",
        "product_reference": "ASLTI-NVY-XS",
        "packaging_reference": [],
        "quantity": "8"
     },
     {
        "line_reference": "1504882",
        "product_reference": "ASLTI-NVY-XXS",
        "packaging_reference": [],
        "quantity": "10"
     },
     {
        "line_reference": "1504883",
        "product_reference": "ASLTI-NVY-2XL",
        "packaging_reference": [],
        "quantity": "3"
     }
  ]
}
```
```
M:\python\apy>py makeprops.py gen1.json gen1.py -name order

M:\python\apy>py gen1.py
```
```json
{
    "BUBBLEID": "1672e37d-88fd-47b3-b884-d05282c7bd0b",
    "TYPENAME": "ORD",
    "ZODA_LOAD_SUBFORM": [
        {
            "RECORDTYPE": "1",
            "TEXT2": "PO22000584"
        },
        {
            "RECORDTYPE": "2",
            "TEXT1": "supplier",
            "TEXT2": "CON50",
            "TEXT3": "CONTRACT EMBROIDERY LTD",
            "TEXT4": "GB"
        },
        {
            "RECORDTYPE": "3",
            "TEXT1": "1504875",
            "TEXT2": "ASLTI-NVY-7/8",
            "INT1": 12
        },
        {
            "RECORDTYPE": "3",
            "TEXT1": "1504876",
            "TEXT2": "ASLTI-NVY-9/10",
            "INT1": 25
        },
        {
            "RECORDTYPE": "3",
            "TEXT1": "1504877",
            "TEXT2": "ASLTI-NVY-L",
            "INT1": 6
        },
        {
            "RECORDTYPE": "3",
            "TEXT1": "1504878",
            "TEXT2": "ASLTI-NVY-M",
            "INT1": 10
        },
        {
            "RECORDTYPE": "3",
            "TEXT1": "1504879",
            "TEXT2": "ASLTI-NVY-S",
            "INT1": 15
        },
        {
            "RECORDTYPE": "3",
            "TEXT1": "1504880",
            "TEXT2": "ASLTI-NVY-XL",
            "INT1": 3
        },
        {
            "RECORDTYPE": "3",
            "TEXT1": "1504881",
            "TEXT2": "ASLTI-NVY-XS",
            "INT1": 8
        },
        {
            "RECORDTYPE": "3",
            "TEXT1": "1504882",
            "TEXT2": "ASLTI-NVY-XXS",
            "INT1": 10
        },
        {
            "RECORDTYPE": "3",
            "TEXT1": "1504883",
            "TEXT2": "ASLTI-NVY-2XL",
            "INT1": 3
        }
    ]
}
```

### M:\python\apy>type gen2.json
```json
{
    "order_id":"170273",
    "reference_number":"449149",
    "created_at":"2020-05-13T07:04:14Z",
    "state":"pending",
    "status":"Pending",
    "ashridge_ship_method":"Courier",
    "delivery_at":"2020-05-18",
    "currency":"GBP",
    "customer":{
        "id":"125560",
        "prefix":"Mr",
        "firstName":"TEST",
        "lastName":"ACCOUNT",
        "email":"jais.anand007@rediffmail.com",
        "group_id":"1"
    },
    "billingaddress":{
        "prefix":"Mr",
        "firstName":"TEST",
        "lastName":"ACCOUNT",
        "company":"WHIZ SOLUTIONS",
        "street1":"REDHILL FARM",
        "street2":"BLACKSMITHS LANE",
        "city":"GLASGOW",
        "state":"SOMERSET",
        "postCode":"G13 2XZ",
        "country":"GB",
        "telephone":"09988776655"
    },
    "shippingaddress":{
        "prefix":"Mr",
        "firstName":"TEST",
        "lastName":"JAISWAL",
        "company":"ACCOUNT",
        "street1":"REDHILL FARM",
        "street2":"BLACKSMITHS LANE",
        "city":"GLASGOW",
        "state":"SOMERSET",
        "postCode":"G13 2XZ",
        "country":"GB",
        "telephone":"09988776655"
    },
    "payment_method":{
        "title":"paysafe",
        "authorize":"yes",
        "card_token":"Cam9F1kcOVYTucV"
    },
    "shipping_method":{
        "title":"Delivery",
        "amount":"6.50",
        "currency":"GBP"
    },
    "instruction_for_courier":"Drop at main gate.",
    "message_for_ashridge":"Deliver after 01 July.",
    "order_special_note":"Send with bulb order",
    "warehouse_special_note":"Pack carefully.",
    "orderitems":[
        {
            "name":"Hidcote Lavender - Lavandula angustifolia Hidcote",
            "sku":"LAVAANGHI-P9",
            "size":"P9",
            "price":"3.95",
            "qty":"9",
            "subtotal":"35.55",
            "tax_percent":"0.00",
            "tax":"0.00",
            "discount_percent":"10.00",
            "discount":"3.56",
            "row_total":"31.99"
        },
        {
            "name":"Hawthorn, Quickthorn",
            "sku":"CRATMON-40/60 cm",
            "size":"40/60 cm",
            "price":"1.60",
            "qty":"2",
            "subtotal":"3.20",
            "tax_percent":"20.00",
            "tax":"0.58",
            "discount_percent":"10.00",
            "discount":"0.32",
            "row_total":"3.46"
        }
    ],
    "subtotal":"38.75",
    "shipping_amount":"6.50",
    "discount_amount":"3.88",
    "discount_code":"HAS110",
    "tax_amount":"1.88",
    "grandtotal":"43.25",
    "total_paid":"0.00",
    "total_refunded":"0.00",
    "total_due":"43.25"
}
```
```
M:\python\apy>py makeprops.py gen2.json gen2.py -name order

M:\python\apy>py gen2.py
```
```json
{
    "BUBBLEID": "24dde073-6b81-4121-b712-ffd26fa11500",
    "TYPENAME": "ORD",
    "ZODA_LOAD_SUBFORM": [
        {
            "RECORDTYPE": "1",
            "TEXT1": "170273",
            "TEXT2": "449149",
            "TEXT3": "2020-05-13T07:04:14Z",
            "TEXT4": "pending",
            "TEXT5": "Pending",
            "TEXT6": "Courier",
            "TEXT7": "2020-05-18",
            "TEXT8": "GBP",
            "TEXT9": "Drop at main gate.",
            "TEXT10": "Deliver after 01 July.",
            "TEXT11": "Send with bulb order",
            "TEXT12": "Pack carefully.",
            "REAL1": 38.75,
            "REAL2": 6.5,
            "REAL3": 3.88,
            "TEXT13": "HAS110",
            "REAL4": 1.88,
            "REAL5": 43.25,
            "REAL6": 0.0,
            "REAL7": 0.0,
            "REAL8": 43.25
        },
        {
            "RECORDTYPE": "2",
            "TEXT1": "125560",
            "TEXT2": "Mr",
            "TEXT3": "TEST",
            "TEXT4": "ACCOUNT",
            "TEXT5": "jais.anand007@rediffmail.com",
            "INT1": 1
        },
        {
            "RECORDTYPE": "3",
            "TEXT1": "Mr",
            "TEXT2": "TEST",
            "TEXT3": "ACCOUNT",
            "TEXT4": "WHIZ SOLUTIONS",
            "TEXT5": "REDHILL FARM",
            "TEXT6": "BLACKSMITHS LANE",
            "TEXT7": "GLASGOW",
            "TEXT8": "SOMERSET",
            "TEXT9": "G13 2XZ",
            "TEXT10": "GB",
            "TEXT11": "09988776655"
        },
        {
            "RECORDTYPE": "4",
            "TEXT1": "Mr",
            "TEXT2": "TEST",
            "TEXT3": "JAISWAL",
            "TEXT4": "ACCOUNT",
            "TEXT5": "REDHILL FARM",
            "TEXT6": "BLACKSMITHS LANE",
            "TEXT7": "GLASGOW",
            "TEXT8": "SOMERSET",
            "TEXT9": "G13 2XZ",
            "TEXT10": "GB",
            "TEXT11": "09988776655"
        },
        {
            "RECORDTYPE": "5",
            "TEXT1": "paysafe",
            "TEXT2": "yes",
            "TEXT3": "Cam9F1kcOVYTucV"
        },
        {
            "RECORDTYPE": "6",
            "TEXT1": "Delivery",
            "REAL1": 6.5,
            "TEXT2": "GBP"
        },
        {
            "RECORDTYPE": "7",
            "TEXT1": "Hidcote Lavender - Lavandula angustifolia Hidcote",
            "TEXT2": "LAVAANGHI-P9",
            "TEXT3": "P9",
            "REAL1": 3.95,
            "INT1": 9,
            "REAL2": 35.55,
            "REAL3": 0.0,
            "REAL4": 0.0,
            "REAL5": 10.0,
            "REAL6": 3.56,
            "REAL7": 31.99
        },
        {
            "RECORDTYPE": "7",
            "TEXT1": "Hawthorn, Quickthorn",
            "TEXT2": "CRATMON-40/60 cm",
            "TEXT3": "40/60 cm",
            "REAL1": 1.6,
            "INT1": 2,
            "REAL2": 3.2,
            "REAL3": 20.0,
            "REAL4": 0.58,
            "REAL5": 10.0,
            "REAL6": 0.32,
            "REAL7": 3.46
        }
    ]
}

```

### M:\python\apy>type gen3.json
```json
{
    "acc": [
        {
            "id": "551d2281-5f34-4c3e-b7e9-9330c83556d8",
            "dateAdded": "2021-09-24T19:15:34+00:00",
            "dateModified": "2021-09-29T02:14:45+00:00",
            "accountName": "Business Account",
            "type": "cash:current",
            "accountType": "business",
            "accountReference": "3801",
            "providerName": "Lloyds",
            "providerId": "DEMO",
            "providerReference": "demo",
            "connectionId": "DEMO:666",
            "balance": {
                "amount": {
                    "value": 10456552,
                    "currency": "GBP"
                },
                "date": "2021-09-29"
            },
            "currency": "GBP",
            "details": {
                "AER": 0,
                "overdraftLimit": 0
            },
            "transactionData": {
                "count": 315,
                "earliestDate": "2020-09-27",
                "lastDate": "2021-09-27T00:00:00.000Z"
            },
            "trans": [
                {
                    "amount": {
                        "value": 2387827,
                        "currency": "GBP"
                    },
                    "accountId": "551d2281-5f34-4c3e-b7e9-9330c83556d8",
                    "categoryId": "std:47d1b4b6-174e-4410-95f5-667dfe44be98",
                    "categoryIdConfirmed": "False",
                    "date": "2021-09-27T02:26:47",
                    "dateModified": "2021-09-27T02:26:48.242Z",
                    "id": "34a06b5b-cb95-4f9e-b2dd-b61b687e131f",
                    "longDescription": "BAILEY BUILDING AND LOAN ASSOCIATION Bill Payment INVx5998 BBP",
                    "notes": "",
                    "shortDescription": "Bailey Building and Loan Association",
                    "status": "posted",
                    "counterpartyId": "ae19861000e6d7a292d6f0e47f46d68ea05034ab399b2798974d50e5d48fe905",
                    "providerId": "a5499e09-854b-4883-a405-8a07136de591"
                },
                {
                    "amount": {
                        "value": 565702,
                        "currency": "GBP"
                    },
                    "accountId": "551d2281-5f34-4c3e-b7e9-9330c83556d8",
                    "categoryId": "std:47d1b4b6-174e-4410-95f5-667dfe44be98",
                    "categoryIdConfirmed": "False",
                    "date": "2021-09-27T02:26:47",
                    "dateModified": "2021-09-27T02:26:48.276Z",
                    "id": "f4ef0b79-7080-4e55-8e23-82df07e11684",
                    "longDescription": "STARK INDUSTRIES Counter Credit x8292 BGC",
                    "notes": "",
                    "shortDescription": "Stark Industries",
                    "status": "posted",
                    "counterpartyId": "9b18a211193b1889ab9b5af51bc61bc3b507037dc46dfd1c88333de3424021fd",
                    "providerId": "89860d4d-c622-4dab-b6df-b3c18cd459fe"
                }
            ]
        }
    ]
}
```
```
M:\python\apy>py makeprops.py gen3.json gen3.py -name order

M:\python\apy>py gen3.py
```
```json
{
    "BUBBLEID": "9918ac0f-2b77-4b8d-988e-03d76d12a4e0",
    "TYPENAME": "ORD",
    "ZODA_LOAD_SUBFORM": [
        {
            "RECORDTYPE": "1"
        },
        {
            "RECORDTYPE": "2",
            "TEXT1": "551d2281-5f34-4c3e-b7e9-9330c83556d8",
            "TEXT2": "2021-09-24T19:15:34+00:00",
            "TEXT3": "2021-09-29T02:14:45+00:00",
            "TEXT4": "Business Account",
            "TEXT5": "cash:current",
            "TEXT6": "business",
            "INT1": 3801,
            "TEXT7": "Lloyds",
            "TEXT8": "DEMO",
            "TEXT9": "demo",
            "TEXT10": "DEMO:666",
            "TEXT11": "GBP"
        },
        {
            "RECORDTYPE": "3",
            "TEXT1": "2021-09-29"
        },
        {
            "RECORDTYPE": "4",
            "TEXT1": "10456552",
            "TEXT2": "GBP"
        },
        {
            "RECORDTYPE": "5",
            "INT1": 0,
            "INT2": 0
        },
        {
            "RECORDTYPE": "6",
            "INT1": 315,
            "TEXT1": "2020-09-27",
            "TEXT2": "2021-09-27T00:00:00.000Z"
        },
        {
            "RECORDTYPE": "7",
            "TEXT1": "551d2281-5f34-4c3e-b7e9-9330c83556d8",
            "TEXT2": "std:47d1b4b6-174e-4410-95f5-667dfe44be98",
            "TEXT3": "False",
            "TEXT4": "2021-09-27T02:26:47",
            "TEXT5": "2021-09-27T02:26:48.242Z",
            "TEXT6": "34a06b5b-cb95-4f9e-b2dd-b61b687e131f",
            "TEXT7": "BAILEY BUILDING AND LOAN ASSOCIATION Bill Payment INVx5998BBP",
            "TEXT8": "",
            "TEXT9": "Bailey Building and Loan Association",
            "TEXT10": "posted",
            "TEXT11": "ae19861000e6d7a292d6f0e47f46d68ea05034ab399b2798974d50e5d48fe905",
            "TEXT12": "a5499e09-854b-4883-a405-8a07136de591"
        },
        {
            "RECORDTYPE": "4",
            "TEXT1": "2387827",
            "TEXT2": "GBP"
        },
        {
            "RECORDTYPE": "7",
            "TEXT1": "551d2281-5f34-4c3e-b7e9-9330c83556d8",
            "TEXT2": "std:47d1b4b6-174e-4410-95f5-667dfe44be98",
            "TEXT3": "False",
            "TEXT4": "2021-09-27T02:26:47",
            "TEXT5": "2021-09-27T02:26:48.276Z",
            "TEXT6": "f4ef0b79-7080-4e55-8e23-82df07e11684",
            "TEXT7": "STARK INDUSTRIES Counter Credit x8292 BGC",
            "TEXT8": "",
            "TEXT9": "Stark Industries",
            "TEXT10": "posted",
            "TEXT11": "9b18a211193b1889ab9b5af51bc61bc3b507037dc46dfd1c88333de3424021fd",
            "TEXT12": "89860d4d-c622-4dab-b6df-b3c18cd459fe"
        },
        {
            "RECORDTYPE": "4",
            "TEXT1": "565702",
            "TEXT2": "GBP"
        }
    ]
}

```