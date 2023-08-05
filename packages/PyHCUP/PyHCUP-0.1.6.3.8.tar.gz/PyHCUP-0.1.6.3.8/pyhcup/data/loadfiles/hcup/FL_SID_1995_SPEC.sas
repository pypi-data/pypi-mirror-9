DATA FL95SPEC; 
INFILE EBSPEC LRECL = 323; 

LENGTH 
       SEQ_SID  7
       PAY1_X   $17
       CHG1     6
       CHG2     6
       CHG3     6
       CHG4     6
       CHG5     6
       CHG6     6
       CHG7     6
       CHG8     6
       CHG9     6
       CHG10    6
       CHG11    6
       CHG12    6
       CHG13    6
       CHG14    6
       CHG15    6
       CHG16    6
       CHG17    6
       CHG18    6
       CHG19    6
       CHG20    6
       CHG21    6
       CHG22    6
       CHG23    6
       CHG24    6
       ZIP      $5
;


LABEL 
      SEQ_SID ='I:HCUP SID record sequence number'
      PAY1_X  ='I:Primary exp. payer (from data source)'
      CHG1    ='I:Detailed charges 1 (from data source)'
      CHG2    ='I:Detailed charges 2 (from data source)'
      CHG3    ='I:Detailed charges 3 (from data source)'
      CHG4    ='I:Detailed charges 4 (from data source)'
      CHG5    ='I:Detailed charges 5 (from data source)'
      CHG6    ='I:Detailed charges 6 (from data source)'
      CHG7    ='I:Detailed charges 7 (from data source)'
      CHG8    ='I:Detailed charges 8 (from data source)'
      CHG9    ='I:Detailed charges 9 (from data source)'
      CHG10   ='I:Detailed charges 10 (from data source)'
      CHG11   ='I:Detailed charges 11 (from data source)'
      CHG12   ='I:Detailed charges 12 (from data source)'
      CHG13   ='I:Detailed charges 13 (from data source)'
      CHG14   ='I:Detailed charges 14 (from data source)'
      CHG15   ='I:Detailed charges 15 (from data source)'
      CHG16   ='I:Detailed charges 16 (from data source)'
      CHG17   ='I:Detailed charges 17 (from data source)'
      CHG18   ='I:Detailed charges 18 (from data source)'
      CHG19   ='I:Detailed charges 19 (from data source)'
      CHG20   ='I:Detailed charges 20 (from data source)'
      CHG21   ='I:Detailed charges 21 (from data source)'
      CHG22   ='I:Detailed charges 22 (from data source)'
      CHG23   ='I:Detailed charges 23 (from data source)'
      CHG24   ='I:Detailed charges 24 (from data source)'
      ZIP     ='I:Patient zip code'
;


FORMAT
       SEQ_SID   Z13.
;


INPUT 
      @1      SEQ_SID   13.
      @14     PAY1_X    $CHAR17.
      @31     CHG1      N12P2F.
      @43     CHG2      N12P2F.
      @55     CHG3      N12P2F.
      @67     CHG4      N12P2F.
      @79     CHG5      N12P2F.
      @91     CHG6      N12P2F.
      @103    CHG7      N12P2F.
      @115    CHG8      N12P2F.
      @127    CHG9      N12P2F.
      @139    CHG10     N12P2F.
      @151    CHG11     N12P2F.
      @163    CHG12     N12P2F.
      @175    CHG13     N12P2F.
      @187    CHG14     N12P2F.
      @199    CHG15     N12P2F.
      @211    CHG16     N12P2F.
      @223    CHG17     N12P2F.
      @235    CHG18     N12P2F.
      @247    CHG19     N12P2F.
      @259    CHG20     N12P2F.
      @271    CHG21     N12P2F.
      @283    CHG22     N12P2F.
      @295    CHG23     N12P2F.
      @307    CHG24     N12P2F.
      @319    ZIP       $CHAR5.
;


