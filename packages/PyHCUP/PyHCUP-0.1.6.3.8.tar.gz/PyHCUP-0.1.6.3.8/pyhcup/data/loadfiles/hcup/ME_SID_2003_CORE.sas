/*******************************************************************            
*   ME_SID_2003_CORE.SAS:                                                       
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
DATA ME_SIDC_2003_CORE;                                                         
INFILE 'ME_SID_2003_CORE.ASC' LRECL = 426;                                      
                                                                                
*** Variable attribute ***;                                                     
ATTRIB                                                                          
  KEY                LENGTH=8          FORMAT=Z14.                              
  LABEL="HCUP record identifier"                                                
                                                                                
  ADRG               LENGTH=3                                                   
  LABEL="All Patient Refined DRG"                                               
                                                                                
  AGE                LENGTH=3                                                   
  LABEL="Age in years at admission"                                             
                                                                                
  AGEDAY             LENGTH=3                                                   
  LABEL="Age in days (when age < 1 year)"                                       
                                                                                
  AGEMONTH           LENGTH=3                                                   
  LABEL="Age in months (when age < 11 years)"                                   
                                                                                
  AMDC               LENGTH=3                                                   
  LABEL="All Patient Refined MDC"                                               
                                                                                
  AMONTH             LENGTH=3                                                   
  LABEL="Admission month"                                                       
                                                                                
  ASOURCE            LENGTH=3                                                   
  LABEL="Admission source (uniform)"                                            
                                                                                
  ASOURCE_X          LENGTH=$1                                                  
  LABEL="Admission source (as received from source)"                            
                                                                                
  ASOURCEUB92        LENGTH=$1                                                  
  LABEL="Admission source (UB-92 standard coding)"                              
                                                                                
  ATYPE              LENGTH=3                                                   
  LABEL="Admission type"                                                        
                                                                                
  AWEEKEND           LENGTH=3                                                   
  LABEL="Admission day is a weekend"                                            
                                                                                
  DIED               LENGTH=3                                                   
  LABEL="Died during hospitalization"                                           
                                                                                
  DISP_X             LENGTH=$2                                                  
  LABEL="Disposition of patient (as received from source)"                      
                                                                                
  DISPUB92           LENGTH=3                                                   
  LABEL="Disposition of patient (UB-92 standard coding)"                        
                                                                                
  DISPUNIFORM        LENGTH=3                                                   
  LABEL="Disposition of patient (uniform)"                                      
                                                                                
  DQTR               LENGTH=3                                                   
  LABEL="Discharge quarter"                                                     
                                                                                
  DRG                LENGTH=3                                                   
  LABEL="DRG in effect on discharge date"                                       
                                                                                
  DRG18              LENGTH=3                                                   
  LABEL="DRG, version 18"                                                       
                                                                                
  DRGVER             LENGTH=3                                                   
  LABEL="DRG grouper version used on discharge date"                            
                                                                                
  DSHOSPID           LENGTH=$13                                                 
  LABEL="Data source hospital identifier"                                       
                                                                                
  DX1                LENGTH=$5                                                  
  LABEL="Principal diagnosis"                                                   
                                                                                
  DX2                LENGTH=$5                                                  
  LABEL="Diagnosis 2"                                                           
                                                                                
  DX3                LENGTH=$5                                                  
  LABEL="Diagnosis 3"                                                           
                                                                                
  DX4                LENGTH=$5                                                  
  LABEL="Diagnosis 4"                                                           
                                                                                
  DX5                LENGTH=$5                                                  
  LABEL="Diagnosis 5"                                                           
                                                                                
  DX6                LENGTH=$5                                                  
  LABEL="Diagnosis 6"                                                           
                                                                                
  DX7                LENGTH=$5                                                  
  LABEL="Diagnosis 7"                                                           
                                                                                
  DX8                LENGTH=$5                                                  
  LABEL="Diagnosis 8"                                                           
                                                                                
  DX9                LENGTH=$5                                                  
  LABEL="Diagnosis 9"                                                           
                                                                                
  DX10               LENGTH=$5                                                  
  LABEL="Diagnosis 10"                                                          
                                                                                
  DXCCS1             LENGTH=4                                                   
  LABEL="CCS: principal diagnosis"                                              
                                                                                
  DXCCS2             LENGTH=4                                                   
  LABEL="CCS: diagnosis 2"                                                      
                                                                                
  DXCCS3             LENGTH=4                                                   
  LABEL="CCS: diagnosis 3"                                                      
                                                                                
  DXCCS4             LENGTH=4                                                   
  LABEL="CCS: diagnosis 4"                                                      
                                                                                
  DXCCS5             LENGTH=4                                                   
  LABEL="CCS: diagnosis 5"                                                      
                                                                                
  DXCCS6             LENGTH=4                                                   
  LABEL="CCS: diagnosis 6"                                                      
                                                                                
  DXCCS7             LENGTH=4                                                   
  LABEL="CCS: diagnosis 7"                                                      
                                                                                
  DXCCS8             LENGTH=4                                                   
  LABEL="CCS: diagnosis 8"                                                      
                                                                                
  DXCCS9             LENGTH=4                                                   
  LABEL="CCS: diagnosis 9"                                                      
                                                                                
  DXCCS10            LENGTH=4                                                   
  LABEL="CCS: diagnosis 10"                                                     
                                                                                
  ECODE1             LENGTH=$5                                                  
  LABEL="E code 1"                                                              
                                                                                
  ECODE2             LENGTH=$5                                                  
  LABEL="E code 2"                                                              
                                                                                
  ECODE3             LENGTH=$5                                                  
  LABEL="E code 3"                                                              
                                                                                
  ECODE4             LENGTH=$5                                                  
  LABEL="E code 4"                                                              
                                                                                
  ECODE5             LENGTH=$5                                                  
  LABEL="E code 5"                                                              
                                                                                
  E_CCS1             LENGTH=3                                                   
  LABEL="CCS: E Code 1"                                                         
                                                                                
  E_CCS2             LENGTH=3                                                   
  LABEL="CCS: E Code 2"                                                         
                                                                                
  E_CCS3             LENGTH=3                                                   
  LABEL="CCS: E Code 3"                                                         
                                                                                
  E_CCS4             LENGTH=3                                                   
  LABEL="CCS: E Code 4"                                                         
                                                                                
  E_CCS5             LENGTH=3                                                   
  LABEL="CCS: E Code 5"                                                         
                                                                                
  FEMALE             LENGTH=3                                                   
  LABEL="Indicator of sex"                                                      
                                                                                
  HOSPST             LENGTH=$2                                                  
  LABEL="Hospital state postal code"                                            
                                                                                
  LOS                LENGTH=4                                                   
  LABEL="Length of stay (cleaned)"                                              
                                                                                
  LOS_X              LENGTH=4                                                   
  LABEL="Length of stay (as received from source)"                              
                                                                                
  MDC                LENGTH=3                                                   
  LABEL="MDC in effect on discharge date"                                       
                                                                                
  MDC18              LENGTH=3                                                   
  LABEL="MDC, version 18"                                                       
                                                                                
  MDSPEC1            LENGTH=$2                                                  
  LABEL="Physician 1 specialty (as received from source)"                       
                                                                                
  MDSPEC2            LENGTH=$2                                                  
  LABEL="Physician 2 specialty (as received from source)"                       
                                                                                
  MRN_R              LENGTH=5                                                   
  LABEL="Medical record number (re-identified)"                                 
                                                                                
  NDX                LENGTH=3                                                   
  LABEL="Number of diagnoses on this record"                                    
                                                                                
  NECODE             LENGTH=3                                                   
  LABEL="Number of E codes on this record"                                      
                                                                                
  NEOMAT             LENGTH=3                                                   
  LABEL="Neonatal and/or maternal DX and/or PR"                                 
                                                                                
  NPR                LENGTH=3                                                   
  LABEL="Number of procedures on this record"                                   
                                                                                
  PAY1               LENGTH=3                                                   
  LABEL="Primary expected payer (uniform)"                                      
                                                                                
  PAY2               LENGTH=3                                                   
  LABEL="Secondary expected payer (uniform)"                                    
                                                                                
  PAY1_X             LENGTH=$2                                                  
  LABEL="Primary expected payer (as received from source)"                      
                                                                                
  PAY2_X             LENGTH=$2                                                  
  LABEL="Secondary expected payer (as received from source)"                    
                                                                                
  PAY3_X             LENGTH=$2                                                  
  LABEL="Tertiary expected payer (as received from source)"                     
                                                                                
  PAYER1_X           LENGTH=$23                                                 
  LABEL="Primary expected payer plan identifier (as received from source)"      
                                                                                
  PL_CBSA            LENGTH=3                                                   
  LABEL="Patient location: Core Based Statistical Area (CBSA)"                  
                                                                                
  PL_MSA1993         LENGTH=3                                                   
  LABEL="Patient location: Metropolitan Statistical Area (MSA), 1993"           
                                                                                
  PL_RUCA4           LENGTH=3                                                   
  LABEL="Patient location: Rural-Urban Commuting Area (RUCA) Codes, four levels"
                                                                                
  PL_UIC2003         LENGTH=3                                                   
  LABEL="Patient location: Urban Influence Codes, 2003"                         
                                                                                
  PL_UR_CAT4         LENGTH=3                                                   
  LABEL="Patient Location: Urban-Rural 4 Categories"                            
                                                                                
  PL_UR_CAT5         LENGTH=3                                                   
  LABEL="Patient Location: Urban-Rural 5 Categories"                            
                                                                                
  PR1                LENGTH=$4                                                  
  LABEL="Principal procedure"                                                   
                                                                                
  PR2                LENGTH=$4                                                  
  LABEL="Procedure 2"                                                           
                                                                                
  PR3                LENGTH=$4                                                  
  LABEL="Procedure 3"                                                           
                                                                                
  PR4                LENGTH=$4                                                  
  LABEL="Procedure 4"                                                           
                                                                                
  PR5                LENGTH=$4                                                  
  LABEL="Procedure 5"                                                           
                                                                                
  PR6                LENGTH=$4                                                  
  LABEL="Procedure 6"                                                           
                                                                                
  PRCCS1             LENGTH=3                                                   
  LABEL="CCS: principal procedure"                                              
                                                                                
  PRCCS2             LENGTH=3                                                   
  LABEL="CCS: procedure 2"                                                      
                                                                                
  PRCCS3             LENGTH=3                                                   
  LABEL="CCS: procedure 3"                                                      
                                                                                
  PRCCS4             LENGTH=3                                                   
  LABEL="CCS: procedure 4"                                                      
                                                                                
  PRCCS5             LENGTH=3                                                   
  LABEL="CCS: procedure 5"                                                      
                                                                                
  PRCCS6             LENGTH=3                                                   
  LABEL="CCS: procedure 6"                                                      
                                                                                
  PRDAY1             LENGTH=4                                                   
  LABEL="Number of days from admission to PR1"                                  
                                                                                
  PRDAY2             LENGTH=4                                                   
  LABEL="Number of days from admission to PR2"                                  
                                                                                
  PRDAY3             LENGTH=4                                                   
  LABEL="Number of days from admission to PR3"                                  
                                                                                
  PRDAY4             LENGTH=4                                                   
  LABEL="Number of days from admission to PR4"                                  
                                                                                
  PRDAY5             LENGTH=4                                                   
  LABEL="Number of days from admission to PR5"                                  
                                                                                
  PRDAY6             LENGTH=4                                                   
  LABEL="Number of days from admission to PR6"                                  
                                                                                
  PSTATE             LENGTH=$2                                                  
  LABEL="Patient State postal code"                                             
                                                                                
  PSTCO              LENGTH=4                                                   
  LABEL="Patient state/county FIPS code"                                        
                                                                                
  PSTCO2             LENGTH=4                                                   
  LABEL="Patient state/county FIPS code, possibly derived from ZIP Code"        
                                                                                
  YEAR               LENGTH=3                                                   
  LABEL="Calendar year"                                                         
                                                                                
  ZIP_S              LENGTH=$5                                                  
  LABEL="Patient ZIP Code (synthetic)"                                          
                                                                                
  AYEAR              LENGTH=3                                                   
  LABEL="Admission year"                                                        
                                                                                
  DMONTH             LENGTH=3                                                   
  LABEL="Discharge month"                                                       
                                                                                
  PRMONTH1           LENGTH=3                                                   
  LABEL="Month of procedure 1"                                                  
                                                                                
  PRMONTH2           LENGTH=3                                                   
  LABEL="Month of procedure 2"                                                  
                                                                                
  PRMONTH3           LENGTH=3                                                   
  LABEL="Month of procedure 3"                                                  
                                                                                
  PRMONTH4           LENGTH=3                                                   
  LABEL="Month of procedure 4"                                                  
                                                                                
  PRMONTH5           LENGTH=3                                                   
  LABEL="Month of procedure 5"                                                  
                                                                                
  PRMONTH6           LENGTH=3                                                   
  LABEL="Month of procedure 6"                                                  
                                                                                
  PRYEAR1            LENGTH=3                                                   
  LABEL="Year of procedure 1"                                                   
                                                                                
  PRYEAR2            LENGTH=3                                                   
  LABEL="Year of procedure 2"                                                   
                                                                                
  PRYEAR3            LENGTH=3                                                   
  LABEL="Year of procedure 3"                                                   
                                                                                
  PRYEAR4            LENGTH=3                                                   
  LABEL="Year of procedure 4"                                                   
                                                                                
  PRYEAR5            LENGTH=3                                                   
  LABEL="Year of procedure 5"                                                   
                                                                                
  PRYEAR6            LENGTH=3                                                   
  LABEL="Year of procedure 6"                                                   
  ;                                                                             
                                                                                
                                                                                
*** Input the variables from the ASCII file ***;                                
INPUT                                                                           
      @1      KEY                 14.                                           
      @15     ADRG                N3PF.                                         
      @18     AGE                 N3PF.                                         
      @21     AGEDAY              N3PF.                                         
      @24     AGEMONTH            N3PF.                                         
      @27     AMDC                N2PF.                                         
      @29     AMONTH              N2PF.                                         
      @31     ASOURCE             N2PF.                                         
      @33     ASOURCE_X           $CHAR1.                                       
      @34     ASOURCEUB92         $CHAR1.                                       
      @35     ATYPE               N2PF.                                         
      @37     AWEEKEND            N2PF.                                         
      @39     DIED                N2PF.                                         
      @41     DISP_X              $CHAR2.                                       
      @43     DISPUB92            N2PF.                                         
      @45     DISPUNIFORM         N2PF.                                         
      @47     DQTR                N2PF.                                         
      @49     DRG                 N3PF.                                         
      @52     DRG18               N3PF.                                         
      @55     DRGVER              N2PF.                                         
      @57     DSHOSPID            $CHAR13.                                      
      @70     DX1                 $CHAR5.                                       
      @75     DX2                 $CHAR5.                                       
      @80     DX3                 $CHAR5.                                       
      @85     DX4                 $CHAR5.                                       
      @90     DX5                 $CHAR5.                                       
      @95     DX6                 $CHAR5.                                       
      @100    DX7                 $CHAR5.                                       
      @105    DX8                 $CHAR5.                                       
      @110    DX9                 $CHAR5.                                       
      @115    DX10                $CHAR5.                                       
      @120    DXCCS1              N4PF.                                         
      @124    DXCCS2              N4PF.                                         
      @128    DXCCS3              N4PF.                                         
      @132    DXCCS4              N4PF.                                         
      @136    DXCCS5              N4PF.                                         
      @140    DXCCS6              N4PF.                                         
      @144    DXCCS7              N4PF.                                         
      @148    DXCCS8              N4PF.                                         
      @152    DXCCS9              N4PF.                                         
      @156    DXCCS10             N4PF.                                         
      @160    ECODE1              $CHAR5.                                       
      @165    ECODE2              $CHAR5.                                       
      @170    ECODE3              $CHAR5.                                       
      @175    ECODE4              $CHAR5.                                       
      @180    ECODE5              $CHAR5.                                       
      @185    E_CCS1              N4PF.                                         
      @189    E_CCS2              N4PF.                                         
      @193    E_CCS3              N4PF.                                         
      @197    E_CCS4              N4PF.                                         
      @201    E_CCS5              N4PF.                                         
      @205    FEMALE              N2PF.                                         
      @207    HOSPST              $CHAR2.                                       
      @209    LOS                 N5PF.                                         
      @214    LOS_X               N6PF.                                         
      @220    MDC                 N2PF.                                         
      @222    MDC18               N2PF.                                         
      @224    MDSPEC1             $CHAR2.                                       
      @226    MDSPEC2             $CHAR2.                                       
      @228    MRN_R               N9PF.                                         
      @237    NDX                 N2PF.                                         
      @239    NECODE              N2PF.                                         
      @241    NEOMAT              N2PF.                                         
      @243    NPR                 N2PF.                                         
      @245    PAY1                N2PF.                                         
      @247    PAY2                N2PF.                                         
      @249    PAY1_X              $CHAR2.                                       
      @251    PAY2_X              $CHAR2.                                       
      @253    PAY3_X              $CHAR2.                                       
      @255    PAYER1_X            $CHAR23.                                      
      @278    PL_CBSA             N3PF.                                         
      @281    PL_MSA1993          N3PF.                                         
      @284    PL_RUCA4            N2PF.                                         
      @286    PL_UIC2003          N2PF.                                         
      @288    PL_UR_CAT4          N2PF.                                         
      @290    PL_UR_CAT5          N2PF.                                         
      @292    PR1                 $CHAR4.                                       
      @296    PR2                 $CHAR4.                                       
      @300    PR3                 $CHAR4.                                       
      @304    PR4                 $CHAR4.                                       
      @308    PR5                 $CHAR4.                                       
      @312    PR6                 $CHAR4.                                       
      @316    PRCCS1              N3PF.                                         
      @319    PRCCS2              N3PF.                                         
      @322    PRCCS3              N3PF.                                         
      @325    PRCCS4              N3PF.                                         
      @328    PRCCS5              N3PF.                                         
      @331    PRCCS6              N3PF.                                         
      @334    PRDAY1              N5PF.                                         
      @339    PRDAY2              N5PF.                                         
      @344    PRDAY3              N5PF.                                         
      @349    PRDAY4              N5PF.                                         
      @354    PRDAY5              N5PF.                                         
      @359    PRDAY6              N5PF.                                         
      @364    PSTATE              $CHAR2.                                       
      @366    PSTCO               N5PF.                                         
      @371    PSTCO2              N5PF.                                         
      @376    YEAR                N4PF.                                         
      @380    ZIP_S               $CHAR5.                                       
      @385    AYEAR               N4PF.                                         
      @389    DMONTH              N2PF.                                         
      @391    PRMONTH1            N2PF.                                         
      @393    PRMONTH2            N2PF.                                         
      @395    PRMONTH3            N2PF.                                         
      @397    PRMONTH4            N2PF.                                         
      @399    PRMONTH5            N2PF.                                         
      @401    PRMONTH6            N2PF.                                         
      @403    PRYEAR1             N4PF.                                         
      @407    PRYEAR2             N4PF.                                         
      @411    PRYEAR3             N4PF.                                         
      @415    PRYEAR4             N4PF.                                         
      @419    PRYEAR5             N4PF.                                         
      @423    PRYEAR6             N4PF.                                         
      ;                                                                         
                                                                                
                                                                                
RUN;
