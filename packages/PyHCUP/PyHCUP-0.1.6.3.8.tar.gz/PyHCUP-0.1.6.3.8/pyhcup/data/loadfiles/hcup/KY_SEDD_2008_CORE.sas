/*******************************************************************            
*   KY_SEDD_2008_CORE.SAS:                                                      
*      THE SAS CODE SHOWN BELOW WILL LOAD THE ASCII                             
*      INPATIENT STAY CORE FILE INTO SAS                                        
*******************************************************************/            
                                                                                
                                                                                
***********************************************;                                
*  Create SAS informats for missing values     ;                                
***********************************************;                                
PROC FORMAT;                                                                    
  INVALUE N2PF                                                                  
    '-9' = .                                                                    
    '-8' = .A                                                                   
    '-6' = .C                                                                   
    '-5' = .N                                                                   
    OTHER = (|2.|)                                                              
  ;                                                                             
  INVALUE N3PF                                                                  
    '-99' = .                                                                   
    '-88' = .A                                                                  
    '-66' = .C                                                                  
    OTHER = (|3.|)                                                              
  ;                                                                             
  INVALUE N4PF                                                                  
    '-999' = .                                                                  
    '-888' = .A                                                                 
    '-666' = .C                                                                 
    OTHER = (|4.|)                                                              
  ;                                                                             
  INVALUE N4P1F                                                                 
    '-9.9' = .                                                                  
    '-8.8' = .A                                                                 
    '-6.6' = .C                                                                 
    OTHER = (|4.1|)                                                             
  ;                                                                             
  INVALUE N5PF                                                                  
    '-9999' = .                                                                 
    '-8888' = .A                                                                
    '-6666' = .C                                                                
    OTHER = (|5.|)                                                              
  ;                                                                             
  INVALUE N5P2F                                                                 
    '-9.99' = .                                                                 
    '-8.88' = .A                                                                
    '-6.66' = .C                                                                
    OTHER = (|5.2|)                                                             
  ;                                                                             
  INVALUE N6PF                                                                  
    '-99999' = .                                                                
    '-88888' = .A                                                               
    '-66666' = .C                                                               
    OTHER = (|6.|)                                                              
  ;                                                                             
  INVALUE N6P2F                                                                 
    '-99.99' = .                                                                
    '-88.88' = .A                                                               
    '-66.66' = .C                                                               
    OTHER = (|6.2|)                                                             
  ;                                                                             
  INVALUE N7P2F                                                                 
    '-999.99' = .                                                               
    '-888.88' = .A                                                              
    '-666.66' = .C                                                              
    OTHER = (|7.2|)                                                             
  ;                                                                             
  INVALUE N7P4F                                                                 
    '-9.9999' = .                                                               
    '-8.8888' = .A                                                              
    '-6.6666' = .C                                                              
    OTHER = (|7.4|)                                                             
  ;                                                                             
  INVALUE N8PF                                                                  
    '-9999999' = .                                                              
    '-8888888' = .A                                                             
    '-6666666' = .C                                                             
    OTHER = (|8.|)                                                              
  ;                                                                             
  INVALUE N8P2F                                                                 
    '-9999.99' = .                                                              
    '-8888.88' = .A                                                             
    '-6666.66' = .C                                                             
    OTHER = (|8.2|)                                                             
  ;                                                                             
  INVALUE N9PF                                                                  
    '-99999999' = .                                                             
    '-88888888' = .A                                                            
    '-66666666' = .C                                                            
    OTHER = (|9.|)                                                              
  ;                                                                             
  INVALUE N9P2F                                                                 
    '-99999.99' = .                                                             
    '-88888.88' = .A                                                            
    '-66666.66' = .C                                                            
    OTHER = (|9.2|)                                                             
  ;                                                                             
  INVALUE N10PF                                                                 
    '-999999999' = .                                                            
    '-888888888' = .A                                                           
    '-666666666' = .C                                                           
    OTHER = (|10.|)                                                             
  ;                                                                             
  INVALUE N10P4F                                                                
    '-9999.9999' = .                                                            
    '-8888.8888' = .A                                                           
    '-6666.6666' = .C                                                           
    OTHER = (|10.4|)                                                            
  ;                                                                             
  INVALUE N10P5F                                                                
    '-999.99999' = .                                                            
    '-888.88888' = .A                                                           
    '-666.66666' = .C                                                           
    OTHER = (|10.5|)                                                            
  ;                                                                             
  INVALUE DATE10F                                                               
    '-999999999' = .                                                            
    '-888888888' = .A                                                           
    '-666666666' = .C                                                           
    OTHER = (|MMDDYY10.|)                                                       
  ;                                                                             
  INVALUE N11PF                                                                 
    '-9999999999' = .                                                           
    '-8888888888' = .A                                                          
    '-6666666666' = .C                                                          
    OTHER = (|11.|)                                                             
  ;                                                                             
  INVALUE N12P2F                                                                
    '-99999999.99' = .                                                          
    '-88888888.88' = .A                                                         
    '-66666666.66' = .C                                                         
    OTHER = (|12.2|)                                                            
  ;                                                                             
  INVALUE N12P5F                                                                
    '-99999.99999' = .                                                          
    '-88888.88888' = .A                                                         
    '-66666.66666' = .C                                                         
    OTHER = (|12.5|)                                                            
  ;                                                                             
  INVALUE N13PF                                                                 
    '-999999999999' = .                                                         
    '-888888888888' = .A                                                        
    '-666666666666' = .C                                                        
    OTHER = (|13.|)                                                             
  ;                                                                             
  INVALUE N15P2F                                                                
    '-99999999999.99' = .                                                       
    '-88888888888.88' = .A                                                      
    '-66666666666.66' = .C                                                      
    OTHER = (|15.2|)                                                            
  ;                                                                             
  RUN;                                                                          
                                                                                
                                                                                
*******************************;                                                
*  Data Step                  *;                                                
*******************************;                                                
DATA KY_SEDDC_2008_CORE;                                                        
INFILE 'KY_SEDD_2008_CORE.ASC' LRECL = 1372;                                    
                                                                                
