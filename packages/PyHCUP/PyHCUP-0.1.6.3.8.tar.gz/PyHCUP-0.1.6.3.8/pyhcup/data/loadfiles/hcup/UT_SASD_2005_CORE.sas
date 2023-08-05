/*******************************************************************            
*   UT_SASD_2005_CORE.SAS:                                                      
*      THE SAS CODE SHOWN BELOW WILL LOAD THE ASCII                             
*      OUTPATIENT CORE FILE INTO SAS                                            
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
DATA UT_SASDC_2005_CORE;                                                        
INFILE 'UT_SASD_2005_CORE.ASC' LRECL = 460;                                     
                                                                                
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
                                                                                
  APG1                       LENGTH=3                                           
  LABEL="Ambulatory Patient Group 1 (as received from data source)"             
                                                                                
  APG2                       LENGTH=3                                           
  LABEL="Ambulatory Patient Group 2 (as received from data source)"             
                                                                                
  APG3                       LENGTH=3                                           
  LABEL="Ambulatory Patient Group 3 (as received from data source)"             
                                                                                
  APG4                       LENGTH=3                                           
  LABEL="Ambulatory Patient Group 4 (as received from data source)"             
                                                                                
  APG5                       LENGTH=3                                           
  LABEL="Ambulatory Patient Group 5 (as received from data source)"             
                                                                                
  APG6                       LENGTH=3                                           
  LABEL="Ambulatory Patient Group 6 (as received from data source)"             
                                                                                
  APGCAT1                    LENGTH=3                                           
  LABEL="Ambulatory Patient Group Category 1 (as received from data source)"    
                                                                                
  APGCAT2                    LENGTH=3                                           
  LABEL="Ambulatory Patient Group Category 2 (as received from data source)"    
                                                                                
  APGCAT3                    LENGTH=3                                           
  LABEL="Ambulatory Patient Group Category 3 (as received from data source)"    
                                                                                
  APGCAT4                    LENGTH=3                                           
  LABEL="Ambulatory Patient Group Category 4 (as received from data source)"    
                                                                                
  APGCAT5                    LENGTH=3                                           
  LABEL="Ambulatory Patient Group Category 5 (as received from data source)"    
                                                                                
  APGCAT6                    LENGTH=3                                           
  LABEL="Ambulatory Patient Group Category 6 (as received from data source)"    
                                                                                
  APGTYPE1                   LENGTH=3                                           
  LABEL="Ambulatory Patient Group Type 1 (as received from data source)"        
                                                                                
  APGTYPE2                   LENGTH=3                                           
  LABEL="Ambulatory Patient Group Type 2 (as received from data source)"        
                                                                                
  APGTYPE3                   LENGTH=3                                           
  LABEL="Ambulatory Patient Group Type 3 (as received from data source)"        
                                                                                
  APGTYPE4                   LENGTH=3                                           
  LABEL="Ambulatory Patient Group Type 4 (as received from data source)"        
                                                                                
  APGTYPE5                   LENGTH=3                                           
  LABEL="Ambulatory Patient Group Type 5 (as received from data source)"        
                                                                                
  APGTYPE6                   LENGTH=3                                           
  LABEL="Ambulatory Patient Group Type 6 (as received from data source)"        
                                                                                
  ASOURCE                    LENGTH=3                                           
  LABEL="Admission source (uniform)"                                            
                                                                                
  ASOURCE_X                  LENGTH=$1                                          
  LABEL="Admission source (as received from source)"                            
                                                                                
  ASOURCEUB92                LENGTH=$1                                          
  LABEL="Admission source (UB-92 standard coding)"                              
                                                                                
  AWEEKEND                   LENGTH=3                                           
  LABEL="Admission day is a weekend"                                            
                                                                                
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
                                                                                
  ECODE1                     LENGTH=$5                                          
  LABEL="E code 1"                                                              
                                                                                
  ECODE2                     LENGTH=$5                                          
  LABEL="E code 2"                                                              
                                                                                
  ECODE3                     LENGTH=$5                                          
  LABEL="E code 3"                                                              
                                                                                
  ECODE4                     LENGTH=$5                                          
  LABEL="E code 4"                                                              
                                                                                
  E_CCS1                     LENGTH=3                                           
  LABEL="CCS: E Code 1"                                                         
                                                                                
  E_CCS2                     LENGTH=3                                           
  LABEL="CCS: E Code 2"                                                         
                                                                                
  E_CCS3                     LENGTH=3                                           
  LABEL="CCS: E Code 3"                                                         
                                                                                
  E_CCS4                     LENGTH=3                                           
  LABEL="CCS: E Code 4"                                                         
                                                                                
  FEMALE                     LENGTH=3                                           
  LABEL="Indicator of sex"                                                      
                                                                                
  HCUP_AS                    LENGTH=3                                           
  LABEL="HCUP Ambulatory Surgery service indicator"                             
                                                                                
  HCUP_ED                    LENGTH=3                                           
  LABEL="HCUP Emergency Department service indicator"                           
                                                                                
  HCUP_OS                    LENGTH=3                                           
  LABEL="HCUP Observation Stay service indicator"                               
                                                                                
  HOSPST                     LENGTH=$2                                          
  LABEL="Hospital state postal code"                                            
                                                                                
  LOS                        LENGTH=4                                           
  LABEL="Length of stay (cleaned)"                                              
                                                                                
  LOS_X                      LENGTH=4                                           
  LABEL="Length of stay (as received from source)"                              
                                                                                
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
                                                                                
  PRDAY1                     LENGTH=4                                           
  LABEL="Number of days from admission to PR1"                                  
                                                                                
  PSTATE                     LENGTH=$2                                          
  LABEL="Patient State postal code"                                             
                                                                                
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
                                                                                
  PRYEAR1                    LENGTH=3                                           
  LABEL="Year of procedure 1"                                                   
  ;                                                                             
                                                                                
                                                                                
*** Input the variables from the ASCII file ***;                                
INPUT                                                                           
      @1      KEY                      14.                                      
      @15     AGE                      N3PF.                                    
      @18     AGEDAY                   N3PF.                                    
      @21     AGEMONTH                 N3PF.                                    
      @24     AMONTH                   N2PF.                                    
      @26     APG1                     N4PF.                                    
      @30     APG2                     N4PF.                                    
      @34     APG3                     N4PF.                                    
      @38     APG4                     N4PF.                                    
      @42     APG5                     N4PF.                                    
      @46     APG6                     N4PF.                                    
      @50     APGCAT1                  N3PF.                                    
      @53     APGCAT2                  N3PF.                                    
      @56     APGCAT3                  N3PF.                                    
      @59     APGCAT4                  N3PF.                                    
      @62     APGCAT5                  N3PF.                                    
      @65     APGCAT6                  N3PF.                                    
      @68     APGTYPE1                 N3PF.                                    
      @71     APGTYPE2                 N3PF.                                    
      @74     APGTYPE3                 N3PF.                                    
      @77     APGTYPE4                 N3PF.                                    
      @80     APGTYPE5                 N3PF.                                    
      @83     APGTYPE6                 N3PF.                                    
      @86     ASOURCE                  N2PF.                                    
      @88     ASOURCE_X                $CHAR1.                                  
      @89     ASOURCEUB92              $CHAR1.                                  
      @90     AWEEKEND                 N2PF.                                    
      @92     CPT1                     $CHAR5.                                  
      @97     CPT2                     $CHAR5.                                  
      @102    CPT3                     $CHAR5.                                  
      @107    CPT4                     $CHAR5.                                  
      @112    CPT5                     $CHAR5.                                  
      @117    CPT6                     $CHAR5.                                  
      @122    CPTM1_1                  $CHAR2.                                  
      @124    CPTM1_2                  $CHAR2.                                  
      @126    CPTM1_3                  $CHAR2.                                  
      @128    CPTM1_4                  $CHAR2.                                  
      @130    CPTM1_5                  $CHAR2.                                  
      @132    CPTM1_6                  $CHAR2.                                  
      @134    CPTM2_1                  $CHAR2.                                  
      @136    CPTM2_2                  $CHAR2.                                  
      @138    CPTM2_3                  $CHAR2.                                  
      @140    CPTM2_4                  $CHAR2.                                  
      @142    CPTM2_5                  $CHAR2.                                  
      @144    CPTM2_6                  $CHAR2.                                  
      @146    DIED                     N2PF.                                    
      @148    DISP_X                   $CHAR2.                                  
      @150    DISPUB92                 N2PF.                                    
      @152    DISPUNIFORM              N2PF.                                    
      @154    DQTR                     N2PF.                                    
      @156    DSHOSPID                 $CHAR13.                                 
      @169    DX1                      $CHAR5.                                  
      @174    DX2                      $CHAR5.                                  
      @179    DX3                      $CHAR5.                                  
      @184    DX4                      $CHAR5.                                  
      @189    DX5                      $CHAR5.                                  
      @194    DX6                      $CHAR5.                                  
      @199    DX7                      $CHAR5.                                  
      @204    DX8                      $CHAR5.                                  
      @209    DX9                      $CHAR5.                                  
      @214    DXCCS1                   N4PF.                                    
      @218    DXCCS2                   N4PF.                                    
      @222    DXCCS3                   N4PF.                                    
      @226    DXCCS4                   N4PF.                                    
      @230    DXCCS5                   N4PF.                                    
      @234    DXCCS6                   N4PF.                                    
      @238    DXCCS7                   N4PF.                                    
      @242    DXCCS8                   N4PF.                                    
      @246    DXCCS9                   N4PF.                                    
      @250    ECODE1                   $CHAR5.                                  
      @255    ECODE2                   $CHAR5.                                  
      @260    ECODE3                   $CHAR5.                                  
      @265    ECODE4                   $CHAR5.                                  
      @270    E_CCS1                   N4PF.                                    
      @274    E_CCS2                   N4PF.                                    
      @278    E_CCS3                   N4PF.                                    
      @282    E_CCS4                   N4PF.                                    
      @286    FEMALE                   N2PF.                                    
      @288    HCUP_AS                  N2PF.                                    
      @290    HCUP_ED                  N2PF.                                    
      @292    HCUP_OS                  N2PF.                                    
      @294    HOSPST                   $CHAR2.                                  
      @296    LOS                      N5PF.                                    
      @301    LOS_X                    N6PF.                                    
      @307    MEDINCSTQ                N2PF.                                    
      @309    NCPT                     N3PF.                                    
      @312    NDX                      N2PF.                                    
      @314    NECODE                   N2PF.                                    
      @316    NEOMAT                   N2PF.                                    
      @318    NPR                      N2PF.                                    
      @320    PAY1                     N2PF.                                    
      @322    PAY2                     N2PF.                                    
      @324    PAY1_X                   $CHAR2.                                  
      @326    PAY2_X                   $CHAR2.                                  
      @328    PAY3_X                   $CHAR2.                                  
      @330    PL_CBSA                  N3PF.                                    
      @333    PL_MSA1993               N3PF.                                    
      @336    PL_NHCS2006              N2PF.                                    
      @338    PL_RUCA10_2005           N2PF.                                    
      @340    PL_RUCA2005              N4P1F.                                   
      @344    PL_RUCA4_2005            N2PF.                                    
      @346    PL_RUCC2003              N2PF.                                    
      @348    PL_UIC2003               N2PF.                                    
      @350    PL_UR_CAT4               N2PF.                                    
      @352    PL_UR_CAT5               N2PF.                                    
      @354    PR1                      $CHAR4.                                  
      @358    PR2                      $CHAR4.                                  
      @362    PR3                      $CHAR4.                                  
      @366    PR4                      $CHAR4.                                  
      @370    PR5                      $CHAR4.                                  
      @374    PR6                      $CHAR4.                                  
      @378    PRCCS1                   N3PF.                                    
      @381    PRCCS2                   N3PF.                                    
      @384    PRCCS3                   N3PF.                                    
      @387    PRCCS4                   N3PF.                                    
      @390    PRCCS5                   N3PF.                                    
      @393    PRCCS6                   N3PF.                                    
      @396    PRDAY1                   N5PF.                                    
      @401    PSTATE                   $CHAR2.                                  
      @403    STATE_AS                 N2PF.                                    
      @405    STATE_ED                 N2PF.                                    
      @407    STATE_OS                 N2PF.                                    
      @409    TOTCHG                   N10PF.                                   
      @419    TOTCHG_X                 N15P2F.                                  
      @434    YEAR                     N4PF.                                    
      @438    ZIP                      $CHAR5.                                  
      @443    AYEAR                    N4PF.                                    
      @447    DMONTH                   N2PF.                                    
      @449    BMONTH                   N2PF.                                    
      @451    BYEAR                    N4PF.                                    
      @455    PRMONTH1                 N2PF.                                    
      @457    PRYEAR1                  N4PF.                                    
      ;                                                                         
                                                                                
                                                                                
RUN;
