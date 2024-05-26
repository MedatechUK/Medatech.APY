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
import os , sys
from MedatechUK.apy import Request
from MedatechUK.mLog import mLog

def main():
   #print('Content-Type: text/plain')
   #print('')
   
   try:
      log = mLog()
      log.start( os.path.dirname(__file__), "DEBUG" )

      # Test request
      if False:
         request = Request(endpoint="gen3.py" , environment="wlnd" , method="POST", data={
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
         })
         
      else:
         ## Initialise the request      
         request = Request()

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