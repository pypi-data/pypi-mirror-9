#include "caerr.h"
#include <stdio.h>
/* copied from access.cpp */
const char * ca_message_text []
=
{
"Normal successful completion",
"Maximum simultaneous IOC connections exceeded",
"Unknown internet host",
"Unknown internet service",
"Unable to allocate a new socket",

"Unable to connect to internet host or service",
"Unable to allocate additional dynamic memory",
"Unknown IO channel",
"Record field specified inappropriate for channel specified",
"The requested data transfer is greater than available memory or EPICS_CA_MAX_ARRAY_BYTES",

"User specified timeout on IO operation expired",
"Sorry, that feature is planned but not supported at this time",
"The supplied string is unusually large",
"The request was ignored because the specified channel is disconnected",
"The data type specifed is invalid",

"Remote Channel not found",
"Unable to locate all user specified channels",
"Channel Access Internal Failure",
"The requested local DB operation failed",
"Channel read request failed",

"Channel write request failed",
"Channel subscription request failed",
"Invalid element count requested",
"Invalid string",
"Virtual circuit disconnect",

"Identical process variable names on multiple servers",
"Request inappropriate within subscription (monitor) update callback",
"Database value get for that channel failed during channel search",
"Unable to initialize without the vxWorks VX_FP_TASK task option set",
"Event queue overflow has prevented first pass event after event add",

"Bad event subscription (monitor) identifier",
"Remote channel has new network address",
"New or resumed network connection",
"Specified task isnt a member of a CA context",
"Attempt to use defunct CA feature failed",

"The supplied string is empty",
"Unable to spawn the CA repeater thread- auto reconnect will fail",
"No channel id match for search reply- search reply ignored",
"Reseting dead connection- will try to reconnect",
"Server (IOC) has fallen behind or is not responding- still waiting",

"No internet interface with broadcast available",
"Invalid event selection mask",
"IO operations have completed",
"IO operations are in progress",
"Invalid synchronous group identifier",

"Put callback timed out",
"Read access denied",
"Write access denied",
"Requested feature is no longer supported",
"Empty PV search address list",

"No reasonable data conversion between client and server types",
"Invalid channel identifier",
"Invalid function pointer",
"Thread is already attached to a client context",
"Not supported by attached service",

"User destroyed channel",
"Invalid channel priority",
"Preemptive callback not enabled - additional threads may not join context",
"Client's protocol revision does not support transfers exceeding 16k bytes",
"Virtual circuit connection sequence aborted",

"Virtual circuit unresponsive"
};