*** Variable attribute ***;                                                     
ATTRIB                                                                          
  AGE                        LENGTH=3                                           
  LABEL="Age in years at admission"                                             
                                                                                
  AGEDAY                     LENGTH=3                                           
  LABEL="Age in days (when age < 1 year)"                                       
                                                                                
  AGEMONTH                   LENGTH=3                                           
  LABEL="Age in months (when age < 11 years)"                                   
                                                                                
  AMONTH                     LENGTH=3                                           
  LABEL="Admission month"                                                       
                                                                                
  ASOURCE                    LENGTH=3                                           
  LABEL="Admission source (uniform)"                                            
                                                                                
  ASOURCEUB92                LENGTH=$1                                          
  LABEL="Admission source (UB-92 standard coding)"                              
                                                                                
  ASOURCE_X                  LENGTH=$2                                          
  LABEL="Admission source (as received from source)"                            
                                                                                
  ATYPE                      LENGTH=3                                           
  LABEL="Admission type"                                                        
                                                                                
  AWEEKEND                   LENGTH=3                                           
  LABEL="Admission day is a weekend"                                            
                                                                                
  BILLTYPE                   LENGTH=$4                                          
  LABEL="UB-92 bill type"                                                       
                                                                                
  CPT1                       LENGTH=$5                                          
  LABEL="CPT/HCPCS procedure code 1"                                            
                                                                                
  CPT2                       LENGTH=$5                                          
  LABEL="CPT/HCPCS procedure code 2"                                            
                                                                                
  CPT3                       LENGTH=$5                                          
  LABEL="CPT/HCPCS procedure code 3"                                            
                                                                                
  CPT4                       LENGTH=$5                                          
  LABEL="CPT/HCPCS procedure code 4"                                            
                                                                                
  CPT5                       LENGTH=$5                                          
  LABEL="CPT/HCPCS procedure code 5"                                            
                                                                                
  CPT6                       LENGTH=$5                                          
  LABEL="CPT/HCPCS procedure code 6"                                            
                                                                                
  CPT7                       LENGTH=$5                                          
  LABEL="CPT/HCPCS procedure code 7"                                            
                                                                                
  CPT8                       LENGTH=$5                                          
  LABEL="CPT/HCPCS procedure code 8"                                            
                                                                                
  CPT9                       LENGTH=$5                                          
  LABEL="CPT/HCPCS procedure code 9"                                            
                                                                                
  CPT10                      LENGTH=$5                                          
  LABEL="CPT/HCPCS procedure code 10"                                           
                                                                                
  CPT11                      LENGTH=$5                                          
  LABEL="CPT/HCPCS procedure code 11"                                           
                                                                                
  CPT12                      LENGTH=$5                                          
  LABEL="CPT/HCPCS procedure code 12"                                           
                                                                                
  CPT13                      LENGTH=$5                                          
  LABEL="CPT/HCPCS procedure code 13"                                           
                                                                                
  CPT14                      LENGTH=$5                                          
  LABEL="CPT/HCPCS procedure code 14"                                           
                                                                                
  CPT15                      LENGTH=$5                                          
  LABEL="CPT/HCPCS procedure code 15"                                           
                                                                                
  CPT16                      LENGTH=$5                                          
  LABEL="CPT/HCPCS procedure code 16"                                           
                                                                                
  CPT17                      LENGTH=$5                                          
  LABEL="CPT/HCPCS procedure code 17"                                           
                                                                                
  CPT18                      LENGTH=$5                                          
  LABEL="CPT/HCPCS procedure code 18"                                           
                                                                                
  CPT19                      LENGTH=$5                                          
  LABEL="CPT/HCPCS procedure code 19"                                           
                                                                                
  CPT20                      LENGTH=$5                                          
  LABEL="CPT/HCPCS procedure code 20"                                           
                                                                                
  CPT21                      LENGTH=$5                                          
  LABEL="CPT/HCPCS procedure code 21"                                           
                                                                                
  CPT22                      LENGTH=$5                                          
  LABEL="CPT/HCPCS procedure code 22"                                           
                                                                                
  CPT23                      LENGTH=$5                                          
  LABEL="CPT/HCPCS procedure code 23"                                           
                                                                                
  CPT24                      LENGTH=$5                                          
  LABEL="CPT/HCPCS procedure code 24"                                           
                                                                                
  CPT25                      LENGTH=$5                                          
  LABEL="CPT/HCPCS procedure code 25"                                           
                                                                                
  CPTCCS1                    LENGTH=4                                           
  LABEL="CCS: CPT 1"                                                            
                                                                                
  CPTCCS2                    LENGTH=4                                           
  LABEL="CCS: CPT 2"                                                            
                                                                                
  CPTCCS3                    LENGTH=4                                           
  LABEL="CCS: CPT 3"                                                            
                                                                                
  CPTCCS4                    LENGTH=4                                           
  LABEL="CCS: CPT 4"                                                            
                                                                                
  CPTCCS5                    LENGTH=4                                           
  LABEL="CCS: CPT 5"                                                            
                                                                                
  CPTCCS6                    LENGTH=4                                           
  LABEL="CCS: CPT 6"                                                            
                                                                                
  CPTCCS7                    LENGTH=4                                           
  LABEL="CCS: CPT 7"                                                            
                                                                                
  CPTCCS8                    LENGTH=4                                           
  LABEL="CCS: CPT 8"                                                            
                                                                                
  CPTCCS9                    LENGTH=4                                           
  LABEL="CCS: CPT 9"                                                            
                                                                                
  CPTCCS10                   LENGTH=4                                           
  LABEL="CCS: CPT 10"                                                           
                                                                                
  CPTCCS11                   LENGTH=4                                           
  LABEL="CCS: CPT 11"                                                           
                                                                                
  CPTCCS12                   LENGTH=4                                           
  LABEL="CCS: CPT 12"                                                           
                                                                                
  CPTCCS13                   LENGTH=4                                           
  LABEL="CCS: CPT 13"                                                           
                                                                                
  CPTCCS14                   LENGTH=4                                           
  LABEL="CCS: CPT 14"                                                           
                                                                                
  CPTCCS15                   LENGTH=4                                           
  LABEL="CCS: CPT 15"                                                           
                                                                                
  CPTCCS16                   LENGTH=4                                           
  LABEL="CCS: CPT 16"                                                           
                                                                                
  CPTCCS17                   LENGTH=4                                           
  LABEL="CCS: CPT 17"                                                           
                                                                                
  CPTCCS18                   LENGTH=4                                           
  LABEL="CCS: CPT 18"                                                           
                                                                                
  CPTCCS19                   LENGTH=4                                           
  LABEL="CCS: CPT 19"                                                           
                                                                                
  CPTCCS20                   LENGTH=4                                           
  LABEL="CCS: CPT 20"                                                           
                                                                                
  CPTCCS21                   LENGTH=4                                           
  LABEL="CCS: CPT 21"                                                           
                                                                                
  CPTCCS22                   LENGTH=4                                           
  LABEL="CCS: CPT 22"                                                           
                                                                                
  CPTCCS23                   LENGTH=4                                           
  LABEL="CCS: CPT 23"                                                           
                                                                                
  CPTCCS24                   LENGTH=4                                           
  LABEL="CCS: CPT 24"                                                           
                                                                                
  CPTCCS25                   LENGTH=4                                           
  LABEL="CCS: CPT 25"                                                           
                                                                                
  CPTDAY1                    LENGTH=4                                           
  LABEL="Number of days from admission to CPT1"                                 
                                                                                
  CPTDAY2                    LENGTH=4                                           
  LABEL="Number of days from admission to CPT2"                                 
                                                                                
  CPTDAY3                    LENGTH=4                                           
  LABEL="Number of days from admission to CPT3"                                 
                                                                                
  CPTDAY4                    LENGTH=4                                           
  LABEL="Number of days from admission to CPT4"                                 
                                                                                
  CPTDAY5                    LENGTH=4                                           
  LABEL="Number of days from admission to CPT5"                                 
                                                                                
  CPTDAY6                    LENGTH=4                                           
  LABEL="Number of days from admission to CPT6"                                 
                                                                                
  CPTDAY7                    LENGTH=4                                           
  LABEL="Number of days from admission to CPT7"                                 
                                                                                
  CPTDAY8                    LENGTH=4                                           
  LABEL="Number of days from admission to CPT8"                                 
                                                                                
  CPTDAY9                    LENGTH=4                                           
  LABEL="Number of days from admission to CPT9"                                 
                                                                                
  CPTDAY10                   LENGTH=4                                           
  LABEL="Number of days from admission to CPT10"                                
                                                                                
  CPTDAY11                   LENGTH=4                                           
  LABEL="Number of days from admission to CPT11"                                
                                                                                
  CPTDAY12                   LENGTH=4                                           
  LABEL="Number of days from admission to CPT12"                                
                                                                                
  CPTDAY13                   LENGTH=4                                           
  LABEL="Number of days from admission to CPT13"                                
                                                                                
  CPTDAY14                   LENGTH=4                                           
  LABEL="Number of days from admission to CPT14"                                
                                                                                
  CPTDAY15                   LENGTH=4                                           
  LABEL="Number of days from admission to CPT15"                                
                                                                                
  CPTDAY16                   LENGTH=4                                           
  LABEL="Number of days from admission to CPT16"                                
                                                                                
  CPTDAY17                   LENGTH=4                                           
  LABEL="Number of days from admission to CPT17"                                
                                                                                
  CPTDAY18                   LENGTH=4                                           
  LABEL="Number of days from admission to CPT18"                                
                                                                                
  CPTDAY19                   LENGTH=4                                           
  LABEL="Number of days from admission to CPT19"                                
                                                                                
  CPTDAY20                   LENGTH=4                                           
  LABEL="Number of days from admission to CPT20"                                
                                                                                
  CPTDAY21                   LENGTH=4                                           
  LABEL="Number of days from admission to CPT21"                                
                                                                                
  CPTDAY22                   LENGTH=4                                           
  LABEL="Number of days from admission to CPT22"                                
                                                                                
  CPTDAY23                   LENGTH=4                                           
  LABEL="Number of days from admission to CPT23"                                
                                                                                
  CPTDAY24                   LENGTH=4                                           
  LABEL="Number of days from admission to CPT24"                                
                                                                                
  CPTDAY25                   LENGTH=4                                           
  LABEL="Number of days from admission to CPT25"                                
                                                                                
  CPTM1_1                    LENGTH=$2                                          
  LABEL="First CPT-4/HCPCS modifier 1"                                          
                                                                                
  CPTM1_2                    LENGTH=$2                                          
  LABEL="First CPT-4/HCPCS modifier 2"                                          
                                                                                
  CPTM1_3                    LENGTH=$2                                          
  LABEL="First CPT-4/HCPCS modifier 3"                                          
                                                                                
  CPTM1_4                    LENGTH=$2                                          
  LABEL="First CPT-4/HCPCS modifier 4"                                          
                                                                                
  CPTM1_5                    LENGTH=$2                                          
  LABEL="First CPT-4/HCPCS modifier 5"                                          
                                                                                
  CPTM1_6                    LENGTH=$2                                          
  LABEL="First CPT-4/HCPCS modifier 6"                                          
                                                                                
  CPTM1_7                    LENGTH=$2                                          
  LABEL="First CPT-4/HCPCS modifier 7"                                          
                                                                                
  CPTM1_8                    LENGTH=$2                                          
  LABEL="First CPT-4/HCPCS modifier 8"                                          
                                                                                
  CPTM1_9                    LENGTH=$2                                          
  LABEL="First CPT-4/HCPCS modifier 9"                                          
                                                                                
  CPTM1_10                   LENGTH=$2                                          
  LABEL="First CPT-4/HCPCS modifier 10"                                         
                                                                                
  CPTM1_11                   LENGTH=$2                                          
  LABEL="First CPT-4/HCPCS modifier 11"                                         
                                                                                
  CPTM1_12                   LENGTH=$2                                          
  LABEL="First CPT-4/HCPCS modifier 12"                                         
                                                                                
  CPTM1_13                   LENGTH=$2                                          
  LABEL="First CPT-4/HCPCS modifier 13"                                         
                                                                                
  CPTM1_14                   LENGTH=$2                                          
  LABEL="First CPT-4/HCPCS modifier 14"                                         
                                                                                
  CPTM1_15                   LENGTH=$2                                          
  LABEL="First CPT-4/HCPCS modifier 15"                                         
                                                                                
  CPTM1_16                   LENGTH=$2                                          
  LABEL="First CPT-4/HCPCS modifier 16"                                         
                                                                                
  CPTM1_17                   LENGTH=$2                                          
  LABEL="First CPT-4/HCPCS modifier 17"                                         
                                                                                
  CPTM1_18                   LENGTH=$2                                          
  LABEL="First CPT-4/HCPCS modifier 18"                                         
                                                                                
  CPTM1_19                   LENGTH=$2                                          
  LABEL="First CPT-4/HCPCS modifier 19"                                         
                                                                                
  CPTM1_20                   LENGTH=$2                                          
  LABEL="First CPT-4/HCPCS modifier 20"                                         
                                                                                
  CPTM1_21                   LENGTH=$2                                          
  LABEL="First CPT-4/HCPCS modifier 21"                                         
                                                                                
  CPTM1_22                   LENGTH=$2                                          
  LABEL="First CPT-4/HCPCS modifier 22"                                         
                                                                                
  CPTM1_23                   LENGTH=$2                                          
  LABEL="First CPT-4/HCPCS modifier 23"                                         
                                                                                
  CPTM1_24                   LENGTH=$2                                          
  LABEL="First CPT-4/HCPCS modifier 24"                                         
                                                                                
  CPTM1_25                   LENGTH=$2                                          
  LABEL="First CPT-4/HCPCS modifier 25"                                         
                                                                                
  CPTM2_1                    LENGTH=$2                                          
  LABEL="Second CPT-4/HCPCS modifier 1"                                         
                                                                                
  CPTM2_2                    LENGTH=$2                                          
  LABEL="Second CPT-4/HCPCS modifier 2"                                         
                                                                                
  CPTM2_3                    LENGTH=$2                                          
  LABEL="Second CPT-4/HCPCS modifier 3"                                         
                                                                                
  CPTM2_4                    LENGTH=$2                                          
  LABEL="Second CPT-4/HCPCS modifier 4"                                         
                                                                                
  CPTM2_5                    LENGTH=$2                                          
  LABEL="Second CPT-4/HCPCS modifier 5"                                         
                                                                                
  CPTM2_6                    LENGTH=$2                                          
  LABEL="Second CPT-4/HCPCS modifier 6"                                         
                                                                                
  CPTM2_7                    LENGTH=$2                                          
  LABEL="Second CPT-4/HCPCS modifier 7"                                         
                                                                                
  CPTM2_8                    LENGTH=$2                                          
  LABEL="Second CPT-4/HCPCS modifier 8"                                         
                                                                                
  CPTM2_9                    LENGTH=$2                                          
  LABEL="Second CPT-4/HCPCS modifier 9"                                         
                                                                                
  CPTM2_10                   LENGTH=$2                                          
  LABEL="Second CPT-4/HCPCS modifier 10"                                        
                                                                                
  CPTM2_11                   LENGTH=$2                                          
  LABEL="Second CPT-4/HCPCS modifier 11"                                        
                                                                                
  CPTM2_12                   LENGTH=$2                                          
  LABEL="Second CPT-4/HCPCS modifier 12"                                        
                                                                                
  CPTM2_13                   LENGTH=$2                                          
  LABEL="Second CPT-4/HCPCS modifier 13"                                        
                                                                                
  CPTM2_14                   LENGTH=$2                                          
  LABEL="Second CPT-4/HCPCS modifier 14"                                        
                                                                                
  CPTM2_15                   LENGTH=$2                                          
  LABEL="Second CPT-4/HCPCS modifier 15"                                        
                                                                                
  CPTM2_16                   LENGTH=$2                                          
  LABEL="Second CPT-4/HCPCS modifier 16"                                        
                                                                                
  CPTM2_17                   LENGTH=$2                                          
  LABEL="Second CPT-4/HCPCS modifier 17"                                        
                                                                                
  CPTM2_18                   LENGTH=$2                                          
  LABEL="Second CPT-4/HCPCS modifier 18"                                        
                                                                                
  CPTM2_19                   LENGTH=$2                                          
  LABEL="Second CPT-4/HCPCS modifier 19"                                        
                                                                                
  CPTM2_20                   LENGTH=$2                                          
  LABEL="Second CPT-4/HCPCS modifier 20"                                        
                                                                                
  CPTM2_21                   LENGTH=$2                                          
  LABEL="Second CPT-4/HCPCS modifier 21"                                        
                                                                                
  CPTM2_22                   LENGTH=$2                                          
  LABEL="Second CPT-4/HCPCS modifier 22"                                        
                                                                                
  CPTM2_23                   LENGTH=$2                                          
  LABEL="Second CPT-4/HCPCS modifier 23"                                        
                                                                                
  CPTM2_24                   LENGTH=$2                                          
  LABEL="Second CPT-4/HCPCS modifier 24"                                        
                                                                                
  CPTM2_25                   LENGTH=$2                                          
  LABEL="Second CPT-4/HCPCS modifier 25"                                        
                                                                                
  DIED                       LENGTH=3                                           
  LABEL="Died during hospitalization"                                           
                                                                                
  DISPUB04                   LENGTH=3                                           
  LABEL="Disposition of patient (UB-04 standard coding)"                        
                                                                                
  DISPUNIFORM                LENGTH=3                                           
  LABEL="Disposition of patient (uniform)"                                      
                                                                                
  DISP_X                     LENGTH=$2                                          
  LABEL="Disposition of patient (as received from source)"                      
                                                                                
  DQTR                       LENGTH=3                                           
  LABEL="Discharge quarter"                                                     
                                                                                
  DSHOSPID                   LENGTH=$13                                         
  LABEL="Data source hospital identifier"                                       
                                                                                
  DX1                        LENGTH=$5                                          
  LABEL="Diagnosis 1"                                                           
                                                                                
  DX2                        LENGTH=$5                                          
  LABEL="Diagnosis 2"                                                           
                                                                                
  DX3                        LENGTH=$5                                          
  LABEL="Diagnosis 3"                                                           
                                                                                
  DX4                        LENGTH=$5                                          
  LABEL="Diagnosis 4"                                                           
                                                                                
  DX5                        LENGTH=$5                                          
  LABEL="Diagnosis 5"                                                           
                                                                                
  DX6                        LENGTH=$5                                          
  LABEL="Diagnosis 6"                                                           
                                                                                
  DX7                        LENGTH=$5                                          
  LABEL="Diagnosis 7"                                                           
                                                                                
  DX8                        LENGTH=$5                                          
  LABEL="Diagnosis 8"                                                           
                                                                                
  DX9                        LENGTH=$5                                          
  LABEL="Diagnosis 9"                                                           
                                                                                
  DX10                       LENGTH=$5                                          
  LABEL="Diagnosis 10"                                                          
                                                                                
  DX11                       LENGTH=$5                                          
  LABEL="Diagnosis 11"                                                          
                                                                                
  DX12                       LENGTH=$5                                          
  LABEL="Diagnosis 12"                                                          
                                                                                
  DX13                       LENGTH=$5                                          
  LABEL="Diagnosis 13"                                                          
                                                                                
  DX14                       LENGTH=$5                                          
  LABEL="Diagnosis 14"                                                          
                                                                                
  DX15                       LENGTH=$5                                          
  LABEL="Diagnosis 15"                                                          
                                                                                
  DX16                       LENGTH=$5                                          
  LABEL="Diagnosis 16"                                                          
                                                                                
  DX17                       LENGTH=$5                                          
  LABEL="Diagnosis 17"                                                          
                                                                                
  DX18                       LENGTH=$5                                          
  LABEL="Diagnosis 18"                                                          
                                                                                
  DX19                       LENGTH=$5                                          
  LABEL="Diagnosis 19"                                                          
                                                                                
  DX20                       LENGTH=$5                                          
  LABEL="Diagnosis 20"                                                          
                                                                                
  DX21                       LENGTH=$5                                          
  LABEL="Diagnosis 21"                                                          
                                                                                
  DX22                       LENGTH=$5                                          
  LABEL="Diagnosis 22"                                                          
                                                                                
  DX23                       LENGTH=$5                                          
  LABEL="Diagnosis 23"                                                          
                                                                                
  DX24                       LENGTH=$5                                          
  LABEL="Diagnosis 24"                                                          
                                                                                
  DX25                       LENGTH=$5                                          
  LABEL="Diagnosis 25"                                                          
                                                                                
  DXCCS1                     LENGTH=4                                           
  LABEL="CCS: diagnosis 1"                                                      
                                                                                
  DXCCS2                     LENGTH=4                                           
  LABEL="CCS: diagnosis 2"                                                      
                                                                                
  DXCCS3                     LENGTH=4                                           
  LABEL="CCS: diagnosis 3"                                                      
                                                                                
  DXCCS4                     LENGTH=4                                           
  LABEL="CCS: diagnosis 4"                                                      
                                                                                
  DXCCS5                     LENGTH=4                                           
  LABEL="CCS: diagnosis 5"                                                      
                                                                                
  DXCCS6                     LENGTH=4                                           
  LABEL="CCS: diagnosis 6"                                                      
                                                                                
  DXCCS7                     LENGTH=4                                           
  LABEL="CCS: diagnosis 7"                                                      
                                                                                
  DXCCS8                     LENGTH=4                                           
  LABEL="CCS: diagnosis 8"                                                      
                                                                                
  DXCCS9                     LENGTH=4                                           
  LABEL="CCS: diagnosis 9"                                                      
                                                                                
  DXCCS10                    LENGTH=4                                           
  LABEL="CCS: diagnosis 10"                                                     
                                                                                
  DXCCS11                    LENGTH=4                                           
  LABEL="CCS: diagnosis 11"                                                     
                                                                                
  DXCCS12                    LENGTH=4                                           
  LABEL="CCS: diagnosis 12"                                                     
                                                                                
  DXCCS13                    LENGTH=4                                           
  LABEL="CCS: diagnosis 13"                                                     
                                                                                
  DXCCS14                    LENGTH=4                                           
  LABEL="CCS: diagnosis 14"                                                     
                                                                                
  DXCCS15                    LENGTH=4                                           
  LABEL="CCS: diagnosis 15"                                                     
                                                                                
  DXCCS16                    LENGTH=4                                           
  LABEL="CCS: diagnosis 16"                                                     
                                                                                
  DXCCS17                    LENGTH=4                                           
  LABEL="CCS: diagnosis 17"                                                     
                                                                                
  DXCCS18                    LENGTH=4                                           
  LABEL="CCS: diagnosis 18"                                                     
                                                                                
  DXCCS19                    LENGTH=4                                           
  LABEL="CCS: diagnosis 19"                                                     
                                                                                
  DXCCS20                    LENGTH=4                                           
  LABEL="CCS: diagnosis 20"                                                     
                                                                                
  DXCCS21                    LENGTH=4                                           
  LABEL="CCS: diagnosis 21"                                                     
                                                                                
  DXCCS22                    LENGTH=4                                           
  LABEL="CCS: diagnosis 22"                                                     
                                                                                
  DXCCS23                    LENGTH=4                                           
  LABEL="CCS: diagnosis 23"                                                     
                                                                                
  DXCCS24                    LENGTH=4                                           
  LABEL="CCS: diagnosis 24"                                                     
                                                                                
  DXCCS25                    LENGTH=4                                           
  LABEL="CCS: diagnosis 25"                                                     
                                                                                
  DX_Visit_Reason1           LENGTH=$5                                          
  LABEL="Reason for visit diagnosis 1"                                          
                                                                                
  DX_Visit_Reason2           LENGTH=$5                                          
  LABEL="Reason for visit diagnosis 2"                                          
                                                                                
  DX_Visit_Reason3           LENGTH=$5                                          
  LABEL="Reason for visit diagnosis 3"                                          
                                                                                
  ECODE1                     LENGTH=$5                                          
  LABEL="E code 1"                                                              
                                                                                
  ECODE2                     LENGTH=$5                                          
  LABEL="E code 2"                                                              
                                                                                
  ECODE3                     LENGTH=$5                                          
  LABEL="E code 3"                                                              
                                                                                
  ECODE4                     LENGTH=$5                                          
  LABEL="E code 4"                                                              
                                                                                
  ECODE5                     LENGTH=$5                                          
  LABEL="E code 5"                                                              
                                                                                
  ECODE6                     LENGTH=$5                                          
  LABEL="E code 6"                                                              
                                                                                
  ECODE7                     LENGTH=$5                                          
  LABEL="E code 7"                                                              
                                                                                
  ECODE8                     LENGTH=$5                                          
  LABEL="E code 8"                                                              
                                                                                
  E_CCS1                     LENGTH=3                                           
  LABEL="CCS: E Code 1"                                                         
                                                                                
  E_CCS2                     LENGTH=3                                           
  LABEL="CCS: E Code 2"                                                         
                                                                                
  E_CCS3                     LENGTH=3                                           
  LABEL="CCS: E Code 3"                                                         
                                                                                
  E_CCS4                     LENGTH=3                                           
  LABEL="CCS: E Code 4"                                                         
                                                                                
  E_CCS5                     LENGTH=3                                           
  LABEL="CCS: E Code 5"                                                         
                                                                                
  E_CCS6                     LENGTH=3                                           
  LABEL="CCS: E Code 6"                                                         
                                                                                
  E_CCS7                     LENGTH=3                                           
  LABEL="CCS: E Code 7"                                                         
                                                                                
  E_CCS8                     LENGTH=3                                           
  LABEL="CCS: E Code 8"                                                         
                                                                                
  FEMALE                     LENGTH=3                                           
  LABEL="Indicator of sex"                                                      
                                                                                
  HCUP_AS                    LENGTH=3                                           
  LABEL="HCUP Ambulatory Surgery service indicator"                             
                                                                                
  HCUP_ED                    LENGTH=3                                           
  LABEL="HCUP Emergency Department service indicator"                           
                                                                                
  HCUP_OS                    LENGTH=3                                           
  LABEL="HCUP Observation Stay service indicator"                               
                                                                                
  HISPANIC_X                 LENGTH=$2                                          
  LABEL="Hispanic ethnicity (as received from source)"                          
                                                                                
  HOSPBRTH                   LENGTH=3                                           
  LABEL="Indicator of birth in this hospital"                                   
                                                                                
  HOSPST                     LENGTH=$2                                          
  LABEL="Hospital state postal code"                                            
                                                                                
  KEY                        LENGTH=8                 FORMAT=Z14.               
  LABEL="HCUP record identifier"                                                
                                                                                
  LOS                        LENGTH=4                                           
  LABEL="Length of stay (cleaned)"                                              
                                                                                
  LOS_X                      LENGTH=4                                           
  LABEL="Length of stay (as received from source)"                              
                                                                                
  MDNUM1_R                   LENGTH=5                                           
  LABEL="Physician 1 number (re-identified)"                                    
                                                                                
  MDNUM2_R                   LENGTH=5                                           
  LABEL="Physician 2 number (re-identified)"                                    
                                                                                
  MEDINCSTQ                  LENGTH=3                                           
  LABEL="Median household income state quartile for patient ZIP Code"           
                                                                                
  NCPT                       LENGTH=3                                           
  LABEL="Number of CPT/HCPCS procedures on this record"                         
                                                                                
  NDX                        LENGTH=3                                           
  LABEL="Number of diagnoses on this record"                                    
                                                                                
  NECODE                     LENGTH=3                                           
  LABEL="Number of E codes on this record"                                      
                                                                                
  NEOMAT                     LENGTH=3                                           
  LABEL="Neonatal and/or maternal DX and/or PR"                                 
                                                                                
  NPR                        LENGTH=3                                           
  LABEL="Number of procedures on this record"                                   
                                                                                
  OPservice                  LENGTH=$2                                          
  LABEL="Indicator of outpatient service (as received from source)"             
                                                                                
  PAY1                       LENGTH=3                                           
  LABEL="Primary expected payer (uniform)"                                      
                                                                                
  PAY1_X                     LENGTH=$4                                          
  LABEL="Primary expected payer (as received from source)"                      
                                                                                
  PAY2                       LENGTH=3                                           
  LABEL="Secondary expected payer (uniform)"                                    
                                                                                
  PAY2_X                     LENGTH=$4                                          
  LABEL="Secondary expected payer (as received from source)"                    
                                                                                
  PAY3_X                     LENGTH=$4                                          
  LABEL="Tertiary expected payer (as received from source)"                     
                                                                                
  PL_CBSA                    LENGTH=3                                           
  LABEL="Patient location: Core Based Statistical Area (CBSA)"                  
                                                                                
  PL_MSA1993                 LENGTH=3                                           
  LABEL="Patient location: Metropolitan Statistical Area (MSA), 1993"           
                                                                                
  PL_NCHS2006                LENGTH=3                                           
  LABEL="Patient Location: NCHS Urban-Rural Code (V2006)"                       
                                                                                
  PL_RUCA10_2005             LENGTH=3                                           
  LABEL="Patient location: Rural-Urban Commuting Area (RUCA) Codes, ten levels" 
                                                                                
  PL_RUCA2005                LENGTH=4                 FORMAT=4.1                
  LABEL="Patient location: Rural-Urban Commuting Area (RUCA) Codes"             
                                                                                
  PL_RUCA4_2005              LENGTH=3                                           
  LABEL="Patient location: Rural-Urban Commuting Area (RUCA) Codes, four levels"
                                                                                
  PL_RUCC2003                LENGTH=3                                           
  LABEL="Patient location: Rural-Urban Continuum Codes(RUCC), 2003"             
                                                                                
  PL_UIC2003                 LENGTH=3                                           
  LABEL="Patient location: Urban Influence Codes, 2003"                         
                                                                                
  PL_UR_CAT4                 LENGTH=3                                           
  LABEL="Patient Location: Urban-Rural 4 Categories"                            
                                                                                
  PR1                        LENGTH=$4                                          
  LABEL="Procedure 1"                                                           
                                                                                
  PR2                        LENGTH=$4                                          
  LABEL="Procedure 2"                                                           
                                                                                
  PR3                        LENGTH=$4                                          
  LABEL="Procedure 3"                                                           
                                                                                
  PR4                        LENGTH=$4                                          
  LABEL="Procedure 4"                                                           
                                                                                
  PR5                        LENGTH=$4                                          
  LABEL="Procedure 5"                                                           
                                                                                
  PR6                        LENGTH=$4                                          
  LABEL="Procedure 6"                                                           
                                                                                
  PR7                        LENGTH=$4                                          
  LABEL="Procedure 7"                                                           
                                                                                
  PR8                        LENGTH=$4                                          
  LABEL="Procedure 8"                                                           
                                                                                
  PR9                        LENGTH=$4                                          
  LABEL="Procedure 9"                                                           
                                                                                
  PR10                       LENGTH=$4                                          
  LABEL="Procedure 10"                                                          
                                                                                
  PR11                       LENGTH=$4                                          
  LABEL="Procedure 11"                                                          
                                                                                
  PR12                       LENGTH=$4                                          
  LABEL="Procedure 12"                                                          
                                                                                
  PR13                       LENGTH=$4                                          
  LABEL="Procedure 13"                                                          
                                                                                
  PR14                       LENGTH=$4                                          
  LABEL="Procedure 14"                                                          
                                                                                
  PR15                       LENGTH=$4                                          
  LABEL="Procedure 15"                                                          
                                                                                
  PR16                       LENGTH=$4                                          
  LABEL="Procedure 16"                                                          
                                                                                
  PR17                       LENGTH=$4                                          
  LABEL="Procedure 17"                                                          
                                                                                
  PR18                       LENGTH=$4                                          
  LABEL="Procedure 18"                                                          
                                                                                
  PR19                       LENGTH=$4                                          
  LABEL="Procedure 19"                                                          
                                                                                
  PR20                       LENGTH=$4                                          
  LABEL="Procedure 20"                                                          
                                                                                
  PR21                       LENGTH=$4                                          
  LABEL="Procedure 21"                                                          
                                                                                
  PR22                       LENGTH=$4                                          
  LABEL="Procedure 22"                                                          
                                                                                
  PR23                       LENGTH=$4                                          
  LABEL="Procedure 23"                                                          
                                                                                
  PR24                       LENGTH=$4                                          
  LABEL="Procedure 24"                                                          
                                                                                
  PR25                       LENGTH=$4                                          
  LABEL="Procedure 25"                                                          
                                                                                
  PRCCS1                     LENGTH=3                                           
  LABEL="CCS: procedure 1"                                                      
                                                                                
  PRCCS2                     LENGTH=3                                           
  LABEL="CCS: procedure 2"                                                      
                                                                                
  PRCCS3                     LENGTH=3                                           
  LABEL="CCS: procedure 3"                                                      
                                                                                
  PRCCS4                     LENGTH=3                                           
  LABEL="CCS: procedure 4"                                                      
                                                                                
  PRCCS5                     LENGTH=3                                           
  LABEL="CCS: procedure 5"                                                      
                                                                                
  PRCCS6                     LENGTH=3                                           
  LABEL="CCS: procedure 6"                                                      
                                                                                
  PRCCS7                     LENGTH=3                                           
  LABEL="CCS: procedure 7"                                                      
                                                                                
  PRCCS8                     LENGTH=3                                           
  LABEL="CCS: procedure 8"                                                      
                                                                                
  PRCCS9                     LENGTH=3                                           
  LABEL="CCS: procedure 9"                                                      
                                                                                
  PRCCS10                    LENGTH=3                                           
  LABEL="CCS: procedure 10"                                                     
                                                                                
  PRCCS11                    LENGTH=3                                           
  LABEL="CCS: procedure 11"                                                     
                                                                                
  PRCCS12                    LENGTH=3                                           
  LABEL="CCS: procedure 12"                                                     
                                                                                
  PRCCS13                    LENGTH=3                                           
  LABEL="CCS: procedure 13"                                                     
                                                                                
  PRCCS14                    LENGTH=3                                           
  LABEL="CCS: procedure 14"                                                     
                                                                                
  PRCCS15                    LENGTH=3                                           
  LABEL="CCS: procedure 15"                                                     
                                                                                
  PRCCS16                    LENGTH=3                                           
  LABEL="CCS: procedure 16"                                                     
                                                                                
  PRCCS17                    LENGTH=3                                           
  LABEL="CCS: procedure 17"                                                     
                                                                                
  PRCCS18                    LENGTH=3                                           
  LABEL="CCS: procedure 18"                                                     
                                                                                
  PRCCS19                    LENGTH=3                                           
  LABEL="CCS: procedure 19"                                                     
                                                                                
  PRCCS20                    LENGTH=3                                           
  LABEL="CCS: procedure 20"                                                     
                                                                                
  PRCCS21                    LENGTH=3                                           
  LABEL="CCS: procedure 21"                                                     
                                                                                
  PRCCS22                    LENGTH=3                                           
  LABEL="CCS: procedure 22"                                                     
                                                                                
  PRCCS23                    LENGTH=3                                           
  LABEL="CCS: procedure 23"                                                     
                                                                                
  PRCCS24                    LENGTH=3                                           
  LABEL="CCS: procedure 24"                                                     
                                                                                
  PRCCS25                    LENGTH=3                                           
  LABEL="CCS: procedure 25"                                                     
                                                                                
  PRDAY1                     LENGTH=4                                           
  LABEL="Number of days from admission to PR1"                                  
                                                                                
  PRDAY2                     LENGTH=4                                           
  LABEL="Number of days from admission to PR2"                                  
                                                                                
  PRDAY3                     LENGTH=4                                           
  LABEL="Number of days from admission to PR3"                                  
                                                                                
  PRDAY4                     LENGTH=4                                           
  LABEL="Number of days from admission to PR4"                                  
                                                                                
  PRDAY5                     LENGTH=4                                           
  LABEL="Number of days from admission to PR5"                                  
                                                                                
  PRDAY6                     LENGTH=4                                           
  LABEL="Number of days from admission to PR6"                                  
                                                                                
  PRDAY7                     LENGTH=4                                           
  LABEL="Number of days from admission to PR7"                                  
                                                                                
  PRDAY8                     LENGTH=4                                           
  LABEL="Number of days from admission to PR8"                                  
                                                                                
  PRDAY9                     LENGTH=4                                           
  LABEL="Number of days from admission to PR9"                                  
                                                                                
  PRDAY10                    LENGTH=4                                           
  LABEL="Number of days from admission to PR10"                                 
                                                                                
  PRDAY11                    LENGTH=4                                           
  LABEL="Number of days from admission to PR11"                                 
                                                                                
  PRDAY12                    LENGTH=4                                           
  LABEL="Number of days from admission to PR12"                                 
                                                                                
  PRDAY13                    LENGTH=4                                           
  LABEL="Number of days from admission to PR13"                                 
                                                                                
  PRDAY14                    LENGTH=4                                           
  LABEL="Number of days from admission to PR14"                                 
                                                                                
  PRDAY15                    LENGTH=4                                           
  LABEL="Number of days from admission to PR15"                                 
                                                                                
  PRDAY16                    LENGTH=4                                           
  LABEL="Number of days from admission to PR16"                                 
                                                                                
  PRDAY17                    LENGTH=4                                           
  LABEL="Number of days from admission to PR17"                                 
                                                                                
  PRDAY18                    LENGTH=4                                           
  LABEL="Number of days from admission to PR18"                                 
                                                                                
  PRDAY19                    LENGTH=4                                           
  LABEL="Number of days from admission to PR19"                                 
                                                                                
  PRDAY20                    LENGTH=4                                           
  LABEL="Number of days from admission to PR20"                                 
                                                                                
  PRDAY21                    LENGTH=4                                           
  LABEL="Number of days from admission to PR21"                                 
                                                                                
  PRDAY22                    LENGTH=4                                           
  LABEL="Number of days from admission to PR22"                                 
                                                                                
  PRDAY23                    LENGTH=4                                           
  LABEL="Number of days from admission to PR23"                                 
                                                                                
  PRDAY24                    LENGTH=4                                           
  LABEL="Number of days from admission to PR24"                                 
                                                                                
  PRDAY25                    LENGTH=4                                           
  LABEL="Number of days from admission to PR25"                                 
                                                                                
  PROCTYPE                   LENGTH=3                                           
  LABEL="Procedure type indicator"                                              
                                                                                
  PSTATE                     LENGTH=$2                                          
  LABEL="Patient State postal code"                                             
                                                                                
  PSTCO                      LENGTH=4                 FORMAT=Z5.                
  LABEL="Patient state/county FIPS code"                                        
                                                                                
  PSTCO2                     LENGTH=4                 FORMAT=Z5.                
  LABEL="Patient state/county FIPS code, possibly derived from ZIP Code"        
                                                                                
  PointOfOriginUB04          LENGTH=$1                                          
  LABEL="Point of origin for admission or visit, UB-04 standard coding"         
                                                                                
  PointOfOrigin_X            LENGTH=$2                                          
  LABEL="Point of origin for admission or visit, as received from source"       
                                                                                
  RACE                       LENGTH=3                                           
  LABEL="Race (uniform)"                                                        
                                                                                
  RACE_X                     LENGTH=$2                                          
  LABEL="Race (as received from source)"                                        
                                                                                
  STATE_AS                   LENGTH=3                                           
  LABEL="State Ambulatory Surgery service indicator"                            
                                                                                
  STATE_ED                   LENGTH=3                                           
  LABEL="State Emergency Department service indicator"                          
                                                                                
  STATE_OS                   LENGTH=3                                           
  LABEL="State Observation Stay service indicator"                              
                                                                                
  TOTCHG                     LENGTH=6                                           
  LABEL="Total charges (cleaned)"                                               
                                                                                
  TOTCHG_X                   LENGTH=7                                           
  LABEL="Total charges (as received from source)"                               
                                                                                
  YEAR                       LENGTH=3                                           
  LABEL="Calendar year"                                                         
                                                                                
  ZIPINC_QRTL                LENGTH=3                                           
  LABEL="Median household income national quartile for patient ZIP Code"        
                                                                                
  ZIP                        LENGTH=$5                                          
  LABEL="Patient ZIP Code"                                                      
                                                                                
  AYEAR                      LENGTH=3                                           
  LABEL="Admission year"                                                        
                                                                                
  DMONTH                     LENGTH=3                                           
  LABEL="Discharge month"                                                       
                                                                                
  BMONTH                     LENGTH=3                                           
  LABEL="Birth month"                                                           
                                                                                
  BYEAR                      LENGTH=3                                           
  LABEL="Birth year"                                                            
                                                                                
  PRMONTH1                   LENGTH=3                                           
  LABEL="Month of procedure 1"                                                  
                                                                                
  PRMONTH2                   LENGTH=3                                           
  LABEL="Month of procedure 2"                                                  
                                                                                
  PRMONTH3                   LENGTH=3                                           
  LABEL="Month of procedure 3"                                                  
                                                                                
  PRMONTH4                   LENGTH=3                                           
  LABEL="Month of procedure 4"                                                  
                                                                                
  PRMONTH5                   LENGTH=3                                           
  LABEL="Month of procedure 5"                                                  
                                                                                
  PRMONTH6                   LENGTH=3                                           
  LABEL="Month of procedure 6"                                                  
                                                                                
  PRMONTH7                   LENGTH=3                                           
  LABEL="Month of procedure 7"                                                  
                                                                                
  PRMONTH8                   LENGTH=3                                           
  LABEL="Month of procedure 8"                                                  
                                                                                
  PRMONTH9                   LENGTH=3                                           
  LABEL="Month of procedure 9"                                                  
                                                                                
  PRMONTH10                  LENGTH=3                                           
  LABEL="Month of procedure 10"                                                 
                                                                                
  PRMONTH11                  LENGTH=3                                           
  LABEL="Month of procedure 11"                                                 
                                                                                
  PRMONTH12                  LENGTH=3                                           
  LABEL="Month of procedure 12"                                                 
                                                                                
  PRMONTH13                  LENGTH=3                                           
  LABEL="Month of procedure 13"                                                 
                                                                                
  PRMONTH14                  LENGTH=3                                           
  LABEL="Month of procedure 14"                                                 
                                                                                
  PRMONTH15                  LENGTH=3                                           
  LABEL="Month of procedure 15"                                                 
                                                                                
  PRMONTH16                  LENGTH=3                                           
  LABEL="Month of procedure 16"                                                 
                                                                                
  PRMONTH17                  LENGTH=3                                           
  LABEL="Month of procedure 17"                                                 
                                                                                
  PRMONTH18                  LENGTH=3                                           
  LABEL="Month of procedure 18"                                                 
                                                                                
  PRMONTH19                  LENGTH=3                                           
  LABEL="Month of procedure 19"                                                 
                                                                                
  PRMONTH20                  LENGTH=3                                           
  LABEL="Month of procedure 20"                                                 
                                                                                
  PRMONTH21                  LENGTH=3                                           
  LABEL="Month of procedure 21"                                                 
                                                                                
  PRMONTH22                  LENGTH=3                                           
  LABEL="Month of procedure 22"                                                 
                                                                                
  PRMONTH23                  LENGTH=3                                           
  LABEL="Month of procedure 23"                                                 
                                                                                
  PRMONTH24                  LENGTH=3                                           
  LABEL="Month of procedure 24"                                                 
                                                                                
  PRMONTH25                  LENGTH=3                                           
  LABEL="Month of procedure 25"                                                 
                                                                                
  PRYEAR1                    LENGTH=3                                           
  LABEL="Year of procedure 1"                                                   
                                                                                
  PRYEAR2                    LENGTH=3                                           
  LABEL="Year of procedure 2"                                                   
                                                                                
  PRYEAR3                    LENGTH=3                                           
  LABEL="Year of procedure 3"                                                   
                                                                                
  PRYEAR4                    LENGTH=3                                           
  LABEL="Year of procedure 4"                                                   
                                                                                
  PRYEAR5                    LENGTH=3                                           
  LABEL="Year of procedure 5"                                                   
                                                                                
  PRYEAR6                    LENGTH=3                                           
  LABEL="Year of procedure 6"                                                   
                                                                                
  PRYEAR7                    LENGTH=3                                           
  LABEL="Year of procedure 7"                                                   
                                                                                
  PRYEAR8                    LENGTH=3                                           
  LABEL="Year of procedure 8"                                                   
                                                                                
  PRYEAR9                    LENGTH=3                                           
  LABEL="Year of procedure 9"                                                   
                                                                                
  PRYEAR10                   LENGTH=3                                           
  LABEL="Year of procedure 10"                                                  
                                                                                
  PRYEAR11                   LENGTH=3                                           
  LABEL="Year of procedure 11"                                                  
                                                                                
  PRYEAR12                   LENGTH=3                                           
  LABEL="Year of procedure 12"                                                  
                                                                                
  PRYEAR13                   LENGTH=3                                           
  LABEL="Year of procedure 13"                                                  
                                                                                
  PRYEAR14                   LENGTH=3                                           
  LABEL="Year of procedure 14"                                                  
                                                                                
  PRYEAR15                   LENGTH=3                                           
  LABEL="Year of procedure 15"                                                  
                                                                                
  PRYEAR16                   LENGTH=3                                           
  LABEL="Year of procedure 16"                                                  
                                                                                
  PRYEAR17                   LENGTH=3                                           
  LABEL="Year of procedure 17"                                                  
                                                                                
  PRYEAR18                   LENGTH=3                                           
  LABEL="Year of procedure 18"                                                  
                                                                                
  PRYEAR19                   LENGTH=3                                           
  LABEL="Year of procedure 19"                                                  
                                                                                
  PRYEAR20                   LENGTH=3                                           
  LABEL="Year of procedure 20"                                                  
                                                                                
  PRYEAR21                   LENGTH=3                                           
  LABEL="Year of procedure 21"                                                  
                                                                                
  PRYEAR22                   LENGTH=3                                           
  LABEL="Year of procedure 22"                                                  
                                                                                
  PRYEAR23                   LENGTH=3                                           
  LABEL="Year of procedure 23"                                                  
                                                                                
  PRYEAR24                   LENGTH=3                                           
  LABEL="Year of procedure 24"                                                  
                                                                                
  PRYEAR25                   LENGTH=3                                           
  LABEL="Year of procedure 25"                                                  
  ;                                                                             
                                                                                
                                                                                
