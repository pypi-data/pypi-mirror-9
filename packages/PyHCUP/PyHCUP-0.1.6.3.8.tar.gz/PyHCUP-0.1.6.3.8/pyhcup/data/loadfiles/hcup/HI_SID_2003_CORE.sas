/*******************************************************************            
*   HI_SID_2003_CORE.SAS:                                                       
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
DATA HI_SIDC_2003_CORE;                                                         
INFILE 'HI_SID_2003_CORE.ASC' LRECL = 791;                                      
                                                                                
*** Variable attribute ***;                                                     
ATTRIB                                                                          
  HOSPID                     LENGTH=4                 FORMAT=Z5.                
  LABEL="HCUP hospital identification number"                                   
                                                                                
  HOSPST                     LENGTH=$2                                          
  LABEL="Hospital state postal code"                                            
                                                                                
  KEY                        LENGTH=8                 FORMAT=Z14.               
  LABEL="HCUP record identifier"                                                
                                                                                
  AGEDAY                     LENGTH=3                                           
  LABEL="Age in days (when age < 1 year)"                                       
                                                                                
  AGEMONTH                   LENGTH=3                                           
  LABEL="Age in months (when age < 11 years)"                                   
                                                                                
  AMONTH                     LENGTH=3                                           
  LABEL="Admission month"                                                       
                                                                                
  ASOURCE                    LENGTH=3                                           
  LABEL="Admission source (uniform)"                                            
                                                                                
  ASOURCE_X                  LENGTH=$1                                          
  LABEL="Admission source (as received from source)"                            
                                                                                
  ASOURCEUB92                LENGTH=$1                                          
  LABEL="Admission source (UB-92 standard coding)"                              
                                                                                
  ATYPE                      LENGTH=3                                           
  LABEL="Admission type"                                                        
                                                                                
  AWEEKEND                   LENGTH=3                                           
  LABEL="Admission day is a weekend"                                            
                                                                                
  BWT                        LENGTH=4                                           
  LABEL="Birth weight in grams"                                                 
                                                                                
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
                                                                                
  DRGVER                     LENGTH=3                                           
  LABEL="DRG grouper version used on discharge date"                            
                                                                                
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
                                                                                
  LOS                        LENGTH=4                                           
  LABEL="Length of stay (cleaned)"                                              
                                                                                
  LOS_X                      LENGTH=4                                           
  LABEL="Length of stay (as received from source)"                              
                                                                                
  MDC                        LENGTH=3                                           
  LABEL="MDC in effect on discharge date"                                       
                                                                                
  MDC18                      LENGTH=3                                           
  LABEL="MDC, version 18"                                                       
                                                                                
  MRN_R                      LENGTH=5                                           
  LABEL="Medical record number (re-identified)"                                 
                                                                                
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
                                                                                
  PAY1_X                     LENGTH=$2                                          
  LABEL="Primary expected payer (as received from source)"                      
                                                                                
  PL_CBSA                    LENGTH=3                                           
  LABEL="Patient location: Core Based Statistical Area (CBSA)"                  
                                                                                
  PL_MSA1993                 LENGTH=3                                           
  LABEL="Patient location: Metropolitan Statistical Area (MSA), 1993"           
                                                                                
  PL_RUCA                    LENGTH=4                 FORMAT=4.1                
  LABEL="Patient location: Rural-Urban Commuting Area (RUCA) Codes"             
                                                                                
  PL_RUCA10                  LENGTH=3                                           
  LABEL="Patient location: Rural-Urban Commuting Area (RUCA) Codes, ten levels" 
                                                                                
  PL_RUCA4                   LENGTH=3                                           
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
                                                                                
  PSTATE                     LENGTH=$2                                          
  LABEL="Patient State postal code"                                             
                                                                                
  PSTCO2                     LENGTH=4                                           
  LABEL="Patient state/county FIPS code, possibly derived from ZIP Code"        
                                                                                
  RACE                       LENGTH=3                                           
  LABEL="Race (uniform)"                                                        
                                                                                
  RACE_X                     LENGTH=$2                                          
  LABEL="Race (as received from source)"                                        
                                                                                
  TOTCHG                     LENGTH=6                                           
  LABEL="Total charges (cleaned)"                                               
                                                                                
  TOTCHG_X                   LENGTH=7                                           
  LABEL="Total charges (as received from source)"                               
                                                                                
  YEAR                       LENGTH=3                                           
  LABEL="Calendar year"                                                         
                                                                                
  ZIP                        LENGTH=$5                                          
  LABEL="Patient ZIP Code"                                                      
                                                                                
  AGEGROUP                   LENGTH=3                                           
  LABEL="Age Group"                                                             
                                                                                
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
      @1      HOSPID                   N5PF.                                    
      @6      HOSPST                   $CHAR2.                                  
      @8      KEY                      14.                                      
      @22     AGEDAY                   N3PF.                                    
      @25     AGEMONTH                 N3PF.                                    
      @28     AMONTH                   N2PF.                                    
      @30     ASOURCE                  N2PF.                                    
      @32     ASOURCE_X                $CHAR1.                                  
      @33     ASOURCEUB92              $CHAR1.                                  
      @34     ATYPE                    N2PF.                                    
      @36     AWEEKEND                 N2PF.                                    
      @38     BWT                      N4PF.                                    
      @42     DIED                     N2PF.                                    
      @44     DISP_X                   $CHAR2.                                  
      @46     DISPUB92                 N2PF.                                    
      @48     DISPUNIFORM              N2PF.                                    
      @50     DQTR                     N2PF.                                    
      @52     DRG                      N3PF.                                    
      @55     DRG18                    N3PF.                                    
      @58     DRGVER                   N2PF.                                    
      @60     DX1                      $CHAR5.                                  
      @65     DX2                      $CHAR5.                                  
      @70     DX3                      $CHAR5.                                  
      @75     DX4                      $CHAR5.                                  
      @80     DX5                      $CHAR5.                                  
      @85     DX6                      $CHAR5.                                  
      @90     DX7                      $CHAR5.                                  
      @95     DX8                      $CHAR5.                                  
      @100    DX9                      $CHAR5.                                  
      @105    DX10                     $CHAR5.                                  
      @110    DX11                     $CHAR5.                                  
      @115    DX12                     $CHAR5.                                  
      @120    DX13                     $CHAR5.                                  
      @125    DX14                     $CHAR5.                                  
      @130    DX15                     $CHAR5.                                  
      @135    DX16                     $CHAR5.                                  
      @140    DX17                     $CHAR5.                                  
      @145    DX18                     $CHAR5.                                  
      @150    DX19                     $CHAR5.                                  
      @155    DX20                     $CHAR5.                                  
      @160    DXCCS1                   N4PF.                                    
      @164    DXCCS2                   N4PF.                                    
      @168    DXCCS3                   N4PF.                                    
      @172    DXCCS4                   N4PF.                                    
      @176    DXCCS5                   N4PF.                                    
      @180    DXCCS6                   N4PF.                                    
      @184    DXCCS7                   N4PF.                                    
      @188    DXCCS8                   N4PF.                                    
      @192    DXCCS9                   N4PF.                                    
      @196    DXCCS10                  N4PF.                                    
      @200    DXCCS11                  N4PF.                                    
      @204    DXCCS12                  N4PF.                                    
      @208    DXCCS13                  N4PF.                                    
      @212    DXCCS14                  N4PF.                                    
      @216    DXCCS15                  N4PF.                                    
      @220    DXCCS16                  N4PF.                                    
      @224    DXCCS17                  N4PF.                                    
      @228    DXCCS18                  N4PF.                                    
      @232    DXCCS19                  N4PF.                                    
      @236    DXCCS20                  N4PF.                                    
      @240    ECODE1                   $CHAR5.                                  
      @245    ECODE2                   $CHAR5.                                  
      @250    ECODE3                   $CHAR5.                                  
      @255    ECODE4                   $CHAR5.                                  
      @260    ECODE5                   $CHAR5.                                  
      @265    ECODE6                   $CHAR5.                                  
      @270    ECODE7                   $CHAR5.                                  
      @275    ECODE8                   $CHAR5.                                  
      @280    E_CCS1                   N4PF.                                    
      @284    E_CCS2                   N4PF.                                    
      @288    E_CCS3                   N4PF.                                    
      @292    E_CCS4                   N4PF.                                    
      @296    E_CCS5                   N4PF.                                    
      @300    E_CCS6                   N4PF.                                    
      @304    E_CCS7                   N4PF.                                    
      @308    E_CCS8                   N4PF.                                    
      @312    FEMALE                   N2PF.                                    
      @314    LOS                      N5PF.                                    
      @319    LOS_X                    N6PF.                                    
      @325    MDC                      N2PF.                                    
      @327    MDC18                    N2PF.                                    
      @329    MRN_R                    N9PF.                                    
      @338    NDX                      N2PF.                                    
      @340    NECODE                   N2PF.                                    
      @342    NEOMAT                   N2PF.                                    
      @344    NPR                      N2PF.                                    
      @346    PAY1                     N2PF.                                    
      @348    PAY1_X                   $CHAR2.                                  
      @350    PL_CBSA                  N3PF.                                    
      @353    PL_MSA1993               N3PF.                                    
      @356    PL_RUCA                  N4P1F.                                   
      @360    PL_RUCA10                N2PF.                                    
      @362    PL_RUCA4                 N2PF.                                    
      @364    PL_RUCC2003              N2PF.                                    
      @366    PL_UIC2003               N2PF.                                    
      @368    PL_UR_CAT4               N2PF.                                    
      @370    PL_UR_CAT5               N2PF.                                    
      @372    PR1                      $CHAR4.                                  
      @376    PR2                      $CHAR4.                                  
      @380    PR3                      $CHAR4.                                  
      @384    PR4                      $CHAR4.                                  
      @388    PR5                      $CHAR4.                                  
      @392    PR6                      $CHAR4.                                  
      @396    PR7                      $CHAR4.                                  
      @400    PR8                      $CHAR4.                                  
      @404    PR9                      $CHAR4.                                  
      @408    PR10                     $CHAR4.                                  
      @412    PR11                     $CHAR4.                                  
      @416    PR12                     $CHAR4.                                  
      @420    PR13                     $CHAR4.                                  
      @424    PR14                     $CHAR4.                                  
      @428    PR15                     $CHAR4.                                  
      @432    PR16                     $CHAR4.                                  
      @436    PR17                     $CHAR4.                                  
      @440    PR18                     $CHAR4.                                  
      @444    PR19                     $CHAR4.                                  
      @448    PR20                     $CHAR4.                                  
      @452    PRCCS1                   N3PF.                                    
      @455    PRCCS2                   N3PF.                                    
      @458    PRCCS3                   N3PF.                                    
      @461    PRCCS4                   N3PF.                                    
      @464    PRCCS5                   N3PF.                                    
      @467    PRCCS6                   N3PF.                                    
      @470    PRCCS7                   N3PF.                                    
      @473    PRCCS8                   N3PF.                                    
      @476    PRCCS9                   N3PF.                                    
      @479    PRCCS10                  N3PF.                                    
      @482    PRCCS11                  N3PF.                                    
      @485    PRCCS12                  N3PF.                                    
      @488    PRCCS13                  N3PF.                                    
      @491    PRCCS14                  N3PF.                                    
      @494    PRCCS15                  N3PF.                                    
      @497    PRCCS16                  N3PF.                                    
      @500    PRCCS17                  N3PF.                                    
      @503    PRCCS18                  N3PF.                                    
      @506    PRCCS19                  N3PF.                                    
      @509    PRCCS20                  N3PF.                                    
      @512    PRDAY1                   N5PF.                                    
      @517    PRDAY2                   N5PF.                                    
      @522    PRDAY3                   N5PF.                                    
      @527    PRDAY4                   N5PF.                                    
      @532    PRDAY5                   N5PF.                                    
      @537    PRDAY6                   N5PF.                                    
      @542    PRDAY7                   N5PF.                                    
      @547    PRDAY8                   N5PF.                                    
      @552    PRDAY9                   N5PF.                                    
      @557    PRDAY10                  N5PF.                                    
      @562    PRDAY11                  N5PF.                                    
      @567    PRDAY12                  N5PF.                                    
      @572    PRDAY13                  N5PF.                                    
      @577    PRDAY14                  N5PF.                                    
      @582    PRDAY15                  N5PF.                                    
      @587    PRDAY16                  N5PF.                                    
      @592    PRDAY17                  N5PF.                                    
      @597    PRDAY18                  N5PF.                                    
      @602    PRDAY19                  N5PF.                                    
      @607    PRDAY20                  N5PF.                                    
      @612    PSTATE                   $CHAR2.                                  
      @614    PSTCO2                   N5PF.                                    
      @619    RACE                     N2PF.                                    
      @621    RACE_X                   $CHAR2.                                  
      @623    TOTCHG                   N10PF.                                   
      @633    TOTCHG_X                 N15P2F.                                  
      @648    YEAR                     N4PF.                                    
      @652    ZIP                      $CHAR5.                                  
      @657    AGEGROUP                 N3PF.                                    
      @660    AYEAR                    N4PF.                                    
      @664    DMONTH                   N2PF.                                    
      @666    BMONTH                   N2PF.                                    
      @668    BYEAR                    N4PF.                                    
      @672    PRMONTH1                 N2PF.                                    
      @674    PRMONTH2                 N2PF.                                    
      @676    PRMONTH3                 N2PF.                                    
      @678    PRMONTH4                 N2PF.                                    
      @680    PRMONTH5                 N2PF.                                    
      @682    PRMONTH6                 N2PF.                                    
      @684    PRMONTH7                 N2PF.                                    
      @686    PRMONTH8                 N2PF.                                    
      @688    PRMONTH9                 N2PF.                                    
      @690    PRMONTH10                N2PF.                                    
      @692    PRMONTH11                N2PF.                                    
      @694    PRMONTH12                N2PF.                                    
      @696    PRMONTH13                N2PF.                                    
      @698    PRMONTH14                N2PF.                                    
      @700    PRMONTH15                N2PF.                                    
      @702    PRMONTH16                N2PF.                                    
      @704    PRMONTH17                N2PF.                                    
      @706    PRMONTH18                N2PF.                                    
      @708    PRMONTH19                N2PF.                                    
      @710    PRMONTH20                N2PF.                                    
      @712    PRYEAR1                  N4PF.                                    
      @716    PRYEAR2                  N4PF.                                    
      @720    PRYEAR3                  N4PF.                                    
      @724    PRYEAR4                  N4PF.                                    
      @728    PRYEAR5                  N4PF.                                    
      @732    PRYEAR6                  N4PF.                                    
      @736    PRYEAR7                  N4PF.                                    
      @740    PRYEAR8                  N4PF.                                    
      @744    PRYEAR9                  N4PF.                                    
      @748    PRYEAR10                 N4PF.                                    
      @752    PRYEAR11                 N4PF.                                    
      @756    PRYEAR12                 N4PF.                                    
      @760    PRYEAR13                 N4PF.                                    
      @764    PRYEAR14                 N4PF.                                    
      @768    PRYEAR15                 N4PF.                                    
      @772    PRYEAR16                 N4PF.                                    
      @776    PRYEAR17                 N4PF.                                    
      @780    PRYEAR18                 N4PF.                                    
      @784    PRYEAR19                 N4PF.                                    
      @788    PRYEAR20                 N4PF.                                    
      ;                                                                         
                                                                                
                                                                                
RUN;
