/*******************************************************************            
*   FL_SID_1990_CORE.SAS:                                                       
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
DATA FL_SIDC_1990_CORE;                                                         
INFILE 'FL_SID_1990_CORE.ASC' LRECL = 248;                                      
                                                                                
*** Variable attribute ***;                                                     
ATTRIB                                                                          
  AGE                LENGTH=3                                                   
  LABEL="I:Age in years at admission"                                           
                                                                                
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
                                                                                
  YEAR               LENGTH=3                                                   
  LABEL="Calendar year"                                                         
                                                                                
  DSHOSPID           LENGTH=$13                                                 
  LABEL="I:Data source hospital ID number"                                      
                                                                                
  DSTYPE             LENGTH=3                                                   
  LABEL="I:Data source type"                                                    
                                                                                
  HOSPST             LENGTH=$2                                                  
  LABEL="Hospital state postal code"                                            
                                                                                
  MDID_S             LENGTH=$16                                                 
  LABEL="I:Attending physician number (synthetic)"                              
                                                                                
  SURGID_S           LENGTH=$16                                                 
  LABEL="I:Primary surgeon number (synthetic)"                                  
                                                                                
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
                                                                                
  DXV2               LENGTH=3                                                   
  LABEL="I:Validity flag: diagnosis 2"                                          
                                                                                
  DXV3               LENGTH=3                                                   
  LABEL="I:Validity flag: diagnosis 3"                                          
                                                                                
  DXV4               LENGTH=3                                                   
  LABEL="I:Validity flag: diagnosis 4"                                          
                                                                                
  DXV5               LENGTH=3                                                   
  LABEL="I:Validity flag: diagnosis 5"                                          
                                                                                
  DCCHPR2            LENGTH=3                                                   
  LABEL="I:CCHPR: diagnosis 2"                                                  
                                                                                
  DCCHPR3            LENGTH=3                                                   
  LABEL="I:CCHPR: diagnosis 3"                                                  
                                                                                
  DCCHPR4            LENGTH=3                                                   
  LABEL="I:CCHPR: diagnosis 4"                                                  
                                                                                
  DCCHPR5            LENGTH=3                                                   
  LABEL="I:CCHPR: diagnosis 5"                                                  
                                                                                
  PR2                LENGTH=$4                                                  
  LABEL="I:Procedure 2"                                                         
                                                                                
  PR3                LENGTH=$4                                                  
  LABEL="I:Procedure 3"                                                         
                                                                                
  PRV2               LENGTH=3                                                   
  LABEL="I:Validity flag: procedure 2"                                          
                                                                                
  PRV3               LENGTH=3                                                   
  LABEL="I:Validity flag: procedure 3"                                          
                                                                                
  PCCHPR2            LENGTH=3                                                   
  LABEL="I:CCHPR: procedure 2"                                                  
                                                                                
  PCCHPR3            LENGTH=3                                                   
  LABEL="I:CCHPR: procedure 3"                                                  
                                                                                
  ZIP                LENGTH=$5                                                  
  LABEL="I:Patient zip code"                                                    
                                                                                
  PAY1_X             LENGTH=$1                                                  
  LABEL="I:Primary exp. payer (from data source)"                               
  ;                                                                             
                                                                                
                                                                                
*** Input the variables from the ASCII file ***;                                
INPUT                                                                           
      @1      AGE                 N3PF.                                         
      @4      SEX                 N3PF.                                         
      @7      RACE                N2PF.                                         
      @9      DQTR                N2PF.                                         
      @11     LOS                 N5PF.                                         
      @16     DISP                N2PF.                                         
      @18     DIED                N2PF.                                         
      @20     ATYPE               N2PF.                                         
      @22     ASOURCE             N2PF.                                         
      @24     NDX                 N2PF.                                         
      @26     DX1                 $CHAR5.                                       
      @31     DXV1                N4PF.                                         
      @35     DCCHPR1             N4PF.                                         
      @39     NPR                 N2PF.                                         
      @41     PR1                 $CHAR4.                                       
      @45     PRV1                N3PF.                                         
      @48     PCCHPR1             N4PF.                                         
      @52     DRG                 N3PF.                                         
      @55     MDC                 N2PF.                                         
      @57     DRGVER              N2PF.                                         
      @59     DRG10               N3PF.                                         
      @62     MDC10               N2PF.                                         
      @64     PAY1                N2PF.                                         
      @66     TOTCHG              N10PF.                                        
      @76     YEAR                N4PF.                                         
      @80     DSHOSPID            $CHAR13.                                      
      @93     DSTYPE              N3PF.                                         
      @96     HOSPST              $CHAR2.                                       
      @98     MDID_S              $CHAR16.                                      
      @114    SURGID_S            $CHAR16.                                      
      @130    LOS_X               N5PF.                                         
      @135    NEOMAT              N2PF.                                         
      @137    DXSYS               N3PF.                                         
      @140    DSNDX               N3PF.                                         
      @143    PRSYS               N3PF.                                         
      @146    DSNPR               N3PF.                                         
      @149    PRDAY1              N5PF.                                         
      @154    PAY1_N              N3PF.                                         
      @157    TOTCHG_X            N12P2F.                                       
      @169    DX2                 $CHAR5.                                       
      @174    DX3                 $CHAR5.                                       
      @179    DX4                 $CHAR5.                                       
      @184    DX5                 $CHAR5.                                       
      @189    DXV2                N4PF.                                         
      @193    DXV3                N4PF.                                         
      @197    DXV4                N4PF.                                         
      @201    DXV5                N4PF.                                         
      @205    DCCHPR2             N4PF.                                         
      @209    DCCHPR3             N4PF.                                         
      @213    DCCHPR4             N4PF.                                         
      @217    DCCHPR5             N4PF.                                         
      @221    PR2                 $CHAR4.                                       
      @225    PR3                 $CHAR4.                                       
      @229    PRV2                N3PF.                                         
      @232    PRV3                N3PF.                                         
      @235    PCCHPR2             N4PF.                                         
      @239    PCCHPR3             N4PF.                                         
      @243    ZIP                 $CHAR5.                                       
      @248    PAY1_X              $CHAR1.                                       
      ;                                                                         
                                                                                
                                                                                
RUN;
