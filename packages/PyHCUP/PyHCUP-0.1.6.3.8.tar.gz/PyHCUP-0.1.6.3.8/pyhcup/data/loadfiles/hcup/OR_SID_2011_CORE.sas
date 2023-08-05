/*******************************************************************            
*   OR_SID_2011_CORE.SAS:                                                       
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
DATA OR_SIDC_2011_CORE;                                                         
INFILE 'OR_SID_2011_CORE.ASC' LRECL = 1060;                                     
                                                                                
*** Variable attribute ***;                                                     
ATTRIB                                                                          
  AGE                        LENGTH=3                                           
  LABEL="Age in years at admission"                                             
                                                                                
  AGEDAY                     LENGTH=3                                           
  LABEL="Age in days (when age < 1 year)"                                       
                                                                                
  AGEMONTH                   LENGTH=3                                           
  LABEL="Age in months (when age < 11 years)"                                   
                                                                                
  AHOUR                      LENGTH=3                 FORMAT=Z4.                
  LABEL="Admission Hour"                                                        
                                                                                
  AMONTH                     LENGTH=3                                           
  LABEL="Admission month"                                                       
                                                                                
  ATYPE                      LENGTH=3                                           
  LABEL="Admission type"                                                        
                                                                                
  AWEEKEND                   LENGTH=3                                           
  LABEL="Admission day is a weekend"                                            
                                                                                
  BWT                        LENGTH=4                                           
  LABEL="Birth weight in grams"                                                 
                                                                                
  DHOUR                      LENGTH=3                 FORMAT=Z4.                
  LABEL="Discharge Hour"                                                        
                                                                                
  DIED                       LENGTH=3                                           
  LABEL="Died during hospitalization"                                           
                                                                                
  DISPUB04                   LENGTH=3                                           
  LABEL="Disposition of patient (UB-04 standard coding)"                        
                                                                                
  DISPUNIFORM                LENGTH=3                                           
  LABEL="Disposition of patient (uniform)"                                      
                                                                                
  DISP_X                     LENGTH=$2                                          
  LABEL="Disposition of patient (as received from source)"                      
                                                                                
  DNR                        LENGTH=3                                           
  LABEL="Do not resuscitate indicator"                                          
                                                                                
  DQTR                       LENGTH=3                                           
  LABEL="Discharge quarter"                                                     
                                                                                
  DRG                        LENGTH=3                                           
  LABEL="DRG in effect on discharge date"                                       
                                                                                
  DRG24                      LENGTH=3                                           
  LABEL="DRG, version 24"                                                       
                                                                                
  DRGVER                     LENGTH=3                                           
  LABEL="DRG grouper version used on discharge date"                            
                                                                                
  DRG_NoPOA                  LENGTH=3                                           
  LABEL="DRG in use on discharge date, calculated without POA"                  
                                                                                
  DSHOSPID                   LENGTH=$17                                         
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
                                                                                
  DXPOA1                     LENGTH=$1                                          
  LABEL="Diagnosis 1, present on admission indicator"                           
                                                                                
  DXPOA2                     LENGTH=$1                                          
  LABEL="Diagnosis 2, present on admission indicator"                           
                                                                                
  DXPOA3                     LENGTH=$1                                          
  LABEL="Diagnosis 3, present on admission indicator"                           
                                                                                
  DXPOA4                     LENGTH=$1                                          
  LABEL="Diagnosis 4, present on admission indicator"                           
                                                                                
  DXPOA5                     LENGTH=$1                                          
  LABEL="Diagnosis 5, present on admission indicator"                           
                                                                                
  DXPOA6                     LENGTH=$1                                          
  LABEL="Diagnosis 6, present on admission indicator"                           
                                                                                
  DXPOA7                     LENGTH=$1                                          
  LABEL="Diagnosis 7, present on admission indicator"                           
                                                                                
  DXPOA8                     LENGTH=$1                                          
  LABEL="Diagnosis 8, present on admission indicator"                           
                                                                                
  DXPOA9                     LENGTH=$1                                          
  LABEL="Diagnosis 9, present on admission indicator"                           
                                                                                
  DXPOA10                    LENGTH=$1                                          
  LABEL="Diagnosis 10, present on admission indicator"                          
                                                                                
  DXPOA11                    LENGTH=$1                                          
  LABEL="Diagnosis 11, present on admission indicator"                          
                                                                                
  DXPOA12                    LENGTH=$1                                          
  LABEL="Diagnosis 12, present on admission indicator"                          
                                                                                
  DXPOA13                    LENGTH=$1                                          
  LABEL="Diagnosis 13, present on admission indicator"                          
                                                                                
  DXPOA14                    LENGTH=$1                                          
  LABEL="Diagnosis 14, present on admission indicator"                          
                                                                                
  DXPOA15                    LENGTH=$1                                          
  LABEL="Diagnosis 15, present on admission indicator"                          
                                                                                
  DXPOA16                    LENGTH=$1                                          
  LABEL="Diagnosis 16, present on admission indicator"                          
                                                                                
  DXPOA17                    LENGTH=$1                                          
  LABEL="Diagnosis 17, present on admission indicator"                          
                                                                                
  DXPOA18                    LENGTH=$1                                          
  LABEL="Diagnosis 18, present on admission indicator"                          
                                                                                
  DXPOA19                    LENGTH=$1                                          
  LABEL="Diagnosis 19, present on admission indicator"                          
                                                                                
  DXPOA20                    LENGTH=$1                                          
  LABEL="Diagnosis 20, present on admission indicator"                          
                                                                                
  DXPOA21                    LENGTH=$1                                          
  LABEL="Diagnosis 21, present on admission indicator"                          
                                                                                
  DXPOA22                    LENGTH=$1                                          
  LABEL="Diagnosis 22, present on admission indicator"                          
                                                                                
  DXPOA23                    LENGTH=$1                                          
  LABEL="Diagnosis 23, present on admission indicator"                          
                                                                                
  DXPOA24                    LENGTH=$1                                          
  LABEL="Diagnosis 24, present on admission indicator"                          
                                                                                
  DXPOA25                    LENGTH=$1                                          
  LABEL="Diagnosis 25, present on admission indicator"                          
                                                                                
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
                                                                                
  ECODE9                     LENGTH=$5                                          
  LABEL="E code 9"                                                              
                                                                                
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
                                                                                
  E_CCS9                     LENGTH=3                                           
  LABEL="CCS: E Code 9"                                                         
                                                                                
  E_POA1                     LENGTH=$1                                          
  LABEL="E Code 1, present on admission indicator"                              
                                                                                
  E_POA2                     LENGTH=$1                                          
  LABEL="E Code 2, present on admission indicator"                              
                                                                                
  E_POA3                     LENGTH=$1                                          
  LABEL="E Code 3, present on admission indicator"                              
                                                                                
  E_POA4                     LENGTH=$1                                          
  LABEL="E Code 4, present on admission indicator"                              
                                                                                
  E_POA5                     LENGTH=$1                                          
  LABEL="E Code 5, present on admission indicator"                              
                                                                                
  E_POA6                     LENGTH=$1                                          
  LABEL="E Code 6, present on admission indicator"                              
                                                                                
  E_POA7                     LENGTH=$1                                          
  LABEL="E Code 7, present on admission indicator"                              
                                                                                
  E_POA8                     LENGTH=$1                                          
  LABEL="E Code 8, present on admission indicator"                              
                                                                                
  E_POA9                     LENGTH=$1                                          
  LABEL="E Code 9, present on admission indicator"                              
                                                                                
  FEMALE                     LENGTH=3                                           
  LABEL="Indicator of sex"                                                      
                                                                                
  HCUP_ED                    LENGTH=3                                           
  LABEL="HCUP Emergency Department service indicator"                           
                                                                                
  HCUP_OS                    LENGTH=3                                           
  LABEL="HCUP Observation Stay service indicator"                               
                                                                                
  HCUP_SURGERY_BROAD         LENGTH=3                                           
  LABEL="Revised HCUP_AS (PCLASSn=3 or 4, or broad definition)"                 
                                                                                
  HCUP_SURGERY_NARROW        LENGTH=3                                           
  LABEL="Revised HCUP_AS (PCLASSn=4, or narrow definition)"                     
                                                                                
  HISPANIC_X                 LENGTH=$2                                          
  LABEL="Hispanic ethnicity (as received from source)"                          
                                                                                
  HOSPBRTH                   LENGTH=3                                           
  LABEL="Indicator of birth in this hospital"                                   
                                                                                
  HOSPST                     LENGTH=$2                                          
  LABEL="Hospital state postal code"                                            
                                                                                
  KEY                        LENGTH=8                 FORMAT=Z18.               
  LABEL="HCUP record identifier"                                                
                                                                                
  LOS                        LENGTH=4                                           
  LABEL="Length of stay (cleaned)"                                              
                                                                                
  LOS_X                      LENGTH=4                                           
  LABEL="Length of stay (as received from source)"                              
                                                                                
  MDC                        LENGTH=3                                           
  LABEL="MDC in effect on discharge date"                                       
                                                                                
  MDC24                      LENGTH=3                                           
  LABEL="MDC, version 24"                                                       
                                                                                
  MDC_NoPOA                  LENGTH=3                                           
  LABEL="MDC in use on discharge date, calculated without POA"                  
                                                                                
  MEDINCSTQ                  LENGTH=3                                           
  LABEL="Median household income state quartile for patient ZIP Code"           
                                                                                
  NCHRONIC                   LENGTH=3                                           
  LABEL="Number of chronic conditions"                                          
                                                                                
  NDX                        LENGTH=3                                           
  LABEL="Number of diagnoses on this record"                                    
                                                                                
  NECODE                     LENGTH=3                                           
  LABEL="Number of E codes on this record"                                      
                                                                                
  NEOMAT                     LENGTH=3                                           
  LABEL="Neonatal and/or maternal DX and/or PR"                                 
                                                                                
  NPR                        LENGTH=3                                           
  LABEL="Number of procedures on this record"                                   
                                                                                
  ORPROC                     LENGTH=3                                           
  LABEL="Major operating room procedure indicator"                              
                                                                                
  OS_TIME                    LENGTH=4                                           
  LABEL="Observation stay time summed from UNITS"                               
                                                                                
  PAY1                       LENGTH=3                                           
  LABEL="Primary expected payer (uniform)"                                      
                                                                                
  PAY1_X                     LENGTH=$9                                          
  LABEL="Primary expected payer (as received from source)"                      
                                                                                
  PAY2                       LENGTH=3                                           
  LABEL="Secondary expected payer (uniform)"                                    
                                                                                
  PAY2_X                     LENGTH=$9                                          
  LABEL="Secondary expected payer (as received from source)"                    
                                                                                
  PAY3                       LENGTH=3                                           
  LABEL="Tertiary expected payer (uniform)"                                     
                                                                                
  PAY3_X                     LENGTH=$9                                          
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
                                                                                
  TOTCHG                     LENGTH=6                                           
  LABEL="Total charges (cleaned)"                                               
                                                                                
  TOTCHG_X                   LENGTH=7                                           
  LABEL="Total charges (as received from source)"                               
                                                                                
  TRAN_IN                    LENGTH=3                                           
  LABEL="Transfer in indicator"                                                 
                                                                                
  TRAN_OUT                   LENGTH=3                                           
  LABEL="Transfer out indicator"                                                
                                                                                
  YEAR                       LENGTH=3                                           
  LABEL="Calendar year"                                                         
                                                                                
  ZIP3                       LENGTH=$3                                          
  LABEL="Patient ZIP Code, first 3 digits"                                      
                                                                                
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
      @10     AHOUR                    N4PF.                                    
      @14     AMONTH                   N2PF.                                    
      @16     ATYPE                    N2PF.                                    
      @18     AWEEKEND                 N2PF.                                    
      @20     BWT                      N4PF.                                    
      @24     DHOUR                    N4PF.                                    
      @28     DIED                     N2PF.                                    
      @30     DISPUB04                 N2PF.                                    
      @32     DISPUNIFORM              N2PF.                                    
      @34     DISP_X                   $CHAR2.                                  
      @36     DNR                      N2PF.                                    
      @38     DQTR                     N2PF.                                    
      @40     DRG                      N3PF.                                    
      @43     DRG24                    N3PF.                                    
      @46     DRGVER                   N2PF.                                    
      @48     DRG_NoPOA                N3PF.                                    
      @51     DSHOSPID                 $CHAR17.                                 
      @68     DX1                      $CHAR5.                                  
      @73     DX2                      $CHAR5.                                  
      @78     DX3                      $CHAR5.                                  
      @83     DX4                      $CHAR5.                                  
      @88     DX5                      $CHAR5.                                  
      @93     DX6                      $CHAR5.                                  
      @98     DX7                      $CHAR5.                                  
      @103    DX8                      $CHAR5.                                  
      @108    DX9                      $CHAR5.                                  
      @113    DX10                     $CHAR5.                                  
      @118    DX11                     $CHAR5.                                  
      @123    DX12                     $CHAR5.                                  
      @128    DX13                     $CHAR5.                                  
      @133    DX14                     $CHAR5.                                  
      @138    DX15                     $CHAR5.                                  
      @143    DX16                     $CHAR5.                                  
      @148    DX17                     $CHAR5.                                  
      @153    DX18                     $CHAR5.                                  
      @158    DX19                     $CHAR5.                                  
      @163    DX20                     $CHAR5.                                  
      @168    DX21                     $CHAR5.                                  
      @173    DX22                     $CHAR5.                                  
      @178    DX23                     $CHAR5.                                  
      @183    DX24                     $CHAR5.                                  
      @188    DX25                     $CHAR5.                                  
      @193    DXCCS1                   N4PF.                                    
      @197    DXCCS2                   N4PF.                                    
      @201    DXCCS3                   N4PF.                                    
      @205    DXCCS4                   N4PF.                                    
      @209    DXCCS5                   N4PF.                                    
      @213    DXCCS6                   N4PF.                                    
      @217    DXCCS7                   N4PF.                                    
      @221    DXCCS8                   N4PF.                                    
      @225    DXCCS9                   N4PF.                                    
      @229    DXCCS10                  N4PF.                                    
      @233    DXCCS11                  N4PF.                                    
      @237    DXCCS12                  N4PF.                                    
      @241    DXCCS13                  N4PF.                                    
      @245    DXCCS14                  N4PF.                                    
      @249    DXCCS15                  N4PF.                                    
      @253    DXCCS16                  N4PF.                                    
      @257    DXCCS17                  N4PF.                                    
      @261    DXCCS18                  N4PF.                                    
      @265    DXCCS19                  N4PF.                                    
      @269    DXCCS20                  N4PF.                                    
      @273    DXCCS21                  N4PF.                                    
      @277    DXCCS22                  N4PF.                                    
      @281    DXCCS23                  N4PF.                                    
      @285    DXCCS24                  N4PF.                                    
      @289    DXCCS25                  N4PF.                                    
      @293    DXPOA1                   $CHAR1.                                  
      @294    DXPOA2                   $CHAR1.                                  
      @295    DXPOA3                   $CHAR1.                                  
      @296    DXPOA4                   $CHAR1.                                  
      @297    DXPOA5                   $CHAR1.                                  
      @298    DXPOA6                   $CHAR1.                                  
      @299    DXPOA7                   $CHAR1.                                  
      @300    DXPOA8                   $CHAR1.                                  
      @301    DXPOA9                   $CHAR1.                                  
      @302    DXPOA10                  $CHAR1.                                  
      @303    DXPOA11                  $CHAR1.                                  
      @304    DXPOA12                  $CHAR1.                                  
      @305    DXPOA13                  $CHAR1.                                  
      @306    DXPOA14                  $CHAR1.                                  
      @307    DXPOA15                  $CHAR1.                                  
      @308    DXPOA16                  $CHAR1.                                  
      @309    DXPOA17                  $CHAR1.                                  
      @310    DXPOA18                  $CHAR1.                                  
      @311    DXPOA19                  $CHAR1.                                  
      @312    DXPOA20                  $CHAR1.                                  
      @313    DXPOA21                  $CHAR1.                                  
      @314    DXPOA22                  $CHAR1.                                  
      @315    DXPOA23                  $CHAR1.                                  
      @316    DXPOA24                  $CHAR1.                                  
      @317    DXPOA25                  $CHAR1.                                  
      @318    ECODE1                   $CHAR5.                                  
      @323    ECODE2                   $CHAR5.                                  
      @328    ECODE3                   $CHAR5.                                  
      @333    ECODE4                   $CHAR5.                                  
      @338    ECODE5                   $CHAR5.                                  
      @343    ECODE6                   $CHAR5.                                  
      @348    ECODE7                   $CHAR5.                                  
      @353    ECODE8                   $CHAR5.                                  
      @358    ECODE9                   $CHAR5.                                  
      @363    E_CCS1                   N4PF.                                    
      @367    E_CCS2                   N4PF.                                    
      @371    E_CCS3                   N4PF.                                    
      @375    E_CCS4                   N4PF.                                    
      @379    E_CCS5                   N4PF.                                    
      @383    E_CCS6                   N4PF.                                    
      @387    E_CCS7                   N4PF.                                    
      @391    E_CCS8                   N4PF.                                    
      @395    E_CCS9                   N4PF.                                    
      @399    E_POA1                   $CHAR1.                                  
      @400    E_POA2                   $CHAR1.                                  
      @401    E_POA3                   $CHAR1.                                  
      @402    E_POA4                   $CHAR1.                                  
      @403    E_POA5                   $CHAR1.                                  
      @404    E_POA6                   $CHAR1.                                  
      @405    E_POA7                   $CHAR1.                                  
      @406    E_POA8                   $CHAR1.                                  
      @407    E_POA9                   $CHAR1.                                  
      @408    FEMALE                   N2PF.                                    
      @410    HCUP_ED                  N2PF.                                    
      @412    HCUP_OS                  N2PF.                                    
      @414    HCUP_SURGERY_BROAD       N2PF.                                    
      @416    HCUP_SURGERY_NARROW      N2PF.                                    
      @418    HISPANIC_X               $CHAR2.                                  
      @420    HOSPBRTH                 N3PF.                                    
      @423    HOSPST                   $CHAR2.                                  
      @425    KEY                      18.                                      
      @443    LOS                      N5PF.                                    
      @448    LOS_X                    N6PF.                                    
      @454    MDC                      N2PF.                                    
      @456    MDC24                    N2PF.                                    
      @458    MDC_NoPOA                N2PF.                                    
      @460    MEDINCSTQ                N2PF.                                    
      @462    NCHRONIC                 N3PF.                                    
      @465    NDX                      N2PF.                                    
      @467    NECODE                   N2PF.                                    
      @469    NEOMAT                   N2PF.                                    
      @471    NPR                      N2PF.                                    
      @473    ORPROC                   N2PF.                                    
      @475    OS_TIME                  N8PF.                                    
      @483    PAY1                     N2PF.                                    
      @485    PAY1_X                   $CHAR9.                                  
      @494    PAY2                     N2PF.                                    
      @496    PAY2_X                   $CHAR9.                                  
      @505    PAY3                     N2PF.                                    
      @507    PAY3_X                   $CHAR9.                                  
      @516    PL_CBSA                  N3PF.                                    
      @519    PL_MSA1993               N3PF.                                    
      @522    PL_NCHS2006              N2PF.                                    
      @524    PL_RUCA10_2005           N2PF.                                    
      @526    PL_RUCA2005              N4P1F.                                   
      @530    PL_RUCA4_2005            N2PF.                                    
      @532    PL_RUCC2003              N2PF.                                    
      @534    PL_UIC2003               N2PF.                                    
      @536    PL_UR_CAT4               N2PF.                                    
      @538    PR1                      $CHAR4.                                  
      @542    PR2                      $CHAR4.                                  
      @546    PR3                      $CHAR4.                                  
      @550    PR4                      $CHAR4.                                  
      @554    PR5                      $CHAR4.                                  
      @558    PR6                      $CHAR4.                                  
      @562    PR7                      $CHAR4.                                  
      @566    PR8                      $CHAR4.                                  
      @570    PR9                      $CHAR4.                                  
      @574    PR10                     $CHAR4.                                  
      @578    PR11                     $CHAR4.                                  
      @582    PR12                     $CHAR4.                                  
      @586    PR13                     $CHAR4.                                  
      @590    PR14                     $CHAR4.                                  
      @594    PR15                     $CHAR4.                                  
      @598    PR16                     $CHAR4.                                  
      @602    PR17                     $CHAR4.                                  
      @606    PR18                     $CHAR4.                                  
      @610    PR19                     $CHAR4.                                  
      @614    PR20                     $CHAR4.                                  
      @618    PR21                     $CHAR4.                                  
      @622    PR22                     $CHAR4.                                  
      @626    PR23                     $CHAR4.                                  
      @630    PR24                     $CHAR4.                                  
      @634    PR25                     $CHAR4.                                  
      @638    PRCCS1                   N3PF.                                    
      @641    PRCCS2                   N3PF.                                    
      @644    PRCCS3                   N3PF.                                    
      @647    PRCCS4                   N3PF.                                    
      @650    PRCCS5                   N3PF.                                    
      @653    PRCCS6                   N3PF.                                    
      @656    PRCCS7                   N3PF.                                    
      @659    PRCCS8                   N3PF.                                    
      @662    PRCCS9                   N3PF.                                    
      @665    PRCCS10                  N3PF.                                    
      @668    PRCCS11                  N3PF.                                    
      @671    PRCCS12                  N3PF.                                    
      @674    PRCCS13                  N3PF.                                    
      @677    PRCCS14                  N3PF.                                    
      @680    PRCCS15                  N3PF.                                    
      @683    PRCCS16                  N3PF.                                    
      @686    PRCCS17                  N3PF.                                    
      @689    PRCCS18                  N3PF.                                    
      @692    PRCCS19                  N3PF.                                    
      @695    PRCCS20                  N3PF.                                    
      @698    PRCCS21                  N3PF.                                    
      @701    PRCCS22                  N3PF.                                    
      @704    PRCCS23                  N3PF.                                    
      @707    PRCCS24                  N3PF.                                    
      @710    PRCCS25                  N3PF.                                    
      @713    PRDAY1                   N5PF.                                    
      @718    PRDAY2                   N5PF.                                    
      @723    PRDAY3                   N5PF.                                    
      @728    PRDAY4                   N5PF.                                    
      @733    PRDAY5                   N5PF.                                    
      @738    PRDAY6                   N5PF.                                    
      @743    PRDAY7                   N5PF.                                    
      @748    PRDAY8                   N5PF.                                    
      @753    PRDAY9                   N5PF.                                    
      @758    PRDAY10                  N5PF.                                    
      @763    PRDAY11                  N5PF.                                    
      @768    PRDAY12                  N5PF.                                    
      @773    PRDAY13                  N5PF.                                    
      @778    PRDAY14                  N5PF.                                    
      @783    PRDAY15                  N5PF.                                    
      @788    PRDAY16                  N5PF.                                    
      @793    PRDAY17                  N5PF.                                    
      @798    PRDAY18                  N5PF.                                    
      @803    PRDAY19                  N5PF.                                    
      @808    PRDAY20                  N5PF.                                    
      @813    PRDAY21                  N5PF.                                    
      @818    PRDAY22                  N5PF.                                    
      @823    PRDAY23                  N5PF.                                    
      @828    PRDAY24                  N5PF.                                    
      @833    PRDAY25                  N5PF.                                    
      @838    PROCTYPE                 N3PF.                                    
      @841    PSTATE                   $CHAR2.                                  
      @843    PSTCO2                   N5PF.                                    
      @848    PointOfOriginUB04        $CHAR1.                                  
      @849    PointOfOrigin_X          $CHAR2.                                  
      @851    RACE                     N2PF.                                    
      @853    RACE_X                   $CHAR2.                                  
      @855    TOTCHG                   N10PF.                                   
      @865    TOTCHG_X                 N15P2F.                                  
      @880    TRAN_IN                  N2PF.                                    
      @882    TRAN_OUT                 N2PF.                                    
      @884    YEAR                     N4PF.                                    
      @888    ZIP3                     $CHAR3.                                  
      @891    ZIPINC_QRTL              N3PF.                                    
      @894    ZIP                      $CHAR5.                                  
      @899    AYEAR                    N4PF.                                    
      @903    DMONTH                   N2PF.                                    
      @905    BMONTH                   N2PF.                                    
      @907    BYEAR                    N4PF.                                    
      @911    PRMONTH1                 N2PF.                                    
      @913    PRMONTH2                 N2PF.                                    
      @915    PRMONTH3                 N2PF.                                    
      @917    PRMONTH4                 N2PF.                                    
      @919    PRMONTH5                 N2PF.                                    
      @921    PRMONTH6                 N2PF.                                    
      @923    PRMONTH7                 N2PF.                                    
      @925    PRMONTH8                 N2PF.                                    
      @927    PRMONTH9                 N2PF.                                    
      @929    PRMONTH10                N2PF.                                    
      @931    PRMONTH11                N2PF.                                    
      @933    PRMONTH12                N2PF.                                    
      @935    PRMONTH13                N2PF.                                    
      @937    PRMONTH14                N2PF.                                    
      @939    PRMONTH15                N2PF.                                    
      @941    PRMONTH16                N2PF.                                    
      @943    PRMONTH17                N2PF.                                    
      @945    PRMONTH18                N2PF.                                    
      @947    PRMONTH19                N2PF.                                    
      @949    PRMONTH20                N2PF.                                    
      @951    PRMONTH21                N2PF.                                    
      @953    PRMONTH22                N2PF.                                    
      @955    PRMONTH23                N2PF.                                    
      @957    PRMONTH24                N2PF.                                    
      @959    PRMONTH25                N2PF.                                    
      @961    PRYEAR1                  N4PF.                                    
      @965    PRYEAR2                  N4PF.                                    
      @969    PRYEAR3                  N4PF.                                    
      @973    PRYEAR4                  N4PF.                                    
      @977    PRYEAR5                  N4PF.                                    
      @981    PRYEAR6                  N4PF.                                    
      @985    PRYEAR7                  N4PF.                                    
      @989    PRYEAR8                  N4PF.                                    
      @993    PRYEAR9                  N4PF.                                    
      @997    PRYEAR10                 N4PF.                                    
      @1001   PRYEAR11                 N4PF.                                    
      @1005   PRYEAR12                 N4PF.                                    
      @1009   PRYEAR13                 N4PF.                                    
      @1013   PRYEAR14                 N4PF.                                    
      @1017   PRYEAR15                 N4PF.                                    
      @1021   PRYEAR16                 N4PF.                                    
      @1025   PRYEAR17                 N4PF.                                    
      @1029   PRYEAR18                 N4PF.                                    
      @1033   PRYEAR19                 N4PF.                                    
      @1037   PRYEAR20                 N4PF.                                    
      @1041   PRYEAR21                 N4PF.                                    
      @1045   PRYEAR22                 N4PF.                                    
      @1049   PRYEAR23                 N4PF.                                    
      @1053   PRYEAR24                 N4PF.                                    
      @1057   PRYEAR25                 N4PF.                                    
      ;                                                                         
                                                                                
                                                                                
RUN;
