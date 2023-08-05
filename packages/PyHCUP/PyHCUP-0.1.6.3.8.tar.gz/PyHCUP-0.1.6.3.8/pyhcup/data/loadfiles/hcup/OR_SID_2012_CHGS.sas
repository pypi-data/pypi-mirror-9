/*******************************************************************            
*   OR_SID_2012_CHGS.SAS:                                                       
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
DATA OR_SIDC_2012_CHGS;                                                         
INFILE 'OR_SID_2012_CHGS.ASC' LRECL = 1337;                                     
                                                                                
*** Variable attribute ***;                                                     
ATTRIB                                                                          
  KEY                        LENGTH=8                 FORMAT=Z15.               
  LABEL="HCUP record identifier"                                                
                                                                                
  NREVCD                     LENGTH=3                                           
  LABEL="Number of revenue codes for this discharge"                            
                                                                                
  REVCD1                     LENGTH=$4                                          
  LABEL="Revenue code 1 (as received from source)"                              
                                                                                
  REVCD2                     LENGTH=$4                                          
  LABEL="Revenue code 2 (as received from source)"                              
                                                                                
  REVCD3                     LENGTH=$4                                          
  LABEL="Revenue code 3 (as received from source)"                              
                                                                                
  REVCD4                     LENGTH=$4                                          
  LABEL="Revenue code 4 (as received from source)"                              
                                                                                
  REVCD5                     LENGTH=$4                                          
  LABEL="Revenue code 5 (as received from source)"                              
                                                                                
  REVCD6                     LENGTH=$4                                          
  LABEL="Revenue code 6 (as received from source)"                              
                                                                                
  REVCD7                     LENGTH=$4                                          
  LABEL="Revenue code 7 (as received from source)"                              
                                                                                
  REVCD8                     LENGTH=$4                                          
  LABEL="Revenue code 8 (as received from source)"                              
                                                                                
  REVCD9                     LENGTH=$4                                          
  LABEL="Revenue code 9 (as received from source)"                              
                                                                                
  REVCD10                    LENGTH=$4                                          
  LABEL="Revenue code 10 (as received from source)"                             
                                                                                
  REVCD11                    LENGTH=$4                                          
  LABEL="Revenue code 11 (as received from source)"                             
                                                                                
  REVCD12                    LENGTH=$4                                          
  LABEL="Revenue code 12 (as received from source)"                             
                                                                                
  REVCD13                    LENGTH=$4                                          
  LABEL="Revenue code 13 (as received from source)"                             
                                                                                
  REVCD14                    LENGTH=$4                                          
  LABEL="Revenue code 14 (as received from source)"                             
                                                                                
  REVCD15                    LENGTH=$4                                          
  LABEL="Revenue code 15 (as received from source)"                             
                                                                                
  REVCD16                    LENGTH=$4                                          
  LABEL="Revenue code 16 (as received from source)"                             
                                                                                
  REVCD17                    LENGTH=$4                                          
  LABEL="Revenue code 17 (as received from source)"                             
                                                                                
  REVCD18                    LENGTH=$4                                          
  LABEL="Revenue code 18 (as received from source)"                             
                                                                                
  REVCD19                    LENGTH=$4                                          
  LABEL="Revenue code 19 (as received from source)"                             
                                                                                
  REVCD20                    LENGTH=$4                                          
  LABEL="Revenue code 20 (as received from source)"                             
                                                                                
  REVCD21                    LENGTH=$4                                          
  LABEL="Revenue code 21 (as received from source)"                             
                                                                                
  REVCD22                    LENGTH=$4                                          
  LABEL="Revenue code 22 (as received from source)"                             
                                                                                
  REVCD23                    LENGTH=$4                                          
  LABEL="Revenue code 23 (as received from source)"                             
                                                                                
  REVCD24                    LENGTH=$4                                          
  LABEL="Revenue code 24 (as received from source)"                             
                                                                                
  REVCD25                    LENGTH=$4                                          
  LABEL="Revenue code 25 (as received from source)"                             
                                                                                
  REVCD26                    LENGTH=$4                                          
  LABEL="Revenue code 26 (as received from source)"                             
                                                                                
  REVCD27                    LENGTH=$4                                          
  LABEL="Revenue code 27 (as received from source)"                             
                                                                                
  REVCD28                    LENGTH=$4                                          
  LABEL="Revenue code 28 (as received from source)"                             
                                                                                
  REVCD29                    LENGTH=$4                                          
  LABEL="Revenue code 29 (as received from source)"                             
                                                                                
  REVCD30                    LENGTH=$4                                          
  LABEL="Revenue code 30 (as received from source)"                             
                                                                                
  REVCD31                    LENGTH=$4                                          
  LABEL="Revenue code 31 (as received from source)"                             
                                                                                
  REVCD32                    LENGTH=$4                                          
  LABEL="Revenue code 32 (as received from source)"                             
                                                                                
  REVCD33                    LENGTH=$4                                          
  LABEL="Revenue code 33 (as received from source)"                             
                                                                                
  REVCD34                    LENGTH=$4                                          
  LABEL="Revenue code 34 (as received from source)"                             
                                                                                
  REVCD35                    LENGTH=$4                                          
  LABEL="Revenue code 35 (as received from source)"                             
                                                                                
  REVCD36                    LENGTH=$4                                          
  LABEL="Revenue code 36 (as received from source)"                             
                                                                                
  REVCD37                    LENGTH=$4                                          
  LABEL="Revenue code 37 (as received from source)"                             
                                                                                
  REVCD38                    LENGTH=$4                                          
  LABEL="Revenue code 38 (as received from source)"                             
                                                                                
  REVCD39                    LENGTH=$4                                          
  LABEL="Revenue code 39 (as received from source)"                             
                                                                                
  REVCD40                    LENGTH=$4                                          
  LABEL="Revenue code 40 (as received from source)"                             
                                                                                
  REVCD41                    LENGTH=$4                                          
  LABEL="Revenue code 41 (as received from source)"                             
                                                                                
  REVCD42                    LENGTH=$4                                          
  LABEL="Revenue code 42 (as received from source)"                             
                                                                                
  REVCD43                    LENGTH=$4                                          
  LABEL="Revenue code 43 (as received from source)"                             
                                                                                
  REVCD44                    LENGTH=$4                                          
  LABEL="Revenue code 44 (as received from source)"                             
                                                                                
  REVCD45                    LENGTH=$4                                          
  LABEL="Revenue code 45 (as received from source)"                             
                                                                                
  REVCD46                    LENGTH=$4                                          
  LABEL="Revenue code 46 (as received from source)"                             
                                                                                
  REVCD47                    LENGTH=$4                                          
  LABEL="Revenue code 47 (as received from source)"                             
                                                                                
  REVCD48                    LENGTH=$4                                          
  LABEL="Revenue code 48 (as received from source)"                             
                                                                                
  REVCD49                    LENGTH=$4                                          
  LABEL="Revenue code 49 (as received from source)"                             
                                                                                
  REVCD50                    LENGTH=$4                                          
  LABEL="Revenue code 50 (as received from source)"                             
                                                                                
  REVCD51                    LENGTH=$4                                          
  LABEL="Revenue code 51 (as received from source)"                             
                                                                                
  REVCD52                    LENGTH=$4                                          
  LABEL="Revenue code 52 (as received from source)"                             
                                                                                
  REVCD53                    LENGTH=$4                                          
  LABEL="Revenue code 53 (as received from source)"                             
                                                                                
  REVCD54                    LENGTH=$4                                          
  LABEL="Revenue code 54 (as received from source)"                             
                                                                                
  REVCD55                    LENGTH=$4                                          
  LABEL="Revenue code 55 (as received from source)"                             
                                                                                
  REVCHG1                    LENGTH=6                                           
  LABEL="Detailed charges for revenue code 1 (as received from source)"         
                                                                                
  REVCHG2                    LENGTH=6                                           
  LABEL="Detailed charges for revenue code 2 (as received from source)"         
                                                                                
  REVCHG3                    LENGTH=6                                           
  LABEL="Detailed charges for revenue code 3 (as received from source)"         
                                                                                
  REVCHG4                    LENGTH=6                                           
  LABEL="Detailed charges for revenue code 4 (as received from source)"         
                                                                                
  REVCHG5                    LENGTH=6                                           
  LABEL="Detailed charges for revenue code 5 (as received from source)"         
                                                                                
  REVCHG6                    LENGTH=6                                           
  LABEL="Detailed charges for revenue code 6 (as received from source)"         
                                                                                
  REVCHG7                    LENGTH=6                                           
  LABEL="Detailed charges for revenue code 7 (as received from source)"         
                                                                                
  REVCHG8                    LENGTH=6                                           
  LABEL="Detailed charges for revenue code 8 (as received from source)"         
                                                                                
  REVCHG9                    LENGTH=6                                           
  LABEL="Detailed charges for revenue code 9 (as received from source)"         
                                                                                
  REVCHG10                   LENGTH=6                                           
  LABEL="Detailed charges for revenue code 10 (as received from source)"        
                                                                                
  REVCHG11                   LENGTH=6                                           
  LABEL="Detailed charges for revenue code 11 (as received from source)"        
                                                                                
  REVCHG12                   LENGTH=6                                           
  LABEL="Detailed charges for revenue code 12 (as received from source)"        
                                                                                
  REVCHG13                   LENGTH=6                                           
  LABEL="Detailed charges for revenue code 13 (as received from source)"        
                                                                                
  REVCHG14                   LENGTH=6                                           
  LABEL="Detailed charges for revenue code 14 (as received from source)"        
                                                                                
  REVCHG15                   LENGTH=6                                           
  LABEL="Detailed charges for revenue code 15 (as received from source)"        
                                                                                
  REVCHG16                   LENGTH=6                                           
  LABEL="Detailed charges for revenue code 16 (as received from source)"        
                                                                                
  REVCHG17                   LENGTH=6                                           
  LABEL="Detailed charges for revenue code 17 (as received from source)"        
                                                                                
  REVCHG18                   LENGTH=6                                           
  LABEL="Detailed charges for revenue code 18 (as received from source)"        
                                                                                
  REVCHG19                   LENGTH=6                                           
  LABEL="Detailed charges for revenue code 19 (as received from source)"        
                                                                                
  REVCHG20                   LENGTH=6                                           
  LABEL="Detailed charges for revenue code 20 (as received from source)"        
                                                                                
  REVCHG21                   LENGTH=6                                           
  LABEL="Detailed charges for revenue code 21 (as received from source)"        
                                                                                
  REVCHG22                   LENGTH=6                                           
  LABEL="Detailed charges for revenue code 22 (as received from source)"        
                                                                                
  REVCHG23                   LENGTH=6                                           
  LABEL="Detailed charges for revenue code 23 (as received from source)"        
                                                                                
  REVCHG24                   LENGTH=6                                           
  LABEL="Detailed charges for revenue code 24 (as received from source)"        
                                                                                
  REVCHG25                   LENGTH=6                                           
  LABEL="Detailed charges for revenue code 25 (as received from source)"        
                                                                                
  REVCHG26                   LENGTH=6                                           
  LABEL="Detailed charges for revenue code 26 (as received from source)"        
                                                                                
  REVCHG27                   LENGTH=6                                           
  LABEL="Detailed charges for revenue code 27 (as received from source)"        
                                                                                
  REVCHG28                   LENGTH=6                                           
  LABEL="Detailed charges for revenue code 28 (as received from source)"        
                                                                                
  REVCHG29                   LENGTH=6                                           
  LABEL="Detailed charges for revenue code 29 (as received from source)"        
                                                                                
  REVCHG30                   LENGTH=6                                           
  LABEL="Detailed charges for revenue code 30 (as received from source)"        
                                                                                
  REVCHG31                   LENGTH=6                                           
  LABEL="Detailed charges for revenue code 31 (as received from source)"        
                                                                                
  REVCHG32                   LENGTH=6                                           
  LABEL="Detailed charges for revenue code 32 (as received from source)"        
                                                                                
  REVCHG33                   LENGTH=6                                           
  LABEL="Detailed charges for revenue code 33 (as received from source)"        
                                                                                
  REVCHG34                   LENGTH=6                                           
  LABEL="Detailed charges for revenue code 34 (as received from source)"        
                                                                                
  REVCHG35                   LENGTH=6                                           
  LABEL="Detailed charges for revenue code 35 (as received from source)"        
                                                                                
  REVCHG36                   LENGTH=6                                           
  LABEL="Detailed charges for revenue code 36 (as received from source)"        
                                                                                
  REVCHG37                   LENGTH=6                                           
  LABEL="Detailed charges for revenue code 37 (as received from source)"        
                                                                                
  REVCHG38                   LENGTH=6                                           
  LABEL="Detailed charges for revenue code 38 (as received from source)"        
                                                                                
  REVCHG39                   LENGTH=6                                           
  LABEL="Detailed charges for revenue code 39 (as received from source)"        
                                                                                
  REVCHG40                   LENGTH=6                                           
  LABEL="Detailed charges for revenue code 40 (as received from source)"        
                                                                                
  REVCHG41                   LENGTH=6                                           
  LABEL="Detailed charges for revenue code 41 (as received from source)"        
                                                                                
  REVCHG42                   LENGTH=6                                           
  LABEL="Detailed charges for revenue code 42 (as received from source)"        
                                                                                
  REVCHG43                   LENGTH=6                                           
  LABEL="Detailed charges for revenue code 43 (as received from source)"        
                                                                                
  REVCHG44                   LENGTH=6                                           
  LABEL="Detailed charges for revenue code 44 (as received from source)"        
                                                                                
  REVCHG45                   LENGTH=6                                           
  LABEL="Detailed charges for revenue code 45 (as received from source)"        
                                                                                
  REVCHG46                   LENGTH=6                                           
  LABEL="Detailed charges for revenue code 46 (as received from source)"        
                                                                                
  REVCHG47                   LENGTH=6                                           
  LABEL="Detailed charges for revenue code 47 (as received from source)"        
                                                                                
  REVCHG48                   LENGTH=6                                           
  LABEL="Detailed charges for revenue code 48 (as received from source)"        
                                                                                
  REVCHG49                   LENGTH=6                                           
  LABEL="Detailed charges for revenue code 49 (as received from source)"        
                                                                                
  REVCHG50                   LENGTH=6                                           
  LABEL="Detailed charges for revenue code 50 (as received from source)"        
                                                                                
  REVCHG51                   LENGTH=6                                           
  LABEL="Detailed charges for revenue code 51 (as received from source)"        
                                                                                
  REVCHG52                   LENGTH=6                                           
  LABEL="Detailed charges for revenue code 52 (as received from source)"        
                                                                                
  REVCHG53                   LENGTH=6                                           
  LABEL="Detailed charges for revenue code 53 (as received from source)"        
                                                                                
  REVCHG54                   LENGTH=6                                           
  LABEL="Detailed charges for revenue code 54 (as received from source)"        
                                                                                
  REVCHG55                   LENGTH=6                                           
  LABEL="Detailed charges for revenue code 55 (as received from source)"        
                                                                                
  UNIT1                      LENGTH=4                                           
  LABEL="Units of service 1 (as received from source)"                          
                                                                                
  UNIT2                      LENGTH=4                                           
  LABEL="Units of service 2 (as received from source)"                          
                                                                                
  UNIT3                      LENGTH=4                                           
  LABEL="Units of service 3 (as received from source)"                          
                                                                                
  UNIT4                      LENGTH=4                                           
  LABEL="Units of service 4 (as received from source)"                          
                                                                                
  UNIT5                      LENGTH=4                                           
  LABEL="Units of service 5 (as received from source)"                          
                                                                                
  UNIT6                      LENGTH=4                                           
  LABEL="Units of service 6 (as received from source)"                          
                                                                                
  UNIT7                      LENGTH=4                                           
  LABEL="Units of service 7 (as received from source)"                          
                                                                                
  UNIT8                      LENGTH=4                                           
  LABEL="Units of service 8 (as received from source)"                          
                                                                                
  UNIT9                      LENGTH=4                                           
  LABEL="Units of service 9 (as received from source)"                          
                                                                                
  UNIT10                     LENGTH=4                                           
  LABEL="Units of service 10 (as received from source)"                         
                                                                                
  UNIT11                     LENGTH=4                                           
  LABEL="Units of service 11 (as received from source)"                         
                                                                                
  UNIT12                     LENGTH=4                                           
  LABEL="Units of service 12 (as received from source)"                         
                                                                                
  UNIT13                     LENGTH=4                                           
  LABEL="Units of service 13 (as received from source)"                         
                                                                                
  UNIT14                     LENGTH=4                                           
  LABEL="Units of service 14 (as received from source)"                         
                                                                                
  UNIT15                     LENGTH=4                                           
  LABEL="Units of service 15 (as received from source)"                         
                                                                                
  UNIT16                     LENGTH=4                                           
  LABEL="Units of service 16 (as received from source)"                         
                                                                                
  UNIT17                     LENGTH=4                                           
  LABEL="Units of service 17 (as received from source)"                         
                                                                                
  UNIT18                     LENGTH=4                                           
  LABEL="Units of service 18 (as received from source)"                         
                                                                                
  UNIT19                     LENGTH=4                                           
  LABEL="Units of service 19 (as received from source)"                         
                                                                                
  UNIT20                     LENGTH=4                                           
  LABEL="Units of service 20 (as received from source)"                         
                                                                                
  UNIT21                     LENGTH=4                                           
  LABEL="Units of service 21 (as received from source)"                         
                                                                                
  UNIT22                     LENGTH=4                                           
  LABEL="Units of service 22 (as received from source)"                         
                                                                                
  UNIT23                     LENGTH=4                                           
  LABEL="Units of service 23 (as received from source)"                         
                                                                                
  UNIT24                     LENGTH=4                                           
  LABEL="Units of service 24 (as received from source)"                         
                                                                                
  UNIT25                     LENGTH=4                                           
  LABEL="Units of service 25 (as received from source)"                         
                                                                                
  UNIT26                     LENGTH=4                                           
  LABEL="Units of service 26 (as received from source)"                         
                                                                                
  UNIT27                     LENGTH=4                                           
  LABEL="Units of service 27 (as received from source)"                         
                                                                                
  UNIT28                     LENGTH=4                                           
  LABEL="Units of service 28 (as received from source)"                         
                                                                                
  UNIT29                     LENGTH=4                                           
  LABEL="Units of service 29 (as received from source)"                         
                                                                                
  UNIT30                     LENGTH=4                                           
  LABEL="Units of service 30 (as received from source)"                         
                                                                                
  UNIT31                     LENGTH=4                                           
  LABEL="Units of service 31 (as received from source)"                         
                                                                                
  UNIT32                     LENGTH=4                                           
  LABEL="Units of service 32 (as received from source)"                         
                                                                                
  UNIT33                     LENGTH=4                                           
  LABEL="Units of service 33 (as received from source)"                         
                                                                                
  UNIT34                     LENGTH=4                                           
  LABEL="Units of service 34 (as received from source)"                         
                                                                                
  UNIT35                     LENGTH=4                                           
  LABEL="Units of service 35 (as received from source)"                         
                                                                                
  UNIT36                     LENGTH=4                                           
  LABEL="Units of service 36 (as received from source)"                         
                                                                                
  UNIT37                     LENGTH=4                                           
  LABEL="Units of service 37 (as received from source)"                         
                                                                                
  UNIT38                     LENGTH=4                                           
  LABEL="Units of service 38 (as received from source)"                         
                                                                                
  UNIT39                     LENGTH=4                                           
  LABEL="Units of service 39 (as received from source)"                         
                                                                                
  UNIT40                     LENGTH=4                                           
  LABEL="Units of service 40 (as received from source)"                         
                                                                                
  UNIT41                     LENGTH=4                                           
  LABEL="Units of service 41 (as received from source)"                         
                                                                                
  UNIT42                     LENGTH=4                                           
  LABEL="Units of service 42 (as received from source)"                         
                                                                                
  UNIT43                     LENGTH=4                                           
  LABEL="Units of service 43 (as received from source)"                         
                                                                                
  UNIT44                     LENGTH=4                                           
  LABEL="Units of service 44 (as received from source)"                         
                                                                                
  UNIT45                     LENGTH=4                                           
  LABEL="Units of service 45 (as received from source)"                         
                                                                                
  UNIT46                     LENGTH=4                                           
  LABEL="Units of service 46 (as received from source)"                         
                                                                                
  UNIT47                     LENGTH=4                                           
  LABEL="Units of service 47 (as received from source)"                         
                                                                                
  UNIT48                     LENGTH=4                                           
  LABEL="Units of service 48 (as received from source)"                         
                                                                                
  UNIT49                     LENGTH=4                                           
  LABEL="Units of service 49 (as received from source)"                         
                                                                                
  UNIT50                     LENGTH=4                                           
  LABEL="Units of service 50 (as received from source)"                         
                                                                                
  UNIT51                     LENGTH=4                                           
  LABEL="Units of service 51 (as received from source)"                         
                                                                                
  UNIT52                     LENGTH=4                                           
  LABEL="Units of service 52 (as received from source)"                         
                                                                                
  UNIT53                     LENGTH=4                                           
  LABEL="Units of service 53 (as received from source)"                         
                                                                                
  UNIT54                     LENGTH=4                                           
  LABEL="Units of service 54 (as received from source)"                         
                                                                                
  UNIT55                     LENGTH=4                                           
  LABEL="Units of service 55 (as received from source)"                         
  ;                                                                             
                                                                                
                                                                                
*** Input the variables from the ASCII file ***;                                
INPUT                                                                           
      @1      KEY                      15.                                      
      @16     NREVCD                   N2PF.                                    
      @18     REVCD1                   $CHAR4.                                  
      @22     REVCD2                   $CHAR4.                                  
      @26     REVCD3                   $CHAR4.                                  
      @30     REVCD4                   $CHAR4.                                  
      @34     REVCD5                   $CHAR4.                                  
      @38     REVCD6                   $CHAR4.                                  
      @42     REVCD7                   $CHAR4.                                  
      @46     REVCD8                   $CHAR4.                                  
      @50     REVCD9                   $CHAR4.                                  
      @54     REVCD10                  $CHAR4.                                  
      @58     REVCD11                  $CHAR4.                                  
      @62     REVCD12                  $CHAR4.                                  
      @66     REVCD13                  $CHAR4.                                  
      @70     REVCD14                  $CHAR4.                                  
      @74     REVCD15                  $CHAR4.                                  
      @78     REVCD16                  $CHAR4.                                  
      @82     REVCD17                  $CHAR4.                                  
      @86     REVCD18                  $CHAR4.                                  
      @90     REVCD19                  $CHAR4.                                  
      @94     REVCD20                  $CHAR4.                                  
      @98     REVCD21                  $CHAR4.                                  
      @102    REVCD22                  $CHAR4.                                  
      @106    REVCD23                  $CHAR4.                                  
      @110    REVCD24                  $CHAR4.                                  
      @114    REVCD25                  $CHAR4.                                  
      @118    REVCD26                  $CHAR4.                                  
      @122    REVCD27                  $CHAR4.                                  
      @126    REVCD28                  $CHAR4.                                  
      @130    REVCD29                  $CHAR4.                                  
      @134    REVCD30                  $CHAR4.                                  
      @138    REVCD31                  $CHAR4.                                  
      @142    REVCD32                  $CHAR4.                                  
      @146    REVCD33                  $CHAR4.                                  
      @150    REVCD34                  $CHAR4.                                  
      @154    REVCD35                  $CHAR4.                                  
      @158    REVCD36                  $CHAR4.                                  
      @162    REVCD37                  $CHAR4.                                  
      @166    REVCD38                  $CHAR4.                                  
      @170    REVCD39                  $CHAR4.                                  
      @174    REVCD40                  $CHAR4.                                  
      @178    REVCD41                  $CHAR4.                                  
      @182    REVCD42                  $CHAR4.                                  
      @186    REVCD43                  $CHAR4.                                  
      @190    REVCD44                  $CHAR4.                                  
      @194    REVCD45                  $CHAR4.                                  
      @198    REVCD46                  $CHAR4.                                  
      @202    REVCD47                  $CHAR4.                                  
      @206    REVCD48                  $CHAR4.                                  
      @210    REVCD49                  $CHAR4.                                  
      @214    REVCD50                  $CHAR4.                                  
      @218    REVCD51                  $CHAR4.                                  
      @222    REVCD52                  $CHAR4.                                  
      @226    REVCD53                  $CHAR4.                                  
      @230    REVCD54                  $CHAR4.                                  
      @234    REVCD55                  $CHAR4.                                  
      @238    REVCHG1                  N12P2F.                                  
      @250    REVCHG2                  N12P2F.                                  
      @262    REVCHG3                  N12P2F.                                  
      @274    REVCHG4                  N12P2F.                                  
      @286    REVCHG5                  N12P2F.                                  
      @298    REVCHG6                  N12P2F.                                  
      @310    REVCHG7                  N12P2F.                                  
      @322    REVCHG8                  N12P2F.                                  
      @334    REVCHG9                  N12P2F.                                  
      @346    REVCHG10                 N12P2F.                                  
      @358    REVCHG11                 N12P2F.                                  
      @370    REVCHG12                 N12P2F.                                  
      @382    REVCHG13                 N12P2F.                                  
      @394    REVCHG14                 N12P2F.                                  
      @406    REVCHG15                 N12P2F.                                  
      @418    REVCHG16                 N12P2F.                                  
      @430    REVCHG17                 N12P2F.                                  
      @442    REVCHG18                 N12P2F.                                  
      @454    REVCHG19                 N12P2F.                                  
      @466    REVCHG20                 N12P2F.                                  
      @478    REVCHG21                 N12P2F.                                  
      @490    REVCHG22                 N12P2F.                                  
      @502    REVCHG23                 N12P2F.                                  
      @514    REVCHG24                 N12P2F.                                  
      @526    REVCHG25                 N12P2F.                                  
      @538    REVCHG26                 N12P2F.                                  
      @550    REVCHG27                 N12P2F.                                  
      @562    REVCHG28                 N12P2F.                                  
      @574    REVCHG29                 N12P2F.                                  
      @586    REVCHG30                 N12P2F.                                  
      @598    REVCHG31                 N12P2F.                                  
      @610    REVCHG32                 N12P2F.                                  
      @622    REVCHG33                 N12P2F.                                  
      @634    REVCHG34                 N12P2F.                                  
      @646    REVCHG35                 N12P2F.                                  
      @658    REVCHG36                 N12P2F.                                  
      @670    REVCHG37                 N12P2F.                                  
      @682    REVCHG38                 N12P2F.                                  
      @694    REVCHG39                 N12P2F.                                  
      @706    REVCHG40                 N12P2F.                                  
      @718    REVCHG41                 N12P2F.                                  
      @730    REVCHG42                 N12P2F.                                  
      @742    REVCHG43                 N12P2F.                                  
      @754    REVCHG44                 N12P2F.                                  
      @766    REVCHG45                 N12P2F.                                  
      @778    REVCHG46                 N12P2F.                                  
      @790    REVCHG47                 N12P2F.                                  
      @802    REVCHG48                 N12P2F.                                  
      @814    REVCHG49                 N12P2F.                                  
      @826    REVCHG50                 N12P2F.                                  
      @838    REVCHG51                 N12P2F.                                  
      @850    REVCHG52                 N12P2F.                                  
      @862    REVCHG53                 N12P2F.                                  
      @874    REVCHG54                 N12P2F.                                  
      @886    REVCHG55                 N12P2F.                                  
      @898    UNIT1                    N8P2F.                                   
      @906    UNIT2                    N8P2F.                                   
      @914    UNIT3                    N8P2F.                                   
      @922    UNIT4                    N8P2F.                                   
      @930    UNIT5                    N8P2F.                                   
      @938    UNIT6                    N8P2F.                                   
      @946    UNIT7                    N8P2F.                                   
      @954    UNIT8                    N8P2F.                                   
      @962    UNIT9                    N8P2F.                                   
      @970    UNIT10                   N8P2F.                                   
      @978    UNIT11                   N8P2F.                                   
      @986    UNIT12                   N8P2F.                                   
      @994    UNIT13                   N8P2F.                                   
      @1002   UNIT14                   N8P2F.                                   
      @1010   UNIT15                   N8P2F.                                   
      @1018   UNIT16                   N8P2F.                                   
      @1026   UNIT17                   N8P2F.                                   
      @1034   UNIT18                   N8P2F.                                   
      @1042   UNIT19                   N8P2F.                                   
      @1050   UNIT20                   N8P2F.                                   
      @1058   UNIT21                   N8P2F.                                   
      @1066   UNIT22                   N8P2F.                                   
      @1074   UNIT23                   N8P2F.                                   
      @1082   UNIT24                   N8P2F.                                   
      @1090   UNIT25                   N8P2F.                                   
      @1098   UNIT26                   N8P2F.                                   
      @1106   UNIT27                   N8P2F.                                   
      @1114   UNIT28                   N8P2F.                                   
      @1122   UNIT29                   N8P2F.                                   
      @1130   UNIT30                   N8P2F.                                   
      @1138   UNIT31                   N8P2F.                                   
      @1146   UNIT32                   N8P2F.                                   
      @1154   UNIT33                   N8P2F.                                   
      @1162   UNIT34                   N8P2F.                                   
      @1170   UNIT35                   N8P2F.                                   
      @1178   UNIT36                   N8P2F.                                   
      @1186   UNIT37                   N8P2F.                                   
      @1194   UNIT38                   N8P2F.                                   
      @1202   UNIT39                   N8P2F.                                   
      @1210   UNIT40                   N8P2F.                                   
      @1218   UNIT41                   N8P2F.                                   
      @1226   UNIT42                   N8P2F.                                   
      @1234   UNIT43                   N8P2F.                                   
      @1242   UNIT44                   N8P2F.                                   
      @1250   UNIT45                   N8P2F.                                   
      @1258   UNIT46                   N8P2F.                                   
      @1266   UNIT47                   N8P2F.                                   
      @1274   UNIT48                   N8P2F.                                   
      @1282   UNIT49                   N8P2F.                                   
      @1290   UNIT50                   N8P2F.                                   
      @1298   UNIT51                   N8P2F.                                   
      @1306   UNIT52                   N8P2F.                                   
      @1314   UNIT53                   N8P2F.                                   
      @1322   UNIT54                   N8P2F.                                   
      @1330   UNIT55                   N8P2F.                                   
      ;                                                                         
                                                                                
                                                                                
RUN;