#define gen(name,val) printf("class %s(caError):\n    __doc__=_caErrorMsg[%d]\n    __errcode__=%d\n\nErrCode2Class[%3$d]=%1$s\n\n",name,CA_EXTRACT_MSG_NO(val),val);
main(void){
  long i=0;
  printf("from ca import _ca\n");
  printf("class caError(_ca.error):\n");
  printf("  \"\"\" EPICS ca.py Errors\"\"\"\n  pass\n\n");
  printf("__caErrorMsg=(\n");
  for(i=0;i<sizeof(ca_message_text)/sizeof(char *); i++){
    printf("\"%s\",\n",ca_message_text[i]);
  }
  printf(")\n");
  printf("_caErrorMsg=map(intern,__caErrorMsg)\n\n");

  printf("ErrCode2Class={}\n");
  printf("class PyCa_NoCallback(caError):\n    __doc__=\"Null callback routine\"\n");
  printf("CA_M_MSG_NO    = 0x0000FFF8\n");
  printf("CA_M_SEVERITY  = 0x00000007\n");
  printf("CA_M_LEVEL     = 0x00000003\n");
  printf("CA_M_SUCCESS   = 0x00000001\n");
  printf("CA_M_ERROR     = 0x00000002\n");
  printf("CA_M_SEVERE    = 0x00000004\n");

  printf("CA_S_MSG_NO= 0x0D\n");
  printf("CA_S_SEVERITY=0x03\n");
  printf("CA_V_MSG_NO=     0x03\n");
  printf("CA_V_SEVERITY=   0x00\n");
  printf("CA_V_SUCCESS=    0x00\n\n");
  printf("def CA_EXTRACT_MSG_NO(code): return ( ( (code) & CA_M_MSG_NO )  >> CA_V_MSG_NO )\n");
  printf("def CA_EXTRACT_SEVERITY(code): return ( ( (code) & CA_M_SEVERITY )    >> CA_V_SEVERITY) \n" );
  printf("def CA_EXTRACT_SUCCESS(code): ( ( (code) & CA_M_SUCCESS )     >> CA_V_SUCCESS )\n\n");

gen("ECA_NORMAL",ECA_NORMAL);   
gen("ECA_MAXIOC",ECA_MAXIOC);   
gen("ECA_UKNHOST",ECA_UKNHOST);  
gen("ECA_UKNSERV",ECA_UKNSERV);  
gen("ECA_SOCK",ECA_SOCK);     
gen("ECA_CONN",ECA_CONN);     
gen("ECA_ALLOCMEM",ECA_ALLOCMEM);        
gen("ECA_UKNCHAN",ECA_UKNCHAN);         
gen("ECA_UKNFIELD",ECA_UKNFIELD);        
gen("ECA_TOLARGE",ECA_TOLARGE);         
gen("ECA_TIMEOUT",ECA_TIMEOUT);         
gen("ECA_NOSUPPORT",ECA_NOSUPPORT);       
gen("ECA_STRTOBIG",ECA_STRTOBIG);        
gen("ECA_DISCONNCHID",ECA_DISCONNCHID);     
gen("ECA_BADTYPE",ECA_BADTYPE);         
gen("ECA_CHIDNOTFND",ECA_CHIDNOTFND);      
gen("ECA_CHIDRETRY",ECA_CHIDRETRY);       
gen("ECA_INTERNAL",ECA_INTERNAL);        
gen("ECA_DBLCLFAIL",ECA_DBLCLFAIL);       
gen("ECA_GETFAIL",ECA_GETFAIL);         
gen("ECA_PUTFAIL",ECA_PUTFAIL);         
gen("ECA_ADDFAIL",ECA_ADDFAIL);         
gen("ECA_BADCOUNT",ECA_BADCOUNT);        
gen("ECA_BADSTR",ECA_BADSTR);          
gen("ECA_DISCONN",ECA_DISCONN);         
gen("ECA_DBLCHNL",ECA_DBLCHNL);         
gen("ECA_EVDISALLOW",ECA_EVDISALLOW);      
gen("ECA_BUILDGET",ECA_BUILDGET);        
gen("ECA_NEEDSFP",ECA_NEEDSFP);         
gen("ECA_OVEVFAIL",ECA_OVEVFAIL);        
gen("ECA_BADMONID",ECA_BADMONID);        
gen("ECA_NEWADDR",ECA_NEWADDR);         
gen("ECA_NEWCONN",ECA_NEWCONN);         
gen("ECA_NOCACTX",ECA_NOCACTX);         
gen("ECA_DEFUNCT",ECA_DEFUNCT);         
gen("ECA_EMPTYSTR",ECA_EMPTYSTR);        
gen("ECA_NOREPEATER",ECA_NOREPEATER);      
gen("ECA_NOCHANMSG",ECA_NOCHANMSG);       
gen("ECA_DLCKREST",ECA_DLCKREST);        
gen("ECA_SERVBEHIND",ECA_SERVBEHIND);      
gen("ECA_NOCAST",ECA_NOCAST);          
gen("ECA_BADMASK",ECA_BADMASK);         
gen("ECA_IODONE",ECA_IODONE);          
gen("ECA_IOINPROGRESS",ECA_IOINPROGRESS);    
gen("ECA_BADSYNCGRP",ECA_BADSYNCGRP);      
gen("ECA_PUTCBINPROG",ECA_PUTCBINPROG);     
gen("ECA_NORDACCESS",ECA_NORDACCESS);      
gen("ECA_NOWTACCESS",ECA_NOWTACCESS);      
gen("ECA_ANACHRONISM",ECA_ANACHRONISM);     
gen("ECA_NOSEARCHADDR",ECA_NOSEARCHADDR);    
gen("ECA_NOCONVERT",ECA_NOCONVERT);       
gen("ECA_BADCHID",ECA_BADCHID);         
gen("ECA_BADFUNCPTR",ECA_BADFUNCPTR);      
gen("ECA_ISATTACHED",ECA_ISATTACHED);      
gen("ECA_UNAVAILINSERV",ECA_UNAVAILINSERV);   
gen("ECA_CHANDESTROY",ECA_CHANDESTROY);     
gen("ECA_BADPRIORITY",ECA_BADPRIORITY);     
gen("ECA_NOTTHREADED",ECA_NOTTHREADED);     
gen("ECA_16KARRAYCLIENT", ECA_16KARRAYCLIENT)  ;
gen("ECA_CONNSEQTMO",ECA_CONNSEQTMO);      
gen("ECA_UNRESPTMO",ECA_UNRESPTMO);       

}
