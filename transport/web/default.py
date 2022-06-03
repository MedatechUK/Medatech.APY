######################################################
## si@medatechuk.com
## 12/09/21
##
## This is the IIS landing page
##
## All requests are redirected here by IIS URL rewriter
## with the environment and endpoint paramaterised into
## the request query string.
## 
## See web.congig:
##      <rewrite>
##         <rules>              
##         <rule name="API Rewrite env and endpoint">
##            <match url="^([0-9a-z_-]+)/(.*$)" />
##            <action type="Rewrite" url="default.py?environment={R:1}&amp;endpoint={R:2}" />
##         </rule>        
##         </rules>
##      </rewrite>

## Import the Request structure
import os
from MedatechUK.apy import Request
from MedatechUK.mLog import mLog

def main():
   #print('Content-Type: text/plain')
   #print('')
   
   try:
      log = mLog()
      log.start( os.path.dirname(__file__), "DEBUG" )

      ## Initialise the request      
      request = Request()

      # Test request
      if False:
         request = Request(endpoint="serialtest.py" , environment="wlnd" , method="POST", data={
            "custname": "CUST123",
            "ordname": "ORD1112233",
            "orderitems": [
               {
                     "partname": "ABC",
                     "qty": 1.1,
                     "duedate": 818181818
               },
               {
                     "partname": "DEF",
                     "qty": 2.2,
                     "duedate": 818181818
               },
               {
                     "partname": "GHI",
                     "qty": 3.3,
                     "duedate": 818181818
               }
            ]
         })
      
      ## Flush the response buffer
      request.response.Flush()

   except Exception as e :
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

if __name__ == '__main__':
    main()