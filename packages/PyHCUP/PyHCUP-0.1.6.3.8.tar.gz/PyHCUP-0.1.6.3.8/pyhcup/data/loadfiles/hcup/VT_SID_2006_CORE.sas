/*******************************************************************            
*   VT_SID_2006_CORE.SAS:                                                       
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
DATA VT_SIDC_2006_CORE;                                                         
INFILE 'VT_SID_2006_CORE.ASC' LRECL = 1134;                                     
                                                                                
*** Variable attribute ***;                                                     
ATTRIB                                                                          
  KEY                        LENGTH=8                 FORMAT=Z14.               
  LABEL="HCUP record identifier"                                                
                                                                                
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
                                                                                
  ASOURCE_X                  LENGTH=$8                                          
  LABEL="Admission source (as received from source)"                            
                                                                                
  ASOURCEUB92                LENGTH=$1                                          
  LABEL="Admission source (UB-92 standard coding)"                              
                                                                                
  ATYPE                      LENGTH=3                                           
  LABEL="Admission type"                                                        
                                                                                
  AWEEKEND                   LENGTH=3                                           
  LABEL="Admission day is a weekend"                                            
                                                                                
  BWT                        LENGTH=4                                           
  LABEL="Birth weight in grams"                                                 
                                                                                
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
                                                                                
  DIED                       LENGTH=3                                           
  LABEL="Died during hospitalization"                                           
                                                                                
  DISP_X                     LENGTH=$2                                          
  LABEL="Disposition of patient (as received from source)"                      
                                                                                
  DISPUB92                   LENGTH=3                                           
  LABEL="Disposition of patient (UB-92 standard coding)"                        
                                                                                
  DISPUNIFORM                LENGTH=3                                           
  LABEL="Disposition of patient (uniform)"                                      
                                                                                
  DQTR                       LENGTH=3                                           
  LABEL="Discharge quarter"                                                     
                                                                                
  DRG                        LENGTH=3                                           
  LABEL="DRG in effect on discharge date"                                       
                                                                                
  DRG18                      LENGTH=3                                           
  LABEL="DRG, version 18"                                                       
                                                                                
  DRG24                      LENGTH=3                                           
  LABEL="DRG, version 24"                                                       
                                                                                
  DRGVER                     LENGTH=3                                           
  LABEL="DRG grouper version used on discharge date"                            
                                                                                
  DSHOSPID                   LENGTH=$13                                         
  LABEL="Data source hospital identifier"                                       
                                                                                
  DX1                        LENGTH=$5                                          
  LABEL="Principal diagnosis"                                                   
                                                                                
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
                                                                                
  DXCCS1                     LENGTH=4                                           
  LABEL="CCS: principal diagnosis"                                              
                                                                                
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
                                                                                
  FEMALE                     LENGTH=3                                           
  LABEL="Indicator of sex"                                                      
                                                                                
  HCUP_ED                    LENGTH=3                                           
  LABEL="HCUP Emergency Department service indicator"                           
                                                                                
  HCUP_OS                    LENGTH=3                                           
  LABEL="HCUP Observation Stay service indicator"                               
                                                                                
  HOSPBRTH                   LENGTH=3                                           
  LABEL="Indicator of birth in this hospital"                                   
                                                                                
  HOSPST                     LENGTH=$2                                          
  LABEL="Hospital state postal code"                                            
                                                                                
  LOS                        LENGTH=4                                           
  LABEL="Length of stay (cleaned)"                                              
                                                                                
  LOS_X                      LENGTH=4                                           
  LABEL="Length of stay (as received from source)"                              
                                                                                
  MDC                        LENGTH=3                                           
  LABEL="MDC in effect on discharge date"                                       
                                                                                
  MDC18                      LENGTH=3                                           
  LABEL="MDC, version 18"                                                       
                                                                                
  MDC24                      LENGTH=3                                           
  LABEL="MDC, version 24"                                                       
                                                                                
  MEDINCSTQ                  LENGTH=3                                           
  LABEL="Median household income state quartile for patient ZIP Code"           
                                                                                
  MRN_R                      LENGTH=5                                           
  LABEL="Medical record number (re-identified)"                                 
                                                                                
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
                                                                                
  PAY1                       LENGTH=3                                           
  LABEL="Primary expected payer (uniform)"                                      
                                                                                
  PAY2                       LENGTH=3                                           
  LABEL="Secondary expected payer (uniform)"                                    
                                                                                
  PAY1_X                     LENGTH=$8                                          
  LABEL="Primary expected payer (as received from source)"                      
                                                                                
  PAY2_X                     LENGTH=$8                                          
  LABEL="Secondary expected payer (as received from source)"                    
                                                                                
  PAY3_X                     LENGTH=$8                                          
  LABEL="Tertiary expected payer (as received from source)"                     
                                                                                
  PAYER1_X                   LENGTH=$16                                         
  LABEL="Primary expected payer plan identifier (as received from source)"      
                                                                                
  PAYER2_X                   LENGTH=$16                                         
  LABEL="Secondary expected payer plan identifier (as received from source)"    
                                                                                
  PL_CBSA                    LENGTH=3                                           
  LABEL="Patient location: Core Based Statistical Area (CBSA)"                  
                                                                                
  PL_MSA1993                 LENGTH=3                                           
  LABEL="Patient location: Metropolitan Statistical Area (MSA), 1993"           
                                                                                
  PL_NHCS2006                LENGTH=3                                           
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
                                                                                
  PL_UR_CAT5                 LENGTH=3                                           
  LABEL="Patient Location: Urban-Rural 5 Categories"                            
                                                                                
  PR1                        LENGTH=$4                                          
  LABEL="Principal procedure"                                                   
                                                                                
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
                                                                                
  PRCCS1                     LENGTH=3                                           
  LABEL="CCS: principal procedure"                                              
                                                                                
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
                                                                                
  PROCTYPE                   LENGTH=3                                           
  LABEL="Procedure type indicator"                                              
                                                                                
  PSTATE                     LENGTH=$2                                          
  LABEL="Patient State postal code"                                             
                                                                                
  PSTCO                      LENGTH=4                 FORMAT=Z5.                
  LABEL="Patient state/county FIPS code"                                        
                                                                                
  PSTCO2                     LENGTH=4                 FORMAT=Z5.                
  LABEL="Patient state/county FIPS code, possibly derived from ZIP Code"        
                                                                                
  RACE                       LENGTH=3                                           
  LABEL="Race (uniform)"                                                        
                                                                                
  RACE_X                     LENGTH=$8                                          
  LABEL="Race (as received from source)"                                        
                                                                                
  READMIT                    LENGTH=3                                           
  LABEL="Readmission"                                                           
                                                                                
  TOTCHG                     LENGTH=6                                           
  LABEL="Total charges (cleaned)"                                               
                                                                                
  TOTCHG_X                   LENGTH=7                                           
  LABEL="Total charges (as received from source)"                               
                                                                                
  YEAR                       LENGTH=3                                           
  LABEL="Calendar year"                                                         
                                                                                
  ZIP3                       LENGTH=$3                                          
  LABEL="Patient ZIP Code, first 3 digits"                                      
                                                                                
  ZIPINC_QRTL                LENGTH=3                                           
  LABEL="Median household income national quartile for patient ZIP Code"        
                                                                                
  TOWN                       LENGTH=$8                                          
  LABEL="Patient town of residence (as received from source)"                   
                                                                                
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
  ;                                                                             
                                                                                
                                                                                
*** Input the variables from the ASCII file ***;                                
INPUT                                                                           
      @1      KEY                      14.                                      
      @15     AGE                      N3PF.                                    
      @18     AGEDAY                   N3PF.                                    
      @21     AGEMONTH                 N3PF.                                    
      @24     AMONTH                   N2PF.                                    
      @26     ASOURCE                  N2PF.                                    
      @28     ASOURCE_X                $CHAR8.                                  
      @36     ASOURCEUB92              $CHAR1.                                  
      @37     ATYPE                    N2PF.                                    
      @39     AWEEKEND                 N2PF.                                    
      @41     BWT                      N4PF.                                    
      @45     CPT1                     $CHAR5.                                  
      @50     CPT2                     $CHAR5.                                  
      @55     CPT3                     $CHAR5.                                  
      @60     CPT4                     $CHAR5.                                  
      @65     CPT5                     $CHAR5.                                  
      @70     CPT6                     $CHAR5.                                  
      @75     CPT7                     $CHAR5.                                  
      @80     CPT8                     $CHAR5.                                  
      @85     CPT9                     $CHAR5.                                  
      @90     CPT10                    $CHAR5.                                  
      @95     CPT11                    $CHAR5.                                  
      @100    CPT12                    $CHAR5.                                  
      @105    CPT13                    $CHAR5.                                  
      @110    CPT14                    $CHAR5.                                  
      @115    CPT15                    $CHAR5.                                  
      @120    CPT16                    $CHAR5.                                  
      @125    CPT17                    $CHAR5.                                  
      @130    CPT18                    $CHAR5.                                  
      @135    CPT19                    $CHAR5.                                  
      @140    CPT20                    $CHAR5.                                  
      @145    CPT21                    $CHAR5.                                  
      @150    CPT22                    $CHAR5.                                  
      @155    CPT23                    $CHAR5.                                  
      @160    CPT24                    $CHAR5.                                  
      @165    CPT25                    $CHAR5.                                  
      @170    CPTDAY1                  N3PF.                                    
      @173    CPTDAY2                  N3PF.                                    
      @176    CPTDAY3                  N3PF.                                    
      @179    CPTDAY4                  N3PF.                                    
      @182    CPTDAY5                  N3PF.                                    
      @185    CPTDAY6                  N3PF.                                    
      @188    CPTDAY7                  N3PF.                                    
      @191    CPTDAY8                  N3PF.                                    
      @194    CPTDAY9                  N3PF.                                    
      @197    CPTDAY10                 N3PF.                                    
      @200    CPTDAY11                 N3PF.                                    
      @203    CPTDAY12                 N3PF.                                    
      @206    CPTDAY13                 N3PF.                                    
      @209    CPTDAY14                 N3PF.                                    
      @212    CPTDAY15                 N3PF.                                    
      @215    CPTDAY16                 N3PF.                                    
      @218    CPTDAY17                 N3PF.                                    
      @221    CPTDAY18                 N3PF.                                    
      @224    CPTDAY19                 N3PF.                                    
      @227    CPTDAY20                 N3PF.                                    
      @230    CPTDAY21                 N3PF.                                    
      @233    CPTDAY22                 N3PF.                                    
      @236    CPTDAY23                 N3PF.                                    
      @239    CPTDAY24                 N3PF.                                    
      @242    CPTDAY25                 N3PF.                                    
      @245    CPTM1_1                  $CHAR2.                                  
      @247    CPTM1_2                  $CHAR2.                                  
      @249    CPTM1_3                  $CHAR2.                                  
      @251    CPTM1_4                  $CHAR2.                                  
      @253    CPTM1_5                  $CHAR2.                                  
      @255    CPTM1_6                  $CHAR2.                                  
      @257    CPTM1_7                  $CHAR2.                                  
      @259    CPTM1_8                  $CHAR2.                                  
      @261    CPTM1_9                  $CHAR2.                                  
      @263    CPTM1_10                 $CHAR2.                                  
      @265    CPTM1_11                 $CHAR2.                                  
      @267    CPTM1_12                 $CHAR2.                                  
      @269    CPTM1_13                 $CHAR2.                                  
      @271    CPTM1_14                 $CHAR2.                                  
      @273    CPTM1_15                 $CHAR2.                                  
      @275    CPTM1_16                 $CHAR2.                                  
      @277    CPTM1_17                 $CHAR2.                                  
      @279    CPTM1_18                 $CHAR2.                                  
      @281    CPTM1_19                 $CHAR2.                                  
      @283    CPTM1_20                 $CHAR2.                                  
      @285    CPTM1_21                 $CHAR2.                                  
      @287    CPTM1_22                 $CHAR2.                                  
      @289    CPTM1_23                 $CHAR2.                                  
      @291    CPTM1_24                 $CHAR2.                                  
      @293    CPTM1_25                 $CHAR2.                                  
      @295    DIED                     N2PF.                                    
      @297    DISP_X                   $CHAR2.                                  
      @299    DISPUB92                 N2PF.                                    
      @301    DISPUNIFORM              N2PF.                                    
      @303    DQTR                     N2PF.                                    
      @305    DRG                      N3PF.                                    
      @308    DRG18                    N3PF.                                    
      @311    DRG24                    N3PF.                                    
      @314    DRGVER                   N2PF.                                    
      @316    DSHOSPID                 $CHAR13.                                 
      @329    DX1                      $CHAR5.                                  
      @334    DX2                      $CHAR5.                                  
      @339    DX3                      $CHAR5.                                  
      @344    DX4                      $CHAR5.                                  
      @349    DX5                      $CHAR5.                                  
      @354    DX6                      $CHAR5.                                  
      @359    DX7                      $CHAR5.                                  
      @364    DX8                      $CHAR5.                                  
      @369    DX9                      $CHAR5.                                  
      @374    DX10                     $CHAR5.                                  
      @379    DX11                     $CHAR5.                                  
      @384    DX12                     $CHAR5.                                  
      @389    DX13                     $CHAR5.                                  
      @394    DX14                     $CHAR5.                                  
      @399    DX15                     $CHAR5.                                  
      @404    DX16                     $CHAR5.                                  
      @409    DX17                     $CHAR5.                                  
      @414    DX18                     $CHAR5.                                  
      @419    DX19                     $CHAR5.                                  
      @424    DX20                     $CHAR5.                                  
      @429    DXCCS1                   N4PF.                                    
      @433    DXCCS2                   N4PF.                                    
      @437    DXCCS3                   N4PF.                                    
      @441    DXCCS4                   N4PF.                                    
      @445    DXCCS5                   N4PF.                                    
      @449    DXCCS6                   N4PF.                                    
      @453    DXCCS7                   N4PF.                                    
      @457    DXCCS8                   N4PF.                                    
      @461    DXCCS9                   N4PF.                                    
      @465    DXCCS10                  N4PF.                                    
      @469    DXCCS11                  N4PF.                                    
      @473    DXCCS12                  N4PF.                                    
      @477    DXCCS13                  N4PF.                                    
      @481    DXCCS14                  N4PF.                                    
      @485    DXCCS15                  N4PF.                                    
      @489    DXCCS16                  N4PF.                                    
      @493    DXCCS17                  N4PF.                                    
      @497    DXCCS18                  N4PF.                                    
      @501    DXCCS19                  N4PF.                                    
      @505    DXCCS20                  N4PF.                                    
      @509    ECODE1                   $CHAR5.                                  
      @514    ECODE2                   $CHAR5.                                  
      @519    ECODE3                   $CHAR5.                                  
      @524    ECODE4                   $CHAR5.                                  
      @529    ECODE5                   $CHAR5.                                  
      @534    E_CCS1                   N4PF.                                    
      @538    E_CCS2                   N4PF.                                    
      @542    E_CCS3                   N4PF.                                    
      @546    E_CCS4                   N4PF.                                    
      @550    E_CCS5                   N4PF.                                    
      @554    FEMALE                   N2PF.                                    
      @556    HCUP_ED                  N2PF.                                    
      @558    HCUP_OS                  N2PF.                                    
      @560    HOSPBRTH                 N3PF.                                    
      @563    HOSPST                   $CHAR2.                                  
      @565    LOS                      N5PF.                                    
      @570    LOS_X                    N6PF.                                    
      @576    MDC                      N2PF.                                    
      @578    MDC18                    N2PF.                                    
      @580    MDC24                    N2PF.                                    
      @582    MEDINCSTQ                N2PF.                                    
      @584    MRN_R                    N9PF.                                    
      @593    NCPT                     N3PF.                                    
      @596    NDX                      N2PF.                                    
      @598    NECODE                   N2PF.                                    
      @600    NEOMAT                   N2PF.                                    
      @602    NPR                      N2PF.                                    
      @604    PAY1                     N2PF.                                    
      @606    PAY2                     N2PF.                                    
      @608    PAY1_X                   $CHAR8.                                  
      @616    PAY2_X                   $CHAR8.                                  
      @624    PAY3_X                   $CHAR8.                                  
      @632    PAYER1_X                 $CHAR16.                                 
      @648    PAYER2_X                 $CHAR16.                                 
      @664    PL_CBSA                  N3PF.                                    
      @667    PL_MSA1993               N3PF.                                    
      @670    PL_NHCS2006              N2PF.                                    
      @672    PL_RUCA10_2005           N2PF.                                    
      @674    PL_RUCA2005              N4P1F.                                   
      @678    PL_RUCA4_2005            N2PF.                                    
      @680    PL_RUCC2003              N2PF.                                    
      @682    PL_UIC2003               N2PF.                                    
      @684    PL_UR_CAT4               N2PF.                                    
      @686    PL_UR_CAT5               N2PF.                                    
      @688    PR1                      $CHAR4.                                  
      @692    PR2                      $CHAR4.                                  
      @696    PR3                      $CHAR4.                                  
      @700    PR4                      $CHAR4.                                  
      @704    PR5                      $CHAR4.                                  
      @708    PR6                      $CHAR4.                                  
      @712    PR7                      $CHAR4.                                  
      @716    PR8                      $CHAR4.                                  
      @720    PR9                      $CHAR4.                                  
      @724    PR10                     $CHAR4.                                  
      @728    PR11                     $CHAR4.                                  
      @732    PR12                     $CHAR4.                                  
      @736    PR13                     $CHAR4.                                  
      @740    PR14                     $CHAR4.                                  
      @744    PR15                     $CHAR4.                                  
      @748    PR16                     $CHAR4.                                  
      @752    PR17                     $CHAR4.                                  
      @756    PR18                     $CHAR4.                                  
      @760    PR19                     $CHAR4.                                  
      @764    PR20                     $CHAR4.                                  
      @768    PRCCS1                   N3PF.                                    
      @771    PRCCS2                   N3PF.                                    
      @774    PRCCS3                   N3PF.                                    
      @777    PRCCS4                   N3PF.                                    
      @780    PRCCS5                   N3PF.                                    
      @783    PRCCS6                   N3PF.                                    
      @786    PRCCS7                   N3PF.                                    
      @789    PRCCS8                   N3PF.                                    
      @792    PRCCS9                   N3PF.                                    
      @795    PRCCS10                  N3PF.                                    
      @798    PRCCS11                  N3PF.                                    
      @801    PRCCS12                  N3PF.                                    
      @804    PRCCS13                  N3PF.                                    
      @807    PRCCS14                  N3PF.                                    
      @810    PRCCS15                  N3PF.                                    
      @813    PRCCS16                  N3PF.                                    
      @816    PRCCS17                  N3PF.                                    
      @819    PRCCS18                  N3PF.                                    
      @822    PRCCS19                  N3PF.                                    
      @825    PRCCS20                  N3PF.                                    
      @828    PRDAY1                   N5PF.                                    
      @833    PRDAY2                   N5PF.                                    
      @838    PRDAY3                   N5PF.                                    
      @843    PRDAY4                   N5PF.                                    
      @848    PRDAY5                   N5PF.                                    
      @853    PRDAY6                   N5PF.                                    
      @858    PRDAY7                   N5PF.                                    
      @863    PRDAY8                   N5PF.                                    
      @868    PRDAY9                   N5PF.                                    
      @873    PRDAY10                  N5PF.                                    
      @878    PRDAY11                  N5PF.                                    
      @883    PRDAY12                  N5PF.                                    
      @888    PRDAY13                  N5PF.                                    
      @893    PRDAY14                  N5PF.                                    
      @898    PRDAY15                  N5PF.                                    
      @903    PRDAY16                  N5PF.                                    
      @908    PRDAY17                  N5PF.                                    
      @913    PRDAY18                  N5PF.                                    
      @918    PRDAY19                  N5PF.                                    
      @923    PRDAY20                  N5PF.                                    
      @928    PROCTYPE                 N3PF.                                    
      @931    PSTATE                   $CHAR2.                                  
      @933    PSTCO                    N5PF.                                    
      @938    PSTCO2                   N5PF.                                    
      @943    RACE                     N2PF.                                    
      @945    RACE_X                   $CHAR8.                                  
      @953    READMIT                  N2PF.                                    
      @955    TOTCHG                   N10PF.                                   
      @965    TOTCHG_X                 N15P2F.                                  
      @980    YEAR                     N4PF.                                    
      @984    ZIP3                     $CHAR3.                                  
      @987    ZIPINC_QRTL              N3PF.                                    
      @990    TOWN                     $CHAR8.                                  
      @998    ZIP                      $CHAR5.                                  
      @1003   AYEAR                    N4PF.                                    
      @1007   DMONTH                   N2PF.                                    
      @1009   BMONTH                   N2PF.                                    
      @1011   BYEAR                    N4PF.                                    
      @1015   PRMONTH1                 N2PF.                                    
      @1017   PRMONTH2                 N2PF.                                    
      @1019   PRMONTH3                 N2PF.                                    
      @1021   PRMONTH4                 N2PF.                                    
      @1023   PRMONTH5                 N2PF.                                    
      @1025   PRMONTH6                 N2PF.                                    
      @1027   PRMONTH7                 N2PF.                                    
      @1029   PRMONTH8                 N2PF.                                    
      @1031   PRMONTH9                 N2PF.                                    
      @1033   PRMONTH10                N2PF.                                    
      @1035   PRMONTH11                N2PF.                                    
      @1037   PRMONTH12                N2PF.                                    
      @1039   PRMONTH13                N2PF.                                    
      @1041   PRMONTH14                N2PF.                                    
      @1043   PRMONTH15                N2PF.                                    
      @1045   PRMONTH16                N2PF.                                    
      @1047   PRMONTH17                N2PF.                                    
      @1049   PRMONTH18                N2PF.                                    
      @1051   PRMONTH19                N2PF.                                    
      @1053   PRMONTH20                N2PF.                                    
      @1055   PRYEAR1                  N4PF.                                    
      @1059   PRYEAR2                  N4PF.                                    
      @1063   PRYEAR3                  N4PF.                                    
      @1067   PRYEAR4                  N4PF.                                    
      @1071   PRYEAR5                  N4PF.                                    
      @1075   PRYEAR6                  N4PF.                                    
      @1079   PRYEAR7                  N4PF.                                    
      @1083   PRYEAR8                  N4PF.                                    
      @1087   PRYEAR9                  N4PF.                                    
      @1091   PRYEAR10                 N4PF.                                    
      @1095   PRYEAR11                 N4PF.                                    
      @1099   PRYEAR12                 N4PF.                                    
      @1103   PRYEAR13                 N4PF.                                    
      @1107   PRYEAR14                 N4PF.                                    
      @1111   PRYEAR15                 N4PF.                                    
      @1115   PRYEAR16                 N4PF.                                    
      @1119   PRYEAR17                 N4PF.                                    
      @1123   PRYEAR18                 N4PF.                                    
      @1127   PRYEAR19                 N4PF.                                    
      @1131   PRYEAR20                 N4PF.                                    
      ;                                                                         
                                                                                
                                                                                
RUN;