*** Input the variables from the ASCII file ***;                                
INPUT                                                                           
      @1      AGE                      N3PF.                                    
      @4      AGEDAY                   N3PF.                                    
      @7      AGEMONTH                 N3PF.                                    
      @10     AMONTH                   N2PF.                                    
      @12     ASOURCE                  N2PF.                                    
      @14     ASOURCEUB92              $CHAR1.                                  
      @15     ASOURCE_X                $CHAR2.                                  
      @17     ATYPE                    N2PF.                                    
      @19     AWEEKEND                 N2PF.                                    
      @21     BILLTYPE                 $CHAR4.                                  
      @25     CPT1                     $CHAR5.                                  
      @30     CPT2                     $CHAR5.                                  
      @35     CPT3                     $CHAR5.                                  
      @40     CPT4                     $CHAR5.                                  
      @45     CPT5                     $CHAR5.                                  
      @50     CPT6                     $CHAR5.                                  
      @55     CPT7                     $CHAR5.                                  
      @60     CPT8                     $CHAR5.                                  
      @65     CPT9                     $CHAR5.                                  
      @70     CPT10                    $CHAR5.                                  
      @75     CPT11                    $CHAR5.                                  
      @80     CPT12                    $CHAR5.                                  
      @85     CPT13                    $CHAR5.                                  
      @90     CPT14                    $CHAR5.                                  
      @95     CPT15                    $CHAR5.                                  
      @100    CPT16                    $CHAR5.                                  
      @105    CPT17                    $CHAR5.                                  
      @110    CPT18                    $CHAR5.                                  
      @115    CPT19                    $CHAR5.                                  
      @120    CPT20                    $CHAR5.                                  
      @125    CPT21                    $CHAR5.                                  
      @130    CPT22                    $CHAR5.                                  
      @135    CPT23                    $CHAR5.                                  
      @140    CPT24                    $CHAR5.                                  
      @145    CPT25                    $CHAR5.                                  
      @150    CPTCCS1                  N3PF.                                    
      @153    CPTCCS2                  N3PF.                                    
      @156    CPTCCS3                  N3PF.                                    
      @159    CPTCCS4                  N3PF.                                    
      @162    CPTCCS5                  N3PF.                                    
      @165    CPTCCS6                  N3PF.                                    
      @168    CPTCCS7                  N3PF.                                    
      @171    CPTCCS8                  N3PF.                                    
      @174    CPTCCS9                  N3PF.                                    
      @177    CPTCCS10                 N3PF.                                    
      @180    CPTCCS11                 N3PF.                                    
      @183    CPTCCS12                 N3PF.                                    
      @186    CPTCCS13                 N3PF.                                    
      @189    CPTCCS14                 N3PF.                                    
      @192    CPTCCS15                 N3PF.                                    
      @195    CPTCCS16                 N3PF.                                    
      @198    CPTCCS17                 N3PF.                                    
      @201    CPTCCS18                 N3PF.                                    
      @204    CPTCCS19                 N3PF.                                    
      @207    CPTCCS20                 N3PF.                                    
      @210    CPTCCS21                 N3PF.                                    
      @213    CPTCCS22                 N3PF.                                    
      @216    CPTCCS23                 N3PF.                                    
      @219    CPTCCS24                 N3PF.                                    
      @222    CPTCCS25                 N3PF.                                    
      @225    CPTDAY1                  N3PF.                                    
      @228    CPTDAY2                  N3PF.                                    
      @231    CPTDAY3                  N3PF.                                    
      @234    CPTDAY4                  N3PF.                                    
      @237    CPTDAY5                  N3PF.                                    
      @240    CPTDAY6                  N3PF.                                    
      @243    CPTDAY7                  N3PF.                                    
      @246    CPTDAY8                  N3PF.                                    
      @249    CPTDAY9                  N3PF.                                    
      @252    CPTDAY10                 N3PF.                                    
      @255    CPTDAY11                 N3PF.                                    
      @258    CPTDAY12                 N3PF.                                    
      @261    CPTDAY13                 N3PF.                                    
      @264    CPTDAY14                 N3PF.                                    
      @267    CPTDAY15                 N3PF.                                    
      @270    CPTDAY16                 N3PF.                                    
      @273    CPTDAY17                 N3PF.                                    
      @276    CPTDAY18                 N3PF.                                    
      @279    CPTDAY19                 N3PF.                                    
      @282    CPTDAY20                 N3PF.                                    
      @285    CPTDAY21                 N3PF.                                    
      @288    CPTDAY22                 N3PF.                                    
      @291    CPTDAY23                 N3PF.                                    
      @294    CPTDAY24                 N3PF.                                    
      @297    CPTDAY25                 N3PF.                                    
      @300    CPTM1_1                  $CHAR2.                                  
      @302    CPTM1_2                  $CHAR2.                                  
      @304    CPTM1_3                  $CHAR2.                                  
      @306    CPTM1_4                  $CHAR2.                                  
      @308    CPTM1_5                  $CHAR2.                                  
      @310    CPTM1_6                  $CHAR2.                                  
      @312    CPTM1_7                  $CHAR2.                                  
      @314    CPTM1_8                  $CHAR2.                                  
      @316    CPTM1_9                  $CHAR2.                                  
      @318    CPTM1_10                 $CHAR2.                                  
      @320    CPTM1_11                 $CHAR2.                                  
      @322    CPTM1_12                 $CHAR2.                                  
      @324    CPTM1_13                 $CHAR2.                                  
      @326    CPTM1_14                 $CHAR2.                                  
      @328    CPTM1_15                 $CHAR2.                                  
      @330    CPTM1_16                 $CHAR2.                                  
      @332    CPTM1_17                 $CHAR2.                                  
      @334    CPTM1_18                 $CHAR2.                                  
      @336    CPTM1_19                 $CHAR2.                                  
      @338    CPTM1_20                 $CHAR2.                                  
      @340    CPTM1_21                 $CHAR2.                                  
      @342    CPTM1_22                 $CHAR2.                                  
      @344    CPTM1_23                 $CHAR2.                                  
      @346    CPTM1_24                 $CHAR2.                                  
      @348    CPTM1_25                 $CHAR2.                                  
      @350    CPTM2_1                  $CHAR2.                                  
      @352    CPTM2_2                  $CHAR2.                                  
      @354    CPTM2_3                  $CHAR2.                                  
      @356    CPTM2_4                  $CHAR2.                                  
      @358    CPTM2_5                  $CHAR2.                                  
      @360    CPTM2_6                  $CHAR2.                                  
      @362    CPTM2_7                  $CHAR2.                                  
      @364    CPTM2_8                  $CHAR2.                                  
      @366    CPTM2_9                  $CHAR2.                                  
      @368    CPTM2_10                 $CHAR2.                                  
      @370    CPTM2_11                 $CHAR2.                                  
      @372    CPTM2_12                 $CHAR2.                                  
      @374    CPTM2_13                 $CHAR2.                                  
      @376    CPTM2_14                 $CHAR2.                                  
      @378    CPTM2_15                 $CHAR2.                                  
      @380    CPTM2_16                 $CHAR2.                                  
      @382    CPTM2_17                 $CHAR2.                                  
      @384    CPTM2_18                 $CHAR2.                                  
      @386    CPTM2_19                 $CHAR2.                                  
      @388    CPTM2_20                 $CHAR2.                                  
      @390    CPTM2_21                 $CHAR2.                                  
      @392    CPTM2_22                 $CHAR2.                                  
      @394    CPTM2_23                 $CHAR2.                                  
      @396    CPTM2_24                 $CHAR2.                                  
      @398    CPTM2_25                 $CHAR2.                                  
      @400    DIED                     N2PF.                                    
      @402    DISPUB04                 N2PF.                                    
      @404    DISPUNIFORM              N2PF.                                    
      @406    DISP_X                   $CHAR2.                                  
      @408    DQTR                     N2PF.                                    
      @410    DSHOSPID                 $CHAR13.                                 
      @423    DX1                      $CHAR5.                                  
      @428    DX2                      $CHAR5.                                  
      @433    DX3                      $CHAR5.                                  
      @438    DX4                      $CHAR5.                                  
      @443    DX5                      $CHAR5.                                  
      @448    DX6                      $CHAR5.                                  
      @453    DX7                      $CHAR5.                                  
      @458    DX8                      $CHAR5.                                  
      @463    DX9                      $CHAR5.                                  
      @468    DX10                     $CHAR5.                                  
      @473    DX11                     $CHAR5.                                  
      @478    DX12                     $CHAR5.                                  
      @483    DX13                     $CHAR5.                                  
      @488    DX14                     $CHAR5.                                  
      @493    DX15                     $CHAR5.                                  
      @498    DX16                     $CHAR5.                                  
      @503    DX17                     $CHAR5.                                  
      @508    DX18                     $CHAR5.                                  
      @513    DX19                     $CHAR5.                                  
      @518    DX20                     $CHAR5.                                  
      @523    DX21                     $CHAR5.                                  
      @528    DX22                     $CHAR5.                                  
      @533    DX23                     $CHAR5.                                  
      @538    DX24                     $CHAR5.                                  
      @543    DX25                     $CHAR5.                                  
      @548    DXCCS1                   N4PF.                                    
      @552    DXCCS2                   N4PF.                                    
      @556    DXCCS3                   N4PF.                                    
      @560    DXCCS4                   N4PF.                                    
      @564    DXCCS5                   N4PF.                                    
      @568    DXCCS6                   N4PF.                                    
      @572    DXCCS7                   N4PF.                                    
      @576    DXCCS8                   N4PF.                                    
      @580    DXCCS9                   N4PF.                                    
      @584    DXCCS10                  N4PF.                                    
      @588    DXCCS11                  N4PF.                                    
      @592    DXCCS12                  N4PF.                                    
      @596    DXCCS13                  N4PF.                                    
      @600    DXCCS14                  N4PF.                                    
      @604    DXCCS15                  N4PF.                                    
      @608    DXCCS16                  N4PF.                                    
      @612    DXCCS17                  N4PF.                                    
      @616    DXCCS18                  N4PF.                                    
      @620    DXCCS19                  N4PF.                                    
      @624    DXCCS20                  N4PF.                                    
      @628    DXCCS21                  N4PF.                                    
      @632    DXCCS22                  N4PF.                                    
      @636    DXCCS23                  N4PF.                                    
      @640    DXCCS24                  N4PF.                                    
      @644    DXCCS25                  N4PF.                                    
      @648    DX_Visit_Reason1         $CHAR5.                                  
      @653    DX_Visit_Reason2         $CHAR5.                                  
      @658    DX_Visit_Reason3         $CHAR5.                                  
      @663    ECODE1                   $CHAR5.                                  
      @668    ECODE2                   $CHAR5.                                  
      @673    ECODE3                   $CHAR5.                                  
      @678    ECODE4                   $CHAR5.                                  
      @683    ECODE5                   $CHAR5.                                  
      @688    ECODE6                   $CHAR5.                                  
      @693    ECODE7                   $CHAR5.                                  
      @698    ECODE8                   $CHAR5.                                  
      @703    E_CCS1                   N4PF.                                    
      @707    E_CCS2                   N4PF.                                    
      @711    E_CCS3                   N4PF.                                    
      @715    E_CCS4                   N4PF.                                    
      @719    E_CCS5                   N4PF.                                    
      @723    E_CCS6                   N4PF.                                    
      @727    E_CCS7                   N4PF.                                    
      @731    E_CCS8                   N4PF.                                    
      @735    FEMALE                   N2PF.                                    
      @737    HCUP_AS                  N2PF.                                    
      @739    HCUP_ED                  N2PF.                                    
      @741    HCUP_OS                  N2PF.                                    
      @743    HISPANIC_X               $CHAR2.                                  
      @745    HOSPBRTH                 N3PF.                                    
      @748    HOSPST                   $CHAR2.                                  
      @750    KEY                      14.                                      
      @764    LOS                      N5PF.                                    
      @769    LOS_X                    N6PF.                                    
      @775    MDNUM1_R                 N9PF.                                    
      @784    MDNUM2_R                 N9PF.                                    
      @793    MEDINCSTQ                N2PF.                                    
      @795    NCPT                     N3PF.                                    
      @798    NDX                      N2PF.                                    
      @800    NECODE                   N2PF.                                    
      @802    NEOMAT                   N2PF.                                    
      @804    NPR                      N2PF.                                    
      @806    OPservice                $CHAR2.                                  
      @808    PAY1                     N2PF.                                    
      @810    PAY1_X                   $CHAR4.                                  
      @814    PAY2                     N2PF.                                    
      @816    PAY2_X                   $CHAR4.                                  
      @820    PAY3_X                   $CHAR4.                                  
      @824    PL_CBSA                  N3PF.                                    
      @827    PL_MSA1993               N3PF.                                    
      @830    PL_NCHS2006              N2PF.                                    
      @832    PL_RUCA10_2005           N2PF.                                    
      @834    PL_RUCA2005              N4P1F.                                   
      @838    PL_RUCA4_2005            N2PF.                                    
      @840    PL_RUCC2003              N2PF.                                    
      @842    PL_UIC2003               N2PF.                                    
      @844    PL_UR_CAT4               N2PF.                                    
      @846    PR1                      $CHAR4.                                  
      @850    PR2                      $CHAR4.                                  
      @854    PR3                      $CHAR4.                                  
      @858    PR4                      $CHAR4.                                  
      @862    PR5                      $CHAR4.                                  
      @866    PR6                      $CHAR4.                                  
      @870    PR7                      $CHAR4.                                  
      @874    PR8                      $CHAR4.                                  
      @878    PR9                      $CHAR4.                                  
      @882    PR10                     $CHAR4.                                  
      @886    PR11                     $CHAR4.                                  
      @890    PR12                     $CHAR4.                                  
      @894    PR13                     $CHAR4.                                  
      @898    PR14                     $CHAR4.                                  
      @902    PR15                     $CHAR4.                                  
      @906    PR16                     $CHAR4.                                  
      @910    PR17                     $CHAR4.                                  
      @914    PR18                     $CHAR4.                                  
      @918    PR19                     $CHAR4.                                  
      @922    PR20                     $CHAR4.                                  
      @926    PR21                     $CHAR4.                                  
      @930    PR22                     $CHAR4.                                  
      @934    PR23                     $CHAR4.                                  
      @938    PR24                     $CHAR4.                                  
      @942    PR25                     $CHAR4.                                  
      @946    PRCCS1                   N3PF.                                    
      @949    PRCCS2                   N3PF.                                    
      @952    PRCCS3                   N3PF.                                    
      @955    PRCCS4                   N3PF.                                    
      @958    PRCCS5                   N3PF.                                    
      @961    PRCCS6                   N3PF.                                    
      @964    PRCCS7                   N3PF.                                    
      @967    PRCCS8                   N3PF.                                    
      @970    PRCCS9                   N3PF.                                    
      @973    PRCCS10                  N3PF.                                    
      @976    PRCCS11                  N3PF.                                    
      @979    PRCCS12                  N3PF.                                    
      @982    PRCCS13                  N3PF.                                    
      @985    PRCCS14                  N3PF.                                    
      @988    PRCCS15                  N3PF.                                    
      @991    PRCCS16                  N3PF.                                    
      @994    PRCCS17                  N3PF.                                    
      @997    PRCCS18                  N3PF.                                    
      @1000   PRCCS19                  N3PF.                                    
      @1003   PRCCS20                  N3PF.                                    
      @1006   PRCCS21                  N3PF.                                    
      @1009   PRCCS22                  N3PF.                                    
      @1012   PRCCS23                  N3PF.                                    
      @1015   PRCCS24                  N3PF.                                    
      @1018   PRCCS25                  N3PF.                                    
      @1021   PRDAY1                   N5PF.                                    
      @1026   PRDAY2                   N5PF.                                    
      @1031   PRDAY3                   N5PF.                                    
      @1036   PRDAY4                   N5PF.                                    
      @1041   PRDAY5                   N5PF.                                    
      @1046   PRDAY6                   N5PF.                                    
      @1051   PRDAY7                   N5PF.                                    
      @1056   PRDAY8                   N5PF.                                    
      @1061   PRDAY9                   N5PF.                                    
      @1066   PRDAY10                  N5PF.                                    
      @1071   PRDAY11                  N5PF.                                    
      @1076   PRDAY12                  N5PF.                                    
      @1081   PRDAY13                  N5PF.                                    
      @1086   PRDAY14                  N5PF.                                    
      @1091   PRDAY15                  N5PF.                                    
      @1096   PRDAY16                  N5PF.                                    
      @1101   PRDAY17                  N5PF.                                    
      @1106   PRDAY18                  N5PF.                                    
      @1111   PRDAY19                  N5PF.                                    
      @1116   PRDAY20                  N5PF.                                    
      @1121   PRDAY21                  N5PF.                                    
      @1126   PRDAY22                  N5PF.                                    
      @1131   PRDAY23                  N5PF.                                    
      @1136   PRDAY24                  N5PF.                                    
      @1141   PRDAY25                  N5PF.                                    
      @1146   PROCTYPE                 N3PF.                                    
      @1149   PSTATE                   $CHAR2.                                  
      @1151   PSTCO                    N5PF.                                    
      @1156   PSTCO2                   N5PF.                                    
      @1161   PointOfOriginUB04        $CHAR1.                                  
      @1162   PointOfOrigin_X          $CHAR2.                                  
      @1164   RACE                     N2PF.                                    
      @1166   RACE_X                   $CHAR2.                                  
      @1168   STATE_AS                 N2PF.                                    
      @1170   STATE_ED                 N2PF.                                    
      @1172   STATE_OS                 N2PF.                                    
      @1174   TOTCHG                   N10PF.                                   
      @1184   TOTCHG_X                 N15P2F.                                  
      @1199   YEAR                     N4PF.                                    
      @1203   ZIPINC_QRTL              N3PF.                                    
      @1206   ZIP                      $CHAR5.                                  
      @1211   AYEAR                    N4PF.                                    
      @1215   DMONTH                   N2PF.                                    
      @1217   BMONTH                   N2PF.                                    
      @1219   BYEAR                    N4PF.                                    
      @1223   PRMONTH1                 N2PF.                                    
      @1225   PRMONTH2                 N2PF.                                    
      @1227   PRMONTH3                 N2PF.                                    
      @1229   PRMONTH4                 N2PF.                                    
      @1231   PRMONTH5                 N2PF.                                    
      @1233   PRMONTH6                 N2PF.                                    
      @1235   PRMONTH7                 N2PF.                                    
      @1237   PRMONTH8                 N2PF.                                    
      @1239   PRMONTH9                 N2PF.                                    
      @1241   PRMONTH10                N2PF.                                    
      @1243   PRMONTH11                N2PF.                                    
      @1245   PRMONTH12                N2PF.                                    
      @1247   PRMONTH13                N2PF.                                    
      @1249   PRMONTH14                N2PF.                                    
      @1251   PRMONTH15                N2PF.                                    
      @1253   PRMONTH16                N2PF.                                    
      @1255   PRMONTH17                N2PF.                                    
      @1257   PRMONTH18                N2PF.                                    
      @1259   PRMONTH19                N2PF.                                    
      @1261   PRMONTH20                N2PF.                                    
      @1263   PRMONTH21                N2PF.                                    
      @1265   PRMONTH22                N2PF.                                    
      @1267   PRMONTH23                N2PF.                                    
      @1269   PRMONTH24                N2PF.                                    
      @1271   PRMONTH25                N2PF.                                    
      @1273   PRYEAR1                  N4PF.                                    
      @1277   PRYEAR2                  N4PF.                                    
      @1281   PRYEAR3                  N4PF.                                    
      @1285   PRYEAR4                  N4PF.                                    
      @1289   PRYEAR5                  N4PF.                                    
      @1293   PRYEAR6                  N4PF.                                    
      @1297   PRYEAR7                  N4PF.                                    
      @1301   PRYEAR8                  N4PF.                                    
      @1305   PRYEAR9                  N4PF.                                    
      @1309   PRYEAR10                 N4PF.                                    
      @1313   PRYEAR11                 N4PF.                                    
      @1317   PRYEAR12                 N4PF.                                    
      @1321   PRYEAR13                 N4PF.                                    
      @1325   PRYEAR14                 N4PF.                                    
      @1329   PRYEAR15                 N4PF.                                    
      @1333   PRYEAR16                 N4PF.                                    
      @1337   PRYEAR17                 N4PF.                                    
      @1341   PRYEAR18                 N4PF.                                    
      @1345   PRYEAR19                 N4PF.                                    
      @1349   PRYEAR20                 N4PF.                                    
      @1353   PRYEAR21                 N4PF.                                    
      @1357   PRYEAR22                 N4PF.                                    
      @1361   PRYEAR23                 N4PF.                                    
      @1365   PRYEAR24                 N4PF.                                    
      @1369   PRYEAR25                 N4PF.                                    
      ;                                                                         
                                                                                
                                                                                
RUN;
