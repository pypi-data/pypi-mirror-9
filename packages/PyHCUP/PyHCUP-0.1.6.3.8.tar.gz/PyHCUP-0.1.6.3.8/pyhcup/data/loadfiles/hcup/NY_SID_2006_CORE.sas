/*******************************************************************            
*   NY_SID_2006_CORE.SAS:                                                       
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
DATA NY_SIDC_2006_CORE;                                                         
INFILE 'NY_SID_2006_CORE.ASC' LRECL = 758;                                      
                                                                                
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
                                                                                
  AHOUR                      LENGTH=3                 FORMAT=Z4.                
  LABEL="Admission Hour"                                                        
                                                                                
  AMONTH                     LENGTH=3                                           
  LABEL="Admission month"                                                       
                                                                                
  ANESTH                     LENGTH=3                                           
  LABEL="Method of anesthesia"                                                  
                                                                                
  ASCHED                     LENGTH=3                                           
  LABEL="Admission scheduled vs. unscheduled"                                   
                                                                                
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
                                                                                
  BLOOD                      LENGTH=4                                           
  LABEL="Pints of blood furnished to the patient"                               
                                                                                
  BWT                        LENGTH=4                                           
  LABEL="Birth weight in grams"                                                 
                                                                                
  DHOUR                      LENGTH=3                 FORMAT=Z4.                
  LABEL="Discharge Hour"                                                        
                                                                                
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
                                                                                
  DXATADMIT1                 LENGTH=3                                           
  LABEL="Principal diagnosis present at admission"                              
                                                                                
  DXATADMIT2                 LENGTH=3                                           
  LABEL="Diagnosis 2 present at admission"                                      
                                                                                
  DXATADMIT3                 LENGTH=3                                           
  LABEL="Diagnosis 3 present at admission"                                      
                                                                                
  DXATADMIT4                 LENGTH=3                                           
  LABEL="Diagnosis 4 present at admission"                                      
                                                                                
  DXATADMIT5                 LENGTH=3                                           
  LABEL="Diagnosis 5 present at admission"                                      
                                                                                
  DXATADMIT6                 LENGTH=3                                           
  LABEL="Diagnosis 6 present at admission"                                      
                                                                                
  DXATADMIT7                 LENGTH=3                                           
  LABEL="Diagnosis 7 present at admission"                                      
                                                                                
  DXATADMIT8                 LENGTH=3                                           
  LABEL="Diagnosis 8 present at admission"                                      
                                                                                
  DXATADMIT9                 LENGTH=3                                           
  LABEL="Diagnosis 9 present at admission"                                      
                                                                                
  DXATADMIT10                LENGTH=3                                           
  LABEL="Diagnosis 10 present at admission"                                     
                                                                                
  DXATADMIT11                LENGTH=3                                           
  LABEL="Diagnosis 11 present at admission"                                     
                                                                                
  DXATADMIT12                LENGTH=3                                           
  LABEL="Diagnosis 12 present at admission"                                     
                                                                                
  DXATADMIT13                LENGTH=3                                           
  LABEL="Diagnosis 13 present at admission"                                     
                                                                                
  DXATADMIT14                LENGTH=3                                           
  LABEL="Diagnosis 14 present at admission"                                     
                                                                                
  DXATADMIT15                LENGTH=3                                           
  LABEL="Diagnosis 15 present at admission"                                     
                                                                                
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
                                                                                
  HCUP_ED                    LENGTH=3                                           
  LABEL="HCUP Emergency Department service indicator"                           
                                                                                
  HCUP_OS                    LENGTH=3                                           
  LABEL="HCUP Observation Stay service indicator"                               
                                                                                
  HISPANIC_X                 LENGTH=$1                                          
  LABEL="Hispanic ethnicity (as received from source)"                          
                                                                                
  Homeless                   LENGTH=3                                           
  LABEL="Indicator that patient is homeless"                                    
                                                                                
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
                                                                                
  MDNUM1_R                   LENGTH=5                                           
  LABEL="Physician 1 number (re-identified)"                                    
                                                                                
  MDNUM2_R                   LENGTH=5                                           
  LABEL="Physician 2 number (re-identified)"                                    
                                                                                
  MEDINCSTQ                  LENGTH=3                                           
  LABEL="Median household income state quartile for patient ZIP Code"           
                                                                                
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
                                                                                
  PAY1_X                     LENGTH=$2                                          
  LABEL="Primary expected payer (as received from source)"                      
                                                                                
  PAY2_X                     LENGTH=$2                                          
  LABEL="Secondary expected payer (as received from source)"                    
                                                                                
  PAY3_X                     LENGTH=$2                                          
  LABEL="Tertiary expected payer (as received from source)"                     
                                                                                
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
                                                                                
  RACE_X                     LENGTH=$2                                          
  LABEL="Race (as received from source)"                                        
                                                                                
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
  ;                                                                             
                                                                                
                                                                                
*** Input the variables from the ASCII file ***;                                
INPUT                                                                           
      @1      KEY                      14.                                      
      @15     AGE                      N3PF.                                    
      @18     AGEDAY                   N3PF.                                    
      @21     AGEMONTH                 N3PF.                                    
      @24     AHOUR                    N4PF.                                    
      @28     AMONTH                   N2PF.                                    
      @30     ANESTH                   N3PF.                                    
      @33     ASCHED                   N2PF.                                    
      @35     ASOURCE                  N2PF.                                    
      @37     ASOURCE_X                $CHAR1.                                  
      @38     ASOURCEUB92              $CHAR1.                                  
      @39     ATYPE                    N2PF.                                    
      @41     AWEEKEND                 N2PF.                                    
      @43     BLOOD                    N6PF.                                    
      @49     BWT                      N4PF.                                    
      @53     DHOUR                    N4PF.                                    
      @57     DIED                     N2PF.                                    
      @59     DISP_X                   $CHAR2.                                  
      @61     DISPUB92                 N2PF.                                    
      @63     DISPUNIFORM              N2PF.                                    
      @65     DQTR                     N2PF.                                    
      @67     DRG                      N3PF.                                    
      @70     DRG18                    N3PF.                                    
      @73     DRG24                    N3PF.                                    
      @76     DRGVER                   N2PF.                                    
      @78     DSHOSPID                 $CHAR13.                                 
      @91     DX1                      $CHAR5.                                  
      @96     DX2                      $CHAR5.                                  
      @101    DX3                      $CHAR5.                                  
      @106    DX4                      $CHAR5.                                  
      @111    DX5                      $CHAR5.                                  
      @116    DX6                      $CHAR5.                                  
      @121    DX7                      $CHAR5.                                  
      @126    DX8                      $CHAR5.                                  
      @131    DX9                      $CHAR5.                                  
      @136    DX10                     $CHAR5.                                  
      @141    DX11                     $CHAR5.                                  
      @146    DX12                     $CHAR5.                                  
      @151    DX13                     $CHAR5.                                  
      @156    DX14                     $CHAR5.                                  
      @161    DX15                     $CHAR5.                                  
      @166    DXATADMIT1               N2PF.                                    
      @168    DXATADMIT2               N2PF.                                    
      @170    DXATADMIT3               N2PF.                                    
      @172    DXATADMIT4               N2PF.                                    
      @174    DXATADMIT5               N2PF.                                    
      @176    DXATADMIT6               N2PF.                                    
      @178    DXATADMIT7               N2PF.                                    
      @180    DXATADMIT8               N2PF.                                    
      @182    DXATADMIT9               N2PF.                                    
      @184    DXATADMIT10              N2PF.                                    
      @186    DXATADMIT11              N2PF.                                    
      @188    DXATADMIT12              N2PF.                                    
      @190    DXATADMIT13              N2PF.                                    
      @192    DXATADMIT14              N2PF.                                    
      @194    DXATADMIT15              N2PF.                                    
      @196    DXCCS1                   N4PF.                                    
      @200    DXCCS2                   N4PF.                                    
      @204    DXCCS3                   N4PF.                                    
      @208    DXCCS4                   N4PF.                                    
      @212    DXCCS5                   N4PF.                                    
      @216    DXCCS6                   N4PF.                                    
      @220    DXCCS7                   N4PF.                                    
      @224    DXCCS8                   N4PF.                                    
      @228    DXCCS9                   N4PF.                                    
      @232    DXCCS10                  N4PF.                                    
      @236    DXCCS11                  N4PF.                                    
      @240    DXCCS12                  N4PF.                                    
      @244    DXCCS13                  N4PF.                                    
      @248    DXCCS14                  N4PF.                                    
      @252    DXCCS15                  N4PF.                                    
      @256    ECODE1                   $CHAR5.                                  
      @261    ECODE2                   $CHAR5.                                  
      @266    ECODE3                   $CHAR5.                                  
      @271    ECODE4                   $CHAR5.                                  
      @276    ECODE5                   $CHAR5.                                  
      @281    ECODE6                   $CHAR5.                                  
      @286    ECODE7                   $CHAR5.                                  
      @291    ECODE8                   $CHAR5.                                  
      @296    E_CCS1                   N4PF.                                    
      @300    E_CCS2                   N4PF.                                    
      @304    E_CCS3                   N4PF.                                    
      @308    E_CCS4                   N4PF.                                    
      @312    E_CCS5                   N4PF.                                    
      @316    E_CCS6                   N4PF.                                    
      @320    E_CCS7                   N4PF.                                    
      @324    E_CCS8                   N4PF.                                    
      @328    FEMALE                   N2PF.                                    
      @330    HCUP_ED                  N2PF.                                    
      @332    HCUP_OS                  N2PF.                                    
      @334    HISPANIC_X               $CHAR1.                                  
      @335    Homeless                 N2PF.                                    
      @337    HOSPBRTH                 N3PF.                                    
      @340    HOSPST                   $CHAR2.                                  
      @342    LOS                      N5PF.                                    
      @347    LOS_X                    N6PF.                                    
      @353    MDC                      N2PF.                                    
      @355    MDC18                    N2PF.                                    
      @357    MDC24                    N2PF.                                    
      @359    MDNUM1_R                 N9PF.                                    
      @368    MDNUM2_R                 N9PF.                                    
      @377    MEDINCSTQ                N2PF.                                    
      @379    NDX                      N2PF.                                    
      @381    NECODE                   N2PF.                                    
      @383    NEOMAT                   N2PF.                                    
      @385    NPR                      N2PF.                                    
      @387    PAY1                     N2PF.                                    
      @389    PAY2                     N2PF.                                    
      @391    PAY1_X                   $CHAR2.                                  
      @393    PAY2_X                   $CHAR2.                                  
      @395    PAY3_X                   $CHAR2.                                  
      @397    PL_CBSA                  N3PF.                                    
      @400    PL_MSA1993               N3PF.                                    
      @403    PL_NHCS2006              N2PF.                                    
      @405    PL_RUCA10_2005           N2PF.                                    
      @407    PL_RUCA2005              N4P1F.                                   
      @411    PL_RUCA4_2005            N2PF.                                    
      @413    PL_RUCC2003              N2PF.                                    
      @415    PL_UIC2003               N2PF.                                    
      @417    PL_UR_CAT4               N2PF.                                    
      @419    PL_UR_CAT5               N2PF.                                    
      @421    PR1                      $CHAR4.                                  
      @425    PR2                      $CHAR4.                                  
      @429    PR3                      $CHAR4.                                  
      @433    PR4                      $CHAR4.                                  
      @437    PR5                      $CHAR4.                                  
      @441    PR6                      $CHAR4.                                  
      @445    PR7                      $CHAR4.                                  
      @449    PR8                      $CHAR4.                                  
      @453    PR9                      $CHAR4.                                  
      @457    PR10                     $CHAR4.                                  
      @461    PR11                     $CHAR4.                                  
      @465    PR12                     $CHAR4.                                  
      @469    PR13                     $CHAR4.                                  
      @473    PR14                     $CHAR4.                                  
      @477    PR15                     $CHAR4.                                  
      @481    PRCCS1                   N3PF.                                    
      @484    PRCCS2                   N3PF.                                    
      @487    PRCCS3                   N3PF.                                    
      @490    PRCCS4                   N3PF.                                    
      @493    PRCCS5                   N3PF.                                    
      @496    PRCCS6                   N3PF.                                    
      @499    PRCCS7                   N3PF.                                    
      @502    PRCCS8                   N3PF.                                    
      @505    PRCCS9                   N3PF.                                    
      @508    PRCCS10                  N3PF.                                    
      @511    PRCCS11                  N3PF.                                    
      @514    PRCCS12                  N3PF.                                    
      @517    PRCCS13                  N3PF.                                    
      @520    PRCCS14                  N3PF.                                    
      @523    PRCCS15                  N3PF.                                    
      @526    PRDAY1                   N5PF.                                    
      @531    PRDAY2                   N5PF.                                    
      @536    PRDAY3                   N5PF.                                    
      @541    PRDAY4                   N5PF.                                    
      @546    PRDAY5                   N5PF.                                    
      @551    PRDAY6                   N5PF.                                    
      @556    PRDAY7                   N5PF.                                    
      @561    PRDAY8                   N5PF.                                    
      @566    PRDAY9                   N5PF.                                    
      @571    PRDAY10                  N5PF.                                    
      @576    PRDAY11                  N5PF.                                    
      @581    PRDAY12                  N5PF.                                    
      @586    PRDAY13                  N5PF.                                    
      @591    PRDAY14                  N5PF.                                    
      @596    PRDAY15                  N5PF.                                    
      @601    PROCTYPE                 N3PF.                                    
      @604    PSTATE                   $CHAR2.                                  
      @606    PSTCO                    N5PF.                                    
      @611    PSTCO2                   N5PF.                                    
      @616    RACE                     N2PF.                                    
      @618    RACE_X                   $CHAR2.                                  
      @620    TOTCHG                   N10PF.                                   
      @630    TOTCHG_X                 N15P2F.                                  
      @645    YEAR                     N4PF.                                    
      @649    ZIPINC_QRTL              N3PF.                                    
      @652    ZIP                      $CHAR5.                                  
      @657    AYEAR                    N4PF.                                    
      @661    DMONTH                   N2PF.                                    
      @663    BMONTH                   N2PF.                                    
      @665    BYEAR                    N4PF.                                    
      @669    PRMONTH1                 N2PF.                                    
      @671    PRMONTH2                 N2PF.                                    
      @673    PRMONTH3                 N2PF.                                    
      @675    PRMONTH4                 N2PF.                                    
      @677    PRMONTH5                 N2PF.                                    
      @679    PRMONTH6                 N2PF.                                    
      @681    PRMONTH7                 N2PF.                                    
      @683    PRMONTH8                 N2PF.                                    
      @685    PRMONTH9                 N2PF.                                    
      @687    PRMONTH10                N2PF.                                    
      @689    PRMONTH11                N2PF.                                    
      @691    PRMONTH12                N2PF.                                    
      @693    PRMONTH13                N2PF.                                    
      @695    PRMONTH14                N2PF.                                    
      @697    PRMONTH15                N2PF.                                    
      @699    PRYEAR1                  N4PF.                                    
      @703    PRYEAR2                  N4PF.                                    
      @707    PRYEAR3                  N4PF.                                    
      @711    PRYEAR4                  N4PF.                                    
      @715    PRYEAR5                  N4PF.                                    
      @719    PRYEAR6                  N4PF.                                    
      @723    PRYEAR7                  N4PF.                                    
      @727    PRYEAR8                  N4PF.                                    
      @731    PRYEAR9                  N4PF.                                    
      @735    PRYEAR10                 N4PF.                                    
      @739    PRYEAR11                 N4PF.                                    
      @743    PRYEAR12                 N4PF.                                    
      @747    PRYEAR13                 N4PF.                                    
      @751    PRYEAR14                 N4PF.                                    
      @755    PRYEAR15                 N4PF.                                    
      ;                                                                         
                                                                                
                                                                                
RUN;
