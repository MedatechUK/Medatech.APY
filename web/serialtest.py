import json , uuid , os , sys
import xmltodict , dicttoxml
from MedatechUK.Serial import SerialBase , SerialT , SerialF
from MedatechUK.mLog import mLog
from MedatechUK.apy import Response
from MedatechUK.oDataConfig import Config

#region "Custom Serialisation objects"

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
        SerialT(self, "duedate" , pCol="INT2" , pType="INT")

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
        request.Status = 500
        request.response.Message = "Internal Server Error"
        request.response.data ={ "error" :
            {
                "type": exc_type,
                "message": str(e),
                "script": fname,
                "line": exc_tb.tb_lineno
            }
        } 

#endregion

#region Examples

if __name__ == '__main__':    

    #region "Create a log file"
    log = mLog()
    log.start( os.getcwd(), "DEBUG" )
    log.logger.debug("Starting {}".format(__file__))                 

    #endregion

    #region "Create an order"
    x = order( custname = 'CUST123' , ordname = 'ORD1112233' )
    x.orderitems.append(orderitems(partname="ABC" , qty=1.1 , duedate=818181818))
    x.orderitems.append(orderitems(partname="DEF" , qty=2.2 , duedate=818181818))
    x.orderitems.append(orderitems(partname="GHI" , qty=3.3 , duedate=818181818))

    # Save the order to file    
    x.toFile('test.json', x.toJSON)

    #endregion

    #region "Load Order from xml file"    
    #with open('test.xml', 'r') as the_file:
    #    t= xmltodict.parse(the_file.read())
    #    q = order(**json.loads(json.dumps(t[list(t)[0]])))
    
    #endregion
    
    #region "Load Order from json file"    
    with open('test.json', 'r') as the_file:
        q = order(**json.loads(the_file.read()))

    #endregion

    #region "Method usage"
    # Output as json
    #print(q.toJSON())

    # Output as nested oData Commands
    #print(json.dumps(json.loads(q.toOdata()), sort_keys=False, indent=4))

    # Output as flat oData Commands (for Priority loading)
    #print(json.dumps(json.loads(q.toFlatOdata()), sort_keys=False, indent=4))

    # Create an object to hold the result
    Response = Response()
    
    # Send toFlatOdata method to Priority API
    q.toPri(
        Config(
            env="wlnd" , 
            path=os.getcwd()
        ) , 
        q.toFlatOdata , 
        response=Response
    )
    
    # Display the result
    print( "[{}]: {}".format( Response.Status , Response.Message ) )
    print( "response : " + json.dumps(Response.data, sort_keys=False, indent=4 ))

    #endregion    

#endregion