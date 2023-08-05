/*******************************************************************            
*   KY_SID_2003_CORE.SAS:                                                       
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
DATA KY_SIDC_2003_CORE;                                                         
INFILE 'KY_SID_2003_CORE.ASC' LRECL = 455;                                      
                                                                                
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
                                                                                
  AMONTH             LENGTH=3                                                   
  LABEL="Admission month"                                                       
                                                                                
  ASOURCE            LENGTH=3                                                   
  LABEL="Admission source (uniform)"                                            
                                                                                
  ASOURCE_X          LENGTH=$2                                                  
  LABEL="Admission source (as received from source)"                            
                                                                                
  ASOURCEUB92        LENGTH=$1                                                  
  LABEL="Admission source (UB-92 standard coding)"                              
                                                                                
  ATYPE              LENGTH=3                                                   
  LABEL="Admission type"                                                        
                                                                                
  AWEEKEND           LENGTH=3                                                   
  LABEL="Admission day is a weekend"                                            
                                                                                
  BWT                LENGTH=4                                                   
  LABEL="Birth weight in grams"                                                 
                                                                                
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
                                                                                
  ECODE1             LENGTH=$5                                                  
  LABEL="E code 1"                                                              
                                                                                
  ECODE2             LENGTH=$5                                                  
  LABEL="E code 2"                                                              
                                                                                
  ECODE3             LENGTH=$5                                                  
  LABEL="E code 3"                                                              
                                                                                
  ECODE4             LENGTH=$5                                                  
  LABEL="E code 4"                                                              
                                                                                
  E_CCS1             LENGTH=3                                                   
  LABEL="CCS: E Code 1"                                                         
                                                                                
  E_CCS2             LENGTH=3                                                   
  LABEL="CCS: E Code 2"                                                         
                                                                                
  E_CCS3             LENGTH=3                                                   
  LABEL="CCS: E Code 3"                                                         
                                                                                
  E_CCS4             LENGTH=3                                                   
  LABEL="CCS: E Code 4"                                                         
                                                                                
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
                                                                                
  MDNUM1_R           LENGTH=5                                                   
  LABEL="Physician 1 number (re-identified)"                                    
                                                                                
  MDNUM2_R           LENGTH=5                                                   
  LABEL="Physician 2 number (re-identified)"                                    
                                                                                
  MDNUM3_R           LENGTH=5                                                   
  LABEL="Physician 3 number (re-identified)"                                    
                                                                                
  MDNUM4_R           LENGTH=5                                                   
  LABEL="Physician 4 number (re-identified)"                                    
                                                                                
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
                                                                                
  PAY1_X             LENGTH=$1                                                  
  LABEL="Primary expected payer (as received from source)"                      
                                                                                
  PAY2_X             LENGTH=$1                                                  
  LABEL="Secondary expected payer (as received from source)"                    
                                                                                
  PAY3_X             LENGTH=$1                                                  
  LABEL="Tertiary expected payer (as received from source)"                     
                                                                                
  PL_CBSA            LENGTH=3                                                   
  LABEL="Patient location: Core Based Statistical Area (CBSA)"                  
                                                                                
  PL_MSA1993         LENGTH=3                                                   
  LABEL="Patient location: Metropolitan Statistical Area (MSA), 1993"           
                                                                                
  PL_RUCA            LENGTH=4          FORMAT=4.1                               
  LABEL="Patient location: Rural-Urban Commuting Area (RUCA) Codes"             
                                                                                
  PL_RUCA10          LENGTH=3                                                   
  LABEL="Patient location: Rural-Urban Commuting Area (RUCA) Codes, ten levels" 
                                                                                
  PL_RUCA4           LENGTH=3                                                   
  LABEL="Patient location: Rural-Urban Commuting Area (RUCA) Codes, four levels"
                                                                                
  PL_RUCC2003        LENGTH=3                                                   
  LABEL="Patient location: Rural-Urban Continuum Codes(RUCC), 2003"             
                                                                                
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
                                                                                
  PSTCO2             LENGTH=4                                                   
  LABEL="Patient state/county FIPS code, possibly derived from ZIP Code"        
                                                                                
  RDRG               LENGTH=$4                                                  
  LABEL="Refined DRG"                                                           
                                                                                
  TOTCHG             LENGTH=6                                                   
  LABEL="Total charges (cleaned)"                                               
                                                                                
  TOTCHG_X           LENGTH=7                                                   
  LABEL="Total charges (as received from source)"                               
                                                                                
  YEAR               LENGTH=3                                                   
  LABEL="Calendar year"                                                         
                                                                                
  ZIP                LENGTH=$5                                                  
  LABEL="Patient ZIP Code"                                                      
                                                                                
  AYEAR              LENGTH=3                                                   
  LABEL="Admission year"                                                        
                                                                                
  DMONTH             LENGTH=3                                                   
  LABEL="Discharge month"                                                       
                                                                                
  BMONTH             LENGTH=3                                                   
  LABEL="Birth month"                                                           
                                                                                
  BYEAR              LENGTH=3                                                   
  LABEL="Birth year"                                                            
                                                                                
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
      @27     AMONTH              N2PF.                                         
      @29     ASOURCE             N2PF.                                         
      @31     ASOURCE_X           $CHAR2.                                       
      @33     ASOURCEUB92         $CHAR1.                                       
      @34     ATYPE               N2PF.                                         
      @36     AWEEKEND            N2PF.                                         
      @38     BWT                 N4PF.                                         
      @42     DIED                N2PF.                                         
      @44     DISP_X              $CHAR2.                                       
      @46     DISPUB92            N2PF.                                         
      @48     DISPUNIFORM         N2PF.                                         
      @50     DQTR                N2PF.                                         
      @52     DRG                 N3PF.                                         
      @55     DRG18               N3PF.                                         
      @58     DRGVER              N2PF.                                         
      @60     DSHOSPID            $CHAR13.                                      
      @73     DX1                 $CHAR5.                                       
      @78     DX2                 $CHAR5.                                       
      @83     DX3                 $CHAR5.                                       
      @88     DX4                 $CHAR5.                                       
      @93     DX5                 $CHAR5.                                       
      @98     DX6                 $CHAR5.                                       
      @103    DX7                 $CHAR5.                                       
      @108    DX8                 $CHAR5.                                       
      @113    DX9                 $CHAR5.                                       
      @118    DXCCS1              N4PF.                                         
      @122    DXCCS2              N4PF.                                         
      @126    DXCCS3              N4PF.                                         
      @130    DXCCS4              N4PF.                                         
      @134    DXCCS5              N4PF.                                         
      @138    DXCCS6              N4PF.                                         
      @142    DXCCS7              N4PF.                                         
      @146    DXCCS8              N4PF.                                         
      @150    DXCCS9              N4PF.                                         
      @154    ECODE1              $CHAR5.                                       
      @159    ECODE2              $CHAR5.                                       
      @164    ECODE3              $CHAR5.                                       
      @169    ECODE4              $CHAR5.                                       
      @174    E_CCS1              N4PF.                                         
      @178    E_CCS2              N4PF.                                         
      @182    E_CCS3              N4PF.                                         
      @186    E_CCS4              N4PF.                                         
      @190    FEMALE              N2PF.                                         
      @192    HOSPST              $CHAR2.                                       
      @194    LOS                 N5PF.                                         
      @199    LOS_X               N6PF.                                         
      @205    MDC                 N2PF.                                         
      @207    MDC18               N2PF.                                         
      @209    MDNUM1_R            N9PF.                                         
      @218    MDNUM2_R            N9PF.                                         
      @227    MDNUM3_R            N9PF.                                         
      @236    MDNUM4_R            N9PF.                                         
      @245    MRN_R               N9PF.                                         
      @254    NDX                 N2PF.                                         
      @256    NECODE              N2PF.                                         
      @258    NEOMAT              N2PF.                                         
      @260    NPR                 N2PF.                                         
      @262    PAY1                N2PF.                                         
      @264    PAY2                N2PF.                                         
      @266    PAY1_X              $CHAR1.                                       
      @267    PAY2_X              $CHAR1.                                       
      @268    PAY3_X              $CHAR1.                                       
      @269    PL_CBSA             N3PF.                                         
      @272    PL_MSA1993          N3PF.                                         
      @275    PL_RUCA             N4P1F.                                        
      @279    PL_RUCA10           N2PF.                                         
      @281    PL_RUCA4            N2PF.                                         
      @283    PL_RUCC2003         N2PF.                                         
      @285    PL_UIC2003          N2PF.                                         
      @287    PL_UR_CAT4          N2PF.                                         
      @289    PL_UR_CAT5          N2PF.                                         
      @291    PR1                 $CHAR4.                                       
      @295    PR2                 $CHAR4.                                       
      @299    PR3                 $CHAR4.                                       
      @303    PR4                 $CHAR4.                                       
      @307    PR5                 $CHAR4.                                       
      @311    PR6                 $CHAR4.                                       
      @315    PRCCS1              N3PF.                                         
      @318    PRCCS2              N3PF.                                         
      @321    PRCCS3              N3PF.                                         
      @324    PRCCS4              N3PF.                                         
      @327    PRCCS5              N3PF.                                         
      @330    PRCCS6              N3PF.                                         
      @333    PRDAY1              N5PF.                                         
      @338    PRDAY2              N5PF.                                         
      @343    PRDAY3              N5PF.                                         
      @348    PRDAY4              N5PF.                                         
      @353    PRDAY5              N5PF.                                         
      @358    PRDAY6              N5PF.                                         
      @363    PSTATE              $CHAR2.                                       
      @365    PSTCO2              N5PF.                                         
      @370    RDRG                $CHAR4.                                       
      @374    TOTCHG              N10PF.                                        
      @384    TOTCHG_X            N15P2F.                                       
      @399    YEAR                N4PF.                                         
      @403    ZIP                 $CHAR5.                                       
      @408    AYEAR               N4PF.                                         
      @412    DMONTH              N2PF.                                         
      @414    BMONTH              N2PF.                                         
      @416    BYEAR               N4PF.                                         
      @420    PRMONTH1            N2PF.                                         
      @422    PRMONTH2            N2PF.                                         
      @424    PRMONTH3            N2PF.                                         
      @426    PRMONTH4            N2PF.                                         
      @428    PRMONTH5            N2PF.                                         
      @430    PRMONTH6            N2PF.                                         
      @432    PRYEAR1             N4PF.                                         
      @436    PRYEAR2             N4PF.                                         
      @440    PRYEAR3             N4PF.                                         
      @444    PRYEAR4             N4PF.                                         
      @448    PRYEAR5             N4PF.                                         
      @452    PRYEAR6             N4PF.                                         
      ;                                                                         
                                                                                
                                                                                
RUN;
