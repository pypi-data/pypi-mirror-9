/*******************************************************************            
*   WA_SID_1994_CHGS.SAS:                                                       
*      THE SAS CODE SHOWN BELOW WILL LOAD THE ASCII                             
*      INPATIENT STAY CHGS FILE INTO SAS                                        
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
DATA WA_SIDC_1994_CHGS;                                                         
INFILE 'WA_SID_1994_CHGS.ASC' LRECL = 984;                                      
                                                                                
*** Variable attribute ***;                                                     
ATTRIB                                                                          
  SEQ_SID            LENGTH=8          FORMAT=Z13.                              
  LABEL="I:HCUP-3 SID record sequence number"                                   
                                                                                
  PROCESS            LENGTH=7                                                   
  LABEL="I:HCUP-3 discharge processing ID number"                               
                                                                                
  REVCD1             LENGTH=$4                                                  
  LABEL="I:Revenue code 1 (from data source)"                                   
                                                                                
  REVCD2             LENGTH=$4                                                  
  LABEL="I:Revenue code 2 (from data source)"                                   
                                                                                
  REVCD3             LENGTH=$4                                                  
  LABEL="I:Revenue code 3 (from data source)"                                   
                                                                                
  REVCD4             LENGTH=$4                                                  
  LABEL="I:Revenue code 4 (from data source)"                                   
                                                                                
  REVCD5             LENGTH=$4                                                  
  LABEL="I:Revenue code 5 (from data source)"                                   
                                                                                
  REVCD6             LENGTH=$4                                                  
  LABEL="I:Revenue code 6 (from data source)"                                   
                                                                                
  REVCD7             LENGTH=$4                                                  
  LABEL="I:Revenue code 7 (from data source)"                                   
                                                                                
  REVCD8             LENGTH=$4                                                  
  LABEL="I:Revenue code 8 (from data source)"                                   
                                                                                
  REVCD9             LENGTH=$4                                                  
  LABEL="I:Revenue code 9 (from data source)"                                   
                                                                                
  REVCD10            LENGTH=$4                                                  
  LABEL="I:Revenue code 10 (from data source)"                                  
                                                                                
  REVCD11            LENGTH=$4                                                  
  LABEL="I:Revenue code 11 (from data source)"                                  
                                                                                
  REVCD12            LENGTH=$4                                                  
  LABEL="I:Revenue code 12 (from data source)"                                  
                                                                                
  REVCD13            LENGTH=$4                                                  
  LABEL="I:Revenue code 13 (from data source)"                                  
                                                                                
  REVCD14            LENGTH=$4                                                  
  LABEL="I:Revenue code 14 (from data source)"                                  
                                                                                
  REVCD15            LENGTH=$4                                                  
  LABEL="I:Revenue code 15 (from data source)"                                  
                                                                                
  REVCD16            LENGTH=$4                                                  
  LABEL="I:Revenue code 16 (from data source)"                                  
                                                                                
  REVCD17            LENGTH=$4                                                  
  LABEL="I:Revenue code 17 (from data source)"                                  
                                                                                
  REVCD18            LENGTH=$4                                                  
  LABEL="I:Revenue code 18 (from data source)"                                  
                                                                                
  REVCD19            LENGTH=$4                                                  
  LABEL="I:Revenue code 19 (from data source)"                                  
                                                                                
  REVCD20            LENGTH=$4                                                  
  LABEL="I:Revenue code 20 (from data source)"                                  
                                                                                
  REVCD21            LENGTH=$4                                                  
  LABEL="I:Revenue code 21 (from data source)"                                  
                                                                                
  REVCD22            LENGTH=$4                                                  
  LABEL="I:Revenue code 22 (from data source)"                                  
                                                                                
  REVCD23            LENGTH=$4                                                  
  LABEL="I:Revenue code 23 (from data source)"                                  
                                                                                
  REVCD24            LENGTH=$4                                                  
  LABEL="I:Revenue code 24 (from data source)"                                  
                                                                                
  REVCD25            LENGTH=$4                                                  
  LABEL="I:Revenue code 25 (from data source)"                                  
                                                                                
  REVCD26            LENGTH=$4                                                  
  LABEL="I:Revenue code 26 (from data source)"                                  
                                                                                
  REVCD27            LENGTH=$4                                                  
  LABEL="I:Revenue code 27 (from data source)"                                  
                                                                                
  REVCD28            LENGTH=$4                                                  
  LABEL="I:Revenue code 28 (from data source)"                                  
                                                                                
  REVCD29            LENGTH=$4                                                  
  LABEL="I:Revenue code 29 (from data source)"                                  
                                                                                
  REVCD30            LENGTH=$4                                                  
  LABEL="I:Revenue code 30 (from data source)"                                  
                                                                                
  REVCD31            LENGTH=$4                                                  
  LABEL="I:Revenue code 31 (from data source)"                                  
                                                                                
  REVCD32            LENGTH=$4                                                  
  LABEL="I:Revenue code 32 (from data source)"                                  
                                                                                
  REVCD33            LENGTH=$4                                                  
  LABEL="I:Revenue code 33 (from data source)"                                  
                                                                                
  REVCD34            LENGTH=$4                                                  
  LABEL="I:Revenue code 34 (from data source)"                                  
                                                                                
  REVCD35            LENGTH=$4                                                  
  LABEL="I:Revenue code 35 (from data source)"                                  
                                                                                
  REVCD36            LENGTH=$4                                                  
  LABEL="I:Revenue code 36 (from data source)"                                  
                                                                                
  REVCD37            LENGTH=$4                                                  
  LABEL="I:Revenue code 37 (from data source)"                                  
                                                                                
  REVCD38            LENGTH=$4                                                  
  LABEL="I:Revenue code 38 (from data source)"                                  
                                                                                
  REVCD39            LENGTH=$4                                                  
  LABEL="I:Revenue code 39 (from data source)"                                  
                                                                                
  REVCD40            LENGTH=$4                                                  
  LABEL="I:Revenue code 40 (from data source)"                                  
                                                                                
  UNIT1              LENGTH=4                                                   
  LABEL="I:Units of service 1 (from data source)"                               
                                                                                
  UNIT2              LENGTH=4                                                   
  LABEL="I:Units of service 2 (from data source)"                               
                                                                                
  UNIT3              LENGTH=4                                                   
  LABEL="I:Units of service 3 (from data source)"                               
                                                                                
  UNIT4              LENGTH=4                                                   
  LABEL="I:Units of service 4 (from data source)"                               
                                                                                
  UNIT5              LENGTH=4                                                   
  LABEL="I:Units of service 5 (from data source)"                               
                                                                                
  UNIT6              LENGTH=4                                                   
  LABEL="I:Units of service 6 (from data source)"                               
                                                                                
  UNIT7              LENGTH=4                                                   
  LABEL="I:Units of service 7 (from data source)"                               
                                                                                
  UNIT8              LENGTH=4                                                   
  LABEL="I:Units of service 8 (from data source)"                               
                                                                                
  UNIT9              LENGTH=4                                                   
  LABEL="I:Units of service 9 (from data source)"                               
                                                                                
  UNIT10             LENGTH=4                                                   
  LABEL="I:Units of service 10 (from data source)"                              
                                                                                
  UNIT11             LENGTH=4                                                   
  LABEL="I:Units of service 11 (from data source)"                              
                                                                                
  UNIT12             LENGTH=4                                                   
  LABEL="I:Units of service 12 (from data source)"                              
                                                                                
  UNIT13             LENGTH=4                                                   
  LABEL="I:Units of service 13 (from data source)"                              
                                                                                
  UNIT14             LENGTH=4                                                   
  LABEL="I:Units of service 14 (from data source)"                              
                                                                                
  UNIT15             LENGTH=4                                                   
  LABEL="I:Units of service 15 (from data source)"                              
                                                                                
  UNIT16             LENGTH=4                                                   
  LABEL="I:Units of service 16 (from data source)"                              
                                                                                
  UNIT17             LENGTH=4                                                   
  LABEL="I:Units of service 17 (from data source)"                              
                                                                                
  UNIT18             LENGTH=4                                                   
  LABEL="I:Units of service 18 (from data source)"                              
                                                                                
  UNIT19             LENGTH=4                                                   
  LABEL="I:Units of service 19 (from data source)"                              
                                                                                
  UNIT20             LENGTH=4                                                   
  LABEL="I:Units of service 20 (from data source)"                              
                                                                                
  UNIT21             LENGTH=4                                                   
  LABEL="I:Units of service 21 (from data source)"                              
                                                                                
  UNIT22             LENGTH=4                                                   
  LABEL="I:Units of service 22 (from data source)"                              
                                                                                
  UNIT23             LENGTH=4                                                   
  LABEL="I:Units of service 23 (from data source)"                              
                                                                                
  UNIT24             LENGTH=4                                                   
  LABEL="I:Units of service 24 (from data source)"                              
                                                                                
  UNIT25             LENGTH=4                                                   
  LABEL="I:Units of service 25 (from data source)"                              
                                                                                
  UNIT26             LENGTH=4                                                   
  LABEL="I:Units of service 26 (from data source)"                              
                                                                                
  UNIT27             LENGTH=4                                                   
  LABEL="I:Units of service 27 (from data source)"                              
                                                                                
  UNIT28             LENGTH=4                                                   
  LABEL="I:Units of service 28 (from data source)"                              
                                                                                
  UNIT29             LENGTH=4                                                   
  LABEL="I:Units of service 29 (from data source)"                              
                                                                                
  UNIT30             LENGTH=4                                                   
  LABEL="I:Units of service 30 (from data source)"                              
                                                                                
  UNIT31             LENGTH=4                                                   
  LABEL="I:Units of service 31 (from data source)"                              
                                                                                
  UNIT32             LENGTH=4                                                   
  LABEL="I:Units of service 32 (from data source)"                              
                                                                                
  UNIT33             LENGTH=4                                                   
  LABEL="I:Units of service 33 (from data source)"                              
                                                                                
  UNIT34             LENGTH=4                                                   
  LABEL="I:Units of service 34 (from data source)"                              
                                                                                
  UNIT35             LENGTH=4                                                   
  LABEL="I:Units of service 35 (from data source)"                              
                                                                                
  UNIT36             LENGTH=4                                                   
  LABEL="I:Units of service 36 (from data source)"                              
                                                                                
  UNIT37             LENGTH=4                                                   
  LABEL="I:Units of service 37 (from data source)"                              
                                                                                
  UNIT38             LENGTH=4                                                   
  LABEL="I:Units of service 38 (from data source)"                              
                                                                                
  UNIT39             LENGTH=4                                                   
  LABEL="I:Units of service 39 (from data source)"                              
                                                                                
  UNIT40             LENGTH=4                                                   
  LABEL="I:Units of service 40 (from data source)"                              
                                                                                
  CHG1               LENGTH=6                                                   
  LABEL="I:Detailed charges 1 (from data source)"                               
                                                                                
  CHG2               LENGTH=6                                                   
  LABEL="I:Detailed charges 2 (from data source)"                               
                                                                                
  CHG3               LENGTH=6                                                   
  LABEL="I:Detailed charges 3 (from data source)"                               
                                                                                
  CHG4               LENGTH=6                                                   
  LABEL="I:Detailed charges 4 (from data source)"                               
                                                                                
  CHG5               LENGTH=6                                                   
  LABEL="I:Detailed charges 5 (from data source)"                               
                                                                                
  CHG6               LENGTH=6                                                   
  LABEL="I:Detailed charges 6 (from data source)"                               
                                                                                
  CHG7               LENGTH=6                                                   
  LABEL="I:Detailed charges 7 (from data source)"                               
                                                                                
  CHG8               LENGTH=6                                                   
  LABEL="I:Detailed charges 8 (from data source)"                               
                                                                                
  CHG9               LENGTH=6                                                   
  LABEL="I:Detailed charges 9 (from data source)"                               
                                                                                
  CHG10              LENGTH=6                                                   
  LABEL="I:Detailed charges 10 (from data source)"                              
                                                                                
  CHG11              LENGTH=6                                                   
  LABEL="I:Detailed charges 11 (from data source)"                              
                                                                                
  CHG12              LENGTH=6                                                   
  LABEL="I:Detailed charges 12 (from data source)"                              
                                                                                
  CHG13              LENGTH=6                                                   
  LABEL="I:Detailed charges 13 (from data source)"                              
                                                                                
  CHG14              LENGTH=6                                                   
  LABEL="I:Detailed charges 14 (from data source)"                              
                                                                                
  CHG15              LENGTH=6                                                   
  LABEL="I:Detailed charges 15 (from data source)"                              
                                                                                
  CHG16              LENGTH=6                                                   
  LABEL="I:Detailed charges 16 (from data source)"                              
                                                                                
  CHG17              LENGTH=6                                                   
  LABEL="I:Detailed charges 17 (from data source)"                              
                                                                                
  CHG18              LENGTH=6                                                   
  LABEL="I:Detailed charges 18 (from data source)"                              
                                                                                
  CHG19              LENGTH=6                                                   
  LABEL="I:Detailed charges 19 (from data source)"                              
                                                                                
  CHG20              LENGTH=6                                                   
  LABEL="I:Detailed charges 20 (from data source)"                              
                                                                                
  CHG21              LENGTH=6                                                   
  LABEL="I:Detailed charges 21 (from data source)"                              
                                                                                
  CHG22              LENGTH=6                                                   
  LABEL="I:Detailed charges 22 (from data source)"                              
                                                                                
  CHG23              LENGTH=6                                                   
  LABEL="I:Detailed charges 23 (from data source)"                              
                                                                                
  CHG24              LENGTH=6                                                   
  LABEL="I:Detailed charges 24 (from data source)"                              
                                                                                
  CHG25              LENGTH=6                                                   
  LABEL="I:Detailed charges 25 (from data source)"                              
                                                                                
  CHG26              LENGTH=6                                                   
  LABEL="I:Detailed charges 26 (from data source)"                              
                                                                                
  CHG27              LENGTH=6                                                   
  LABEL="I:Detailed charges 27 (from data source)"                              
                                                                                
  CHG28              LENGTH=6                                                   
  LABEL="I:Detailed charges 28 (from data source)"                              
                                                                                
  CHG29              LENGTH=6                                                   
  LABEL="I:Detailed charges 29 (from data source)"                              
                                                                                
  CHG30              LENGTH=6                                                   
  LABEL="I:Detailed charges 30 (from data source)"                              
                                                                                
  CHG31              LENGTH=6                                                   
  LABEL="I:Detailed charges 31 (from data source)"                              
                                                                                
  CHG32              LENGTH=6                                                   
  LABEL="I:Detailed charges 32 (from data source)"                              
                                                                                
  CHG33              LENGTH=6                                                   
  LABEL="I:Detailed charges 33 (from data source)"                              
                                                                                
  CHG34              LENGTH=6                                                   
  LABEL="I:Detailed charges 34 (from data source)"                              
                                                                                
  CHG35              LENGTH=6                                                   
  LABEL="I:Detailed charges 35 (from data source)"                              
                                                                                
  CHG36              LENGTH=6                                                   
  LABEL="I:Detailed charges 36 (from data source)"                              
                                                                                
  CHG37              LENGTH=6                                                   
  LABEL="I:Detailed charges 37 (from data source)"                              
                                                                                
  CHG38              LENGTH=6                                                   
  LABEL="I:Detailed charges 38 (from data source)"                              
                                                                                
  CHG39              LENGTH=6                                                   
  LABEL="I:Detailed charges 39 (from data source)"                              
                                                                                
  CHG40              LENGTH=6                                                   
  LABEL="I:Detailed charges 40 (from data source)"                              
  ;                                                                             
                                                                                
                                                                                
*** Input the variables from the ASCII file ***;                                
INPUT                                                                           
      @1      SEQ_SID             13.                                           
      @14     PROCESS             11.                                           
      @25     REVCD1              $CHAR4.                                       
      @29     REVCD2              $CHAR4.                                       
      @33     REVCD3              $CHAR4.                                       
      @37     REVCD4              $CHAR4.                                       
      @41     REVCD5              $CHAR4.                                       
      @45     REVCD6              $CHAR4.                                       
      @49     REVCD7              $CHAR4.                                       
      @53     REVCD8              $CHAR4.                                       
      @57     REVCD9              $CHAR4.                                       
      @61     REVCD10             $CHAR4.                                       
      @65     REVCD11             $CHAR4.                                       
      @69     REVCD12             $CHAR4.                                       
      @73     REVCD13             $CHAR4.                                       
      @77     REVCD14             $CHAR4.                                       
      @81     REVCD15             $CHAR4.                                       
      @85     REVCD16             $CHAR4.                                       
      @89     REVCD17             $CHAR4.                                       
      @93     REVCD18             $CHAR4.                                       
      @97     REVCD19             $CHAR4.                                       
      @101    REVCD20             $CHAR4.                                       
      @105    REVCD21             $CHAR4.                                       
      @109    REVCD22             $CHAR4.                                       
      @113    REVCD23             $CHAR4.                                       
      @117    REVCD24             $CHAR4.                                       
      @121    REVCD25             $CHAR4.                                       
      @125    REVCD26             $CHAR4.                                       
      @129    REVCD27             $CHAR4.                                       
      @133    REVCD28             $CHAR4.                                       
      @137    REVCD29             $CHAR4.                                       
      @141    REVCD30             $CHAR4.                                       
      @145    REVCD31             $CHAR4.                                       
      @149    REVCD32             $CHAR4.                                       
      @153    REVCD33             $CHAR4.                                       
      @157    REVCD34             $CHAR4.                                       
      @161    REVCD35             $CHAR4.                                       
      @165    REVCD36             $CHAR4.                                       
      @169    REVCD37             $CHAR4.                                       
      @173    REVCD38             $CHAR4.                                       
      @177    REVCD39             $CHAR4.                                       
      @181    REVCD40             $CHAR4.                                       
      @185    UNIT1               N8PF.                                         
      @193    UNIT2               N8PF.                                         
      @201    UNIT3               N8PF.                                         
      @209    UNIT4               N8PF.                                         
      @217    UNIT5               N8PF.                                         
      @225    UNIT6               N8PF.                                         
      @233    UNIT7               N8PF.                                         
      @241    UNIT8               N8PF.                                         
      @249    UNIT9               N8PF.                                         
      @257    UNIT10              N8PF.                                         
      @265    UNIT11              N8PF.                                         
      @273    UNIT12              N8PF.                                         
      @281    UNIT13              N8PF.                                         
      @289    UNIT14              N8PF.                                         
      @297    UNIT15              N8PF.                                         
      @305    UNIT16              N8PF.                                         
      @313    UNIT17              N8PF.                                         
      @321    UNIT18              N8PF.                                         
      @329    UNIT19              N8PF.                                         
      @337    UNIT20              N8PF.                                         
      @345    UNIT21              N8PF.                                         
      @353    UNIT22              N8PF.                                         
      @361    UNIT23              N8PF.                                         
      @369    UNIT24              N8PF.                                         
      @377    UNIT25              N8PF.                                         
      @385    UNIT26              N8PF.                                         
      @393    UNIT27              N8PF.                                         
      @401    UNIT28              N8PF.                                         
      @409    UNIT29              N8PF.                                         
      @417    UNIT30              N8PF.                                         
      @425    UNIT31              N8PF.                                         
      @433    UNIT32              N8PF.                                         
      @441    UNIT33              N8PF.                                         
      @449    UNIT34              N8PF.                                         
      @457    UNIT35              N8PF.                                         
      @465    UNIT36              N8PF.                                         
      @473    UNIT37              N8PF.                                         
      @481    UNIT38              N8PF.                                         
      @489    UNIT39              N8PF.                                         
      @497    UNIT40              N8PF.                                         
      @505    CHG1                N12P2F.                                       
      @517    CHG2                N12P2F.                                       
      @529    CHG3                N12P2F.                                       
      @541    CHG4                N12P2F.                                       
      @553    CHG5                N12P2F.                                       
      @565    CHG6                N12P2F.                                       
      @577    CHG7                N12P2F.                                       
      @589    CHG8                N12P2F.                                       
      @601    CHG9                N12P2F.                                       
      @613    CHG10               N12P2F.                                       
      @625    CHG11               N12P2F.                                       
      @637    CHG12               N12P2F.                                       
      @649    CHG13               N12P2F.                                       
      @661    CHG14               N12P2F.                                       
      @673    CHG15               N12P2F.                                       
      @685    CHG16               N12P2F.                                       
      @697    CHG17               N12P2F.                                       
      @709    CHG18               N12P2F.                                       
      @721    CHG19               N12P2F.                                       
      @733    CHG20               N12P2F.                                       
      @745    CHG21               N12P2F.                                       
      @757    CHG22               N12P2F.                                       
      @769    CHG23               N12P2F.                                       
      @781    CHG24               N12P2F.                                       
      @793    CHG25               N12P2F.                                       
      @805    CHG26               N12P2F.                                       
      @817    CHG27               N12P2F.                                       
      @829    CHG28               N12P2F.                                       
      @841    CHG29               N12P2F.                                       
      @853    CHG30               N12P2F.                                       
      @865    CHG31               N12P2F.                                       
      @877    CHG32               N12P2F.                                       
      @889    CHG33               N12P2F.                                       
      @901    CHG34               N12P2F.                                       
      @913    CHG35               N12P2F.                                       
      @925    CHG36               N12P2F.                                       
      @937    CHG37               N12P2F.                                       
      @949    CHG38               N12P2F.                                       
      @961    CHG39               N12P2F.                                       
      @973    CHG40               N12P2F.                                       
      ;                                                                         
                                                                                
                                                                                
RUN;
