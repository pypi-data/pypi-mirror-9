/*******************************************************************            
*   MD_SID_1994_CORE.SAS:                                                       
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
    '-7' = .B                                                                   
    '-6' = .C                                                                   
    '-5' = .N                                                                   
    OTHER = (|2.|)                                                              
  ;                                                                             
  INVALUE N3PF                                                                  
    '-99' = .                                                                   
    '-88' = .A                                                                  
    '-77' = .B                                                                  
    '-66' = .C                                                                  
    OTHER = (|3.|)                                                              
  ;                                                                             
  INVALUE N4PF                                                                  
    '-999' = .                                                                  
    '-888' = .A                                                                 
    '-777' = .B                                                                 
    '-666' = .C                                                                 
    OTHER = (|4.|)                                                              
  ;                                                                             
  INVALUE N4P1F                                                                 
    '-9.9' = .                                                                  
    '-8.8' = .A                                                                 
    '-7.7' = .B                                                                 
    '-6.6' = .C                                                                 
    OTHER = (|4.1|)                                                             
  ;                                                                             
  INVALUE N5PF                                                                  
    '-9999' = .                                                                 
    '-8888' = .A                                                                
    '-7777' = .B                                                                
    '-6666' = .C                                                                
    OTHER = (|5.|)                                                              
  ;                                                                             
  INVALUE N6PF                                                                  
    '-99999' = .                                                                
    '-88888' = .A                                                               
    '-77777' = .B                                                               
    '-66666' = .C                                                               
    OTHER = (|6.|)                                                              
  ;                                                                             
  INVALUE N6P2F                                                                 
    '-99.99' = .                                                                
    '-88.88' = .A                                                               
    '-77.77' = .B                                                               
    '-66.66' = .C                                                               
    OTHER = (|6.2|)                                                             
  ;                                                                             
  INVALUE N7P2F                                                                 
    '-999.99' = .                                                               
    '-888.88' = .A                                                              
    '-777.77' = .B                                                              
    '-666.66' = .C                                                              
    OTHER = (|7.2|)                                                             
  ;                                                                             
  INVALUE N7P4F                                                                 
    '-9.9999' = .                                                               
    '-8.8888' = .A                                                              
    '-7.7777' = .B                                                              
    '-6.6666' = .C                                                              
    OTHER = (|7.4|)                                                             
  ;                                                                             
  INVALUE N8PF                                                                  
    '-9999999' = .                                                              
    '-8888888' = .A                                                             
    '-7777777' = .B                                                             
    '-6666666' = .C                                                             
    OTHER = (|8.|)                                                              
  ;                                                                             
  INVALUE N8P2F                                                                 
    '-9999.99' = .                                                              
    '-8888.88' = .A                                                             
    '-7777.77' = .B                                                             
    '-6666.66' = .C                                                             
    OTHER = (|8.2|)                                                             
  ;                                                                             
  INVALUE N10PF                                                                 
    '-999999999' = .                                                            
    '-888888888' = .A                                                           
    '-777777777' = .B                                                           
    '-666666666' = .C                                                           
    OTHER = (|10.|)                                                             
  ;                                                                             
  INVALUE N10P4F                                                                
    '-9999.9999' = .                                                            
    '-8888.8888' = .A                                                           
    '-7777.7777' = .B                                                           
    '-6666.6666' = .C                                                           
    OTHER = (|10.4|)                                                            
  ;                                                                             
  INVALUE DATE10F                                                               
    '-999999999' = .                                                            
    '-888888888' = .A                                                           
    '-777777777' = .B                                                           
    '-666666666' = .C                                                           
    OTHER = (|MMDDYY10.|)                                                       
  ;                                                                             
  INVALUE N12P2F                                                                
    '-99999999.99' = .                                                          
    '-88888888.88' = .A                                                         
    '-77777777.77' = .B                                                         
    '-66666666.66' = .C                                                         
    OTHER = (|12.2|)                                                            
  ;                                                                             
  INVALUE N15P2F                                                                
    '-99999999999.99' = .                                                       
    '-88888888888.88' = .A                                                      
    '-77777777777.77' = .B                                                      
    '-66666666666.66' = .C                                                      
    OTHER = (|15.2|)                                                            
  ;                                                                             
  RUN;                                                                          
                                                                                
                                                                                
*******************************;                                                
*  Data Step                  *;                                                
*******************************;                                                
DATA MD_SIDC_1994_CORE;                                                         
INFILE 'MD_SID_1994_CORE.ASC' LRECL = 650;                                      
                                                                                
*** Variable attribute ***;                                                     
ATTRIB                                                                          
  SEQ_SID            LENGTH=7          FORMAT=Z13.                              
  LABEL="I:HCUP-3 SID record sequence number"                                   
                                                                                
  AGE                LENGTH=3                                                   
  LABEL="I:Age in years at admission"                                           
                                                                                
  AGEDAY             LENGTH=3                                                   
  LABEL="I:Age in days (when < 1 year)"                                         
                                                                                
  SEX                LENGTH=3                                                   
  LABEL="I:Sex"                                                                 
                                                                                
  RACE               LENGTH=3                                                   
  LABEL="I:Race"                                                                
                                                                                
  DQTR               LENGTH=3                                                   
  LABEL="I:Discharge quarter"                                                   
                                                                                
  LOS                LENGTH=4                                                   
  LABEL="I:Length of stay (cleaned)"                                            
                                                                                
  DISP               LENGTH=3                                                   
  LABEL="I:Disposition of patient"                                              
                                                                                
  DIED               LENGTH=3                                                   
  LABEL="I:Died during hospitalization"                                         
                                                                                
  ATYPE              LENGTH=3                                                   
  LABEL="I:Admission type"                                                      
                                                                                
  ASOURCE            LENGTH=3                                                   
  LABEL="I:Admission source"                                                    
                                                                                
  NDX                LENGTH=3                                                   
  LABEL="I:Number of diagnoses on this discharge"                               
                                                                                
  DX1                LENGTH=$5                                                  
  LABEL="I:Principal diagnosis"                                                 
                                                                                
  DXV1               LENGTH=3                                                   
  LABEL="I:Validity flag: principal diagnosis"                                  
                                                                                
  DCCHPR1            LENGTH=3                                                   
  LABEL="I:CCHPR: principal diagnosis"                                          
                                                                                
  NPR                LENGTH=3                                                   
  LABEL="I:Number of procedures on this discharge"                              
                                                                                
  PR1                LENGTH=$4                                                  
  LABEL="I:Principal procedure"                                                 
                                                                                
  PRV1               LENGTH=3                                                   
  LABEL="I:Validity flag: principal procedure"                                  
                                                                                
  PCCHPR1            LENGTH=3                                                   
  LABEL="I:CCHPR: principal procedure"                                          
                                                                                
  DRG                LENGTH=3                                                   
  LABEL="I:DRG in effect on discharge date"                                     
                                                                                
  MDC                LENGTH=3                                                   
  LABEL="I:MDC in effect on discharge date"                                     
                                                                                
  DRGVER             LENGTH=3                                                   
  LABEL="I:DRG grouper version used on disch date"                              
                                                                                
  DRG10              LENGTH=3                                                   
  LABEL="I:DRG, Version 10"                                                     
                                                                                
  MDC10              LENGTH=3                                                   
  LABEL="I:MDC, Version 10"                                                     
                                                                                
  PAY1               LENGTH=3                                                   
  LABEL="I:Primary expected payer, uniform"                                     
                                                                                
  TOTCHG             LENGTH=6                                                   
  LABEL="I:Total charges (cleaned)"                                             
                                                                                
  PROCESS            LENGTH=6                                                   
  LABEL="I:HCUP-3 discharge processing ID number"                               
                                                                                
  YEAR               LENGTH=3                                                   
  LABEL="Calendar year"                                                         
                                                                                
  DSHOSPID           LENGTH=$13                                                 
  LABEL="I:Data source hospital ID number"                                      
                                                                                
  DSNUM              LENGTH=3                                                   
  LABEL="I:Data source ID number"                                               
                                                                                
  DSTYPE             LENGTH=3                                                   
  LABEL="I:Data source type"                                                    
                                                                                
  HOSPST             LENGTH=$2                                                  
  LABEL="Hospital state postal code"                                            
                                                                                
  MDID_S             LENGTH=$16                                                 
  LABEL="I:Attending physician number (synthetic)"                              
                                                                                
  SURGID_S           LENGTH=$16                                                 
  LABEL="I:Primary surgeon number (synthetic)"                                  
                                                                                
  ADAYWK             LENGTH=3                                                   
  LABEL="I:Admission day of week"                                               
                                                                                
  LOS_X              LENGTH=3                                                   
  LABEL="I:Length of stay (uncleaned)"                                          
                                                                                
  NEOMAT             LENGTH=3                                                   
  LABEL="I:Neonatal and/or maternal DX and/or PR"                               
                                                                                
  DXSYS              LENGTH=3                                                   
  LABEL="I:Diagnosis coding system"                                             
                                                                                
  DSNDX              LENGTH=3                                                   
  LABEL="I:Max number of diagnoses from source"                                 
                                                                                
  PRSYS              LENGTH=3                                                   
  LABEL="I:Procedure coding system"                                             
                                                                                
  DSNPR              LENGTH=3                                                   
  LABEL="I:Max number of procedures from source"                                
                                                                                
  PRDAY1             LENGTH=3                                                   
  LABEL="I:No. of days from admission to PR1"                                   
                                                                                
  PAY1_N             LENGTH=3                                                   
  LABEL="I:Primary expected payer, nonuniform"                                  
                                                                                
  PAY2               LENGTH=3                                                   
  LABEL="I:Secondary expected payer, uniform"                                   
                                                                                
  PAY2_N             LENGTH=3                                                   
  LABEL="I:Secondary expected payer, nonuniform"                                
                                                                                
  TOTCHG_X           LENGTH=6                                                   
  LABEL="I:Total charges (from data source)"                                    
                                                                                
  DX2                LENGTH=$5                                                  
  LABEL="I:Diagnosis 2"                                                         
                                                                                
  DX3                LENGTH=$5                                                  
  LABEL="I:Diagnosis 3"                                                         
                                                                                
  DX4                LENGTH=$5                                                  
  LABEL="I:Diagnosis 4"                                                         
                                                                                
  DX5                LENGTH=$5                                                  
  LABEL="I:Diagnosis 5"                                                         
                                                                                
  DX6                LENGTH=$5                                                  
  LABEL="I:Diagnosis 6"                                                         
                                                                                
  DX7                LENGTH=$5                                                  
  LABEL="I:Diagnosis 7"                                                         
                                                                                
  DX8                LENGTH=$5                                                  
  LABEL="I:Diagnosis 8"                                                         
                                                                                
  DX9                LENGTH=$5                                                  
  LABEL="I:Diagnosis 9"                                                         
                                                                                
  DX10               LENGTH=$5                                                  
  LABEL="I:Diagnosis 10"                                                        
                                                                                
  DX11               LENGTH=$5                                                  
  LABEL="I:Diagnosis 11"                                                        
                                                                                
  DX12               LENGTH=$5                                                  
  LABEL="I:Diagnosis 12"                                                        
                                                                                
  DX13               LENGTH=$5                                                  
  LABEL="I:Diagnosis 13"                                                        
                                                                                
  DX14               LENGTH=$5                                                  
  LABEL="I:Diagnosis 14"                                                        
                                                                                
  DX15               LENGTH=$5                                                  
  LABEL="I:Diagnosis 15"                                                        
                                                                                
  DX16               LENGTH=$5                                                  
  LABEL="I:Diagnosis 16"                                                        
                                                                                
  DXV2               LENGTH=3                                                   
  LABEL="I:Validity flag: diagnosis 2"                                          
                                                                                
  DXV3               LENGTH=3                                                   
  LABEL="I:Validity flag: diagnosis 3"                                          
                                                                                
  DXV4               LENGTH=3                                                   
  LABEL="I:Validity flag: diagnosis 4"                                          
                                                                                
  DXV5               LENGTH=3                                                   
  LABEL="I:Validity flag: diagnosis 5"                                          
                                                                                
  DXV6               LENGTH=3                                                   
  LABEL="I:Validity flag: diagnosis 6"                                          
                                                                                
  DXV7               LENGTH=3                                                   
  LABEL="I:Validity flag: diagnosis 7"                                          
                                                                                
  DXV8               LENGTH=3                                                   
  LABEL="I:Validity flag: diagnosis 8"                                          
                                                                                
  DXV9               LENGTH=3                                                   
  LABEL="I:Validity flag: diagnosis 9"                                          
                                                                                
  DXV10              LENGTH=3                                                   
  LABEL="I:Validity flag: diagnosis 10"                                         
                                                                                
  DXV11              LENGTH=3                                                   
  LABEL="I:Validity flag: diagnosis 11"                                         
                                                                                
  DXV12              LENGTH=3                                                   
  LABEL="I:Validity flag: diagnosis 12"                                         
                                                                                
  DXV13              LENGTH=3                                                   
  LABEL="I:Validity flag: diagnosis 13"                                         
                                                                                
  DXV14              LENGTH=3                                                   
  LABEL="I:Validity flag: diagnosis 14"                                         
                                                                                
  DXV15              LENGTH=3                                                   
  LABEL="I:Validity flag: diagnosis 15"                                         
                                                                                
  DXV16              LENGTH=3                                                   
  LABEL="I:Validity flag: diagnosis 16"                                         
                                                                                
  DCCHPR2            LENGTH=3                                                   
  LABEL="I:CCHPR: diagnosis 2"                                                  
                                                                                
  DCCHPR3            LENGTH=3                                                   
  LABEL="I:CCHPR: diagnosis 3"                                                  
                                                                                
  DCCHPR4            LENGTH=3                                                   
  LABEL="I:CCHPR: diagnosis 4"                                                  
                                                                                
  DCCHPR5            LENGTH=3                                                   
  LABEL="I:CCHPR: diagnosis 5"                                                  
                                                                                
  DCCHPR6            LENGTH=3                                                   
  LABEL="I:CCHPR: diagnosis 6"                                                  
                                                                                
  DCCHPR7            LENGTH=3                                                   
  LABEL="I:CCHPR: diagnosis 7"                                                  
                                                                                
  DCCHPR8            LENGTH=3                                                   
  LABEL="I:CCHPR: diagnosis 8"                                                  
                                                                                
  DCCHPR9            LENGTH=3                                                   
  LABEL="I:CCHPR: diagnosis 9"                                                  
                                                                                
  DCCHPR10           LENGTH=3                                                   
  LABEL="I:CCHPR: diagnosis 10"                                                 
                                                                                
  DCCHPR11           LENGTH=3                                                   
  LABEL="I:CCHPR: diagnosis 11"                                                 
                                                                                
  DCCHPR12           LENGTH=3                                                   
  LABEL="I:CCHPR: diagnosis 12"                                                 
                                                                                
  DCCHPR13           LENGTH=3                                                   
  LABEL="I:CCHPR: diagnosis 13"                                                 
                                                                                
  DCCHPR14           LENGTH=3                                                   
  LABEL="I:CCHPR: diagnosis 14"                                                 
                                                                                
  DCCHPR15           LENGTH=3                                                   
  LABEL="I:CCHPR: diagnosis 15"                                                 
                                                                                
  DCCHPR16           LENGTH=3                                                   
  LABEL="I:CCHPR: diagnosis 16"                                                 
                                                                                
  PR2                LENGTH=$4                                                  
  LABEL="I:Procedure 2"                                                         
                                                                                
  PR3                LENGTH=$4                                                  
  LABEL="I:Procedure 3"                                                         
                                                                                
  PR4                LENGTH=$4                                                  
  LABEL="I:Procedure 4"                                                         
                                                                                
  PR5                LENGTH=$4                                                  
  LABEL="I:Procedure 5"                                                         
                                                                                
  PR6                LENGTH=$4                                                  
  LABEL="I:Procedure 6"                                                         
                                                                                
  PR7                LENGTH=$4                                                  
  LABEL="I:Procedure 7"                                                         
                                                                                
  PR8                LENGTH=$4                                                  
  LABEL="I:Procedure 8"                                                         
                                                                                
  PR9                LENGTH=$4                                                  
  LABEL="I:Procedure 9"                                                         
                                                                                
  PR10               LENGTH=$4                                                  
  LABEL="I:Procedure 10"                                                        
                                                                                
  PR11               LENGTH=$4                                                  
  LABEL="I:Procedure 11"                                                        
                                                                                
  PR12               LENGTH=$4                                                  
  LABEL="I:Procedure 12"                                                        
                                                                                
  PR13               LENGTH=$4                                                  
  LABEL="I:Procedure 13"                                                        
                                                                                
  PR14               LENGTH=$4                                                  
  LABEL="I:Procedure 14"                                                        
                                                                                
  PR15               LENGTH=$4                                                  
  LABEL="I:Procedure 15"                                                        
                                                                                
  PRV2               LENGTH=3                                                   
  LABEL="I:Validity flag: procedure 2"                                          
                                                                                
  PRV3               LENGTH=3                                                   
  LABEL="I:Validity flag: procedure 3"                                          
                                                                                
  PRV4               LENGTH=3                                                   
  LABEL="I:Validity flag: procedure 4"                                          
                                                                                
  PRV5               LENGTH=3                                                   
  LABEL="I:Validity flag: procedure 5"                                          
                                                                                
  PRV6               LENGTH=3                                                   
  LABEL="I:Validity flag: procedure 6"                                          
                                                                                
  PRV7               LENGTH=3                                                   
  LABEL="I:Validity flag: procedure 7"                                          
                                                                                
  PRV8               LENGTH=3                                                   
  LABEL="I:Validity flag: procedure 8"                                          
                                                                                
  PRV9               LENGTH=3                                                   
  LABEL="I:Validity flag: procedure 9"                                          
                                                                                
  PRV10              LENGTH=3                                                   
  LABEL="I:Validity flag: procedure 10"                                         
                                                                                
  PRV11              LENGTH=3                                                   
  LABEL="I:Validity flag: procedure 11"                                         
                                                                                
  PRV12              LENGTH=3                                                   
  LABEL="I:Validity flag: procedure 12"                                         
                                                                                
  PRV13              LENGTH=3                                                   
  LABEL="I:Validity flag: procedure 13"                                         
                                                                                
  PRV14              LENGTH=3                                                   
  LABEL="I:Validity flag: procedure 14"                                         
                                                                                
  PRV15              LENGTH=3                                                   
  LABEL="I:Validity flag: procedure 15"                                         
                                                                                
  PCCHPR2            LENGTH=3                                                   
  LABEL="I:CCHPR: procedure 2"                                                  
                                                                                
  PCCHPR3            LENGTH=3                                                   
  LABEL="I:CCHPR: procedure 3"                                                  
                                                                                
  PCCHPR4            LENGTH=3                                                   
  LABEL="I:CCHPR: procedure 4"                                                  
                                                                                
  PCCHPR5            LENGTH=3                                                   
  LABEL="I:CCHPR: procedure 5"                                                  
                                                                                
  PCCHPR6            LENGTH=3                                                   
  LABEL="I:CCHPR: procedure 6"                                                  
                                                                                
  PCCHPR7            LENGTH=3                                                   
  LABEL="I:CCHPR: procedure 7"                                                  
                                                                                
  PCCHPR8            LENGTH=3                                                   
  LABEL="I:CCHPR: procedure 8"                                                  
                                                                                
  PCCHPR9            LENGTH=3                                                   
  LABEL="I:CCHPR: procedure 9"                                                  
                                                                                
  PCCHPR10           LENGTH=3                                                   
  LABEL="I:CCHPR: procedure 10"                                                 
                                                                                
  PCCHPR11           LENGTH=3                                                   
  LABEL="I:CCHPR: procedure 11"                                                 
                                                                                
  PCCHPR12           LENGTH=3                                                   
  LABEL="I:CCHPR: procedure 12"                                                 
                                                                                
  PCCHPR13           LENGTH=3                                                   
  LABEL="I:CCHPR: procedure 13"                                                 
                                                                                
  PCCHPR14           LENGTH=3                                                   
  LABEL="I:CCHPR: procedure 14"                                                 
                                                                                
  PCCHPR15           LENGTH=3                                                   
  LABEL="I:CCHPR: procedure 15"                                                 
                                                                                
  PRDAY2             LENGTH=4                                                   
  LABEL="I:No. of days from admission to PR2"                                   
                                                                                
  PRDAY3             LENGTH=4                                                   
  LABEL="I:No. of days from admission to PR3"                                   
                                                                                
  PRDAY4             LENGTH=4                                                   
  LABEL="I:No. of days from admission to PR4"                                   
                                                                                
  PRDAY5             LENGTH=4                                                   
  LABEL="I:No. of days from admission to PR5"                                   
                                                                                
  PRDAY6             LENGTH=4                                                   
  LABEL="I:No. of days from admission to PR6"                                   
                                                                                
  PRDAY7             LENGTH=4                                                   
  LABEL="I:No. of days from admission to PR7"                                   
                                                                                
  PRDAY8             LENGTH=4                                                   
  LABEL="I:No. of days from admission to PR8"                                   
                                                                                
  PRDAY9             LENGTH=4                                                   
  LABEL="I:No. of days from admission to PR9"                                   
                                                                                
  PRDAY10            LENGTH=4                                                   
  LABEL="I:No. of days from admission to PR10"                                  
                                                                                
  PRDAY11            LENGTH=4                                                   
  LABEL="I:No. of days from admission to PR11"                                  
                                                                                
  PRDAY12            LENGTH=4                                                   
  LABEL="I:No. of days from admission to PR12"                                  
                                                                                
  PRDAY13            LENGTH=4                                                   
  LABEL="I:No. of days from admission to PR13"                                  
                                                                                
  PRDAY14            LENGTH=4                                                   
  LABEL="I:No. of days from admission to PR14"                                  
                                                                                
  PRDAY15            LENGTH=4                                                   
  LABEL="I:No. of days from admission to PR15"                                  
                                                                                
  MRN_S              LENGTH=$17                                                 
  LABEL="I:Medical record number (synthetic)"                                   
                                                                                
  BWT                LENGTH=3                                                   
  LABEL="I:Birthweight in grams"                                                
                                                                                
  PAY1_X             LENGTH=$2                                                  
  LABEL="I:Primary exp. payer (from data source)"                               
                                                                                
  PAY2_X             LENGTH=$2                                                  
  LABEL="I:Secondary exp. payer (from data source"                              
  ;                                                                             
                                                                                
                                                                                
*** Input the variables from the ASCII file ***;                                
INPUT                                                                           
      @1      SEQ_SID             13.                                           
      @14     AGE                 N3PF.                                         
      @17     AGEDAY              N3PF.                                         
      @20     SEX                 N3PF.                                         
      @23     RACE                N2PF.                                         
      @25     DQTR                N2PF.                                         
      @27     LOS                 N5PF.                                         
      @32     DISP                N2PF.                                         
      @34     DIED                N2PF.                                         
      @36     ATYPE               N2PF.                                         
      @38     ASOURCE             N2PF.                                         
      @40     NDX                 N2PF.                                         
      @42     DX1                 $CHAR5.                                       
      @47     DXV1                N4PF.                                         
      @51     DCCHPR1             N4PF.                                         
      @55     NPR                 N2PF.                                         
      @57     PR1                 $CHAR4.                                       
      @61     PRV1                N3PF.                                         
      @64     PCCHPR1             N4PF.                                         
      @68     DRG                 N3PF.                                         
      @71     MDC                 N2PF.                                         
      @73     DRGVER              N2PF.                                         
      @75     DRG10               N3PF.                                         
      @78     MDC10               N2PF.                                         
      @80     PAY1                N2PF.                                         
      @82     TOTCHG              N10PF.                                        
      @92     PROCESS             11.                                           
      @103    YEAR                N4PF.                                         
      @107    DSHOSPID            $CHAR13.                                      
      @120    DSNUM               N3PF.                                         
      @123    DSTYPE              N3PF.                                         
      @126    HOSPST              $CHAR2.                                       
      @128    MDID_S              $CHAR16.                                      
      @144    SURGID_S            $CHAR16.                                      
      @160    ADAYWK              N3PF.                                         
      @163    LOS_X               N5PF.                                         
      @168    NEOMAT              N2PF.                                         
      @170    DXSYS               N3PF.                                         
      @173    DSNDX               N3PF.                                         
      @176    PRSYS               N3PF.                                         
      @179    DSNPR               N3PF.                                         
      @182    PRDAY1              N5PF.                                         
      @187    PAY1_N              N3PF.                                         
      @190    PAY2                N2PF.                                         
      @192    PAY2_N              N3PF.                                         
      @195    TOTCHG_X            N12P2F.                                       
      @207    DX2                 $CHAR5.                                       
      @212    DX3                 $CHAR5.                                       
      @217    DX4                 $CHAR5.                                       
      @222    DX5                 $CHAR5.                                       
      @227    DX6                 $CHAR5.                                       
      @232    DX7                 $CHAR5.                                       
      @237    DX8                 $CHAR5.                                       
      @242    DX9                 $CHAR5.                                       
      @247    DX10                $CHAR5.                                       
      @252    DX11                $CHAR5.                                       
      @257    DX12                $CHAR5.                                       
      @262    DX13                $CHAR5.                                       
      @267    DX14                $CHAR5.                                       
      @272    DX15                $CHAR5.                                       
      @277    DX16                $CHAR5.                                       
      @282    DXV2                N4PF.                                         
      @286    DXV3                N4PF.                                         
      @290    DXV4                N4PF.                                         
      @294    DXV5                N4PF.                                         
      @298    DXV6                N4PF.                                         
      @302    DXV7                N4PF.                                         
      @306    DXV8                N4PF.                                         
      @310    DXV9                N4PF.                                         
      @314    DXV10               N4PF.                                         
      @318    DXV11               N4PF.                                         
      @322    DXV12               N4PF.                                         
      @326    DXV13               N4PF.                                         
      @330    DXV14               N4PF.                                         
      @334    DXV15               N4PF.                                         
      @338    DXV16               N4PF.                                         
      @342    DCCHPR2             N4PF.                                         
      @346    DCCHPR3             N4PF.                                         
      @350    DCCHPR4             N4PF.                                         
      @354    DCCHPR5             N4PF.                                         
      @358    DCCHPR6             N4PF.                                         
      @362    DCCHPR7             N4PF.                                         
      @366    DCCHPR8             N4PF.                                         
      @370    DCCHPR9             N4PF.                                         
      @374    DCCHPR10            N4PF.                                         
      @378    DCCHPR11            N4PF.                                         
      @382    DCCHPR12            N4PF.                                         
      @386    DCCHPR13            N4PF.                                         
      @390    DCCHPR14            N4PF.                                         
      @394    DCCHPR15            N4PF.                                         
      @398    DCCHPR16            N4PF.                                         
      @402    PR2                 $CHAR4.                                       
      @406    PR3                 $CHAR4.                                       
      @410    PR4                 $CHAR4.                                       
      @414    PR5                 $CHAR4.                                       
      @418    PR6                 $CHAR4.                                       
      @422    PR7                 $CHAR4.                                       
      @426    PR8                 $CHAR4.                                       
      @430    PR9                 $CHAR4.                                       
      @434    PR10                $CHAR4.                                       
      @438    PR11                $CHAR4.                                       
      @442    PR12                $CHAR4.                                       
      @446    PR13                $CHAR4.                                       
      @450    PR14                $CHAR4.                                       
      @454    PR15                $CHAR4.                                       
      @458    PRV2                N3PF.                                         
      @461    PRV3                N3PF.                                         
      @464    PRV4                N3PF.                                         
      @467    PRV5                N3PF.                                         
      @470    PRV6                N3PF.                                         
      @473    PRV7                N3PF.                                         
      @476    PRV8                N3PF.                                         
      @479    PRV9                N3PF.                                         
      @482    PRV10               N3PF.                                         
      @485    PRV11               N3PF.                                         
      @488    PRV12               N3PF.                                         
      @491    PRV13               N3PF.                                         
      @494    PRV14               N3PF.                                         
      @497    PRV15               N3PF.                                         
      @500    PCCHPR2             N4PF.                                         
      @504    PCCHPR3             N4PF.                                         
      @508    PCCHPR4             N4PF.                                         
      @512    PCCHPR5             N4PF.                                         
      @516    PCCHPR6             N4PF.                                         
      @520    PCCHPR7             N4PF.                                         
      @524    PCCHPR8             N4PF.                                         
      @528    PCCHPR9             N4PF.                                         
      @532    PCCHPR10            N4PF.                                         
      @536    PCCHPR11            N4PF.                                         
      @540    PCCHPR12            N4PF.                                         
      @544    PCCHPR13            N4PF.                                         
      @548    PCCHPR14            N4PF.                                         
      @552    PCCHPR15            N4PF.                                         
      @556    PRDAY2              N5PF.                                         
      @561    PRDAY3              N5PF.                                         
      @566    PRDAY4              N5PF.                                         
      @571    PRDAY5              N5PF.                                         
      @576    PRDAY6              N5PF.                                         
      @581    PRDAY7              N5PF.                                         
      @586    PRDAY8              N5PF.                                         
      @591    PRDAY9              N5PF.                                         
      @596    PRDAY10             N5PF.                                         
      @601    PRDAY11             N5PF.                                         
      @606    PRDAY12             N5PF.                                         
      @611    PRDAY13             N5PF.                                         
      @616    PRDAY14             N5PF.                                         
      @621    PRDAY15             N5PF.                                         
      @626    MRN_S               $CHAR17.                                      
      @643    BWT                 N4PF.                                         
      @647    PAY1_X              $CHAR2.                                       
      @649    PAY2_X              $CHAR2.                                       
      ;                                                                         
                                                                                
                                                                                
RUN;
