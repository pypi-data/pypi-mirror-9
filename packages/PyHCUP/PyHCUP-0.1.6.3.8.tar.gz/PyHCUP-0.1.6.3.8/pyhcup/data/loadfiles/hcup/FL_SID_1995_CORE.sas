DATA FL95CORE; 
INFILE EBCORE LRECL = 344; 

LENGTH 
       SEQ_SID  7
       YEAR     3
       DSHOSPID $13
       DSTYPE   3
       HOSPST   $2
       MDID_S   $16
       SURGID_S $16
       AGE      3
       SEX      3
       RACE     3
       DQTR     3
       LOS      3
       LOS_X    4
       DISP     3
       DIED     3
       NEOMAT   3
       ATYPE    3
       ASOURCE  3
       DXSYS    3
       DSNDX    3
       NDX      3
       DX1      $5
       DX2      $5
       DX3      $5
       DX4      $5
       DX5      $5
       DX6      $5
       DX7      $5
       DX8      $5
       DX9      $5
       DX10     $5
       DXV1     3
       DXV2     3
       DXV3     3
       DXV4     3
       DXV5     3
       DXV6     3
       DXV7     3
       DXV8     3
       DXV9     3
       DXV10    3
       DCCHPR1  3
       DCCHPR2  3
       DCCHPR3  3
       DCCHPR4  3
       DCCHPR5  3
       DCCHPR6  3
       DCCHPR7  3
       DCCHPR8  3
       DCCHPR9  3
       DCCHPR10 3
       PRSYS    3
       DSNPR    3
       NPR      3
       PR1      $4
       PR2      $4
       PR3      $4
       PR4      $4
       PR5      $4
       PR6      $4
       PR7      $4
       PR8      $4
       PR9      $4
       PR10     $4
       PRV1     3
       PRV2     3
       PRV3     3
       PRV4     3
       PRV5     3
       PRV6     3
       PRV7     3
       PRV8     3
       PRV9     3
       PRV10    3
       PCCHPR1  3
       PCCHPR2  3
       PCCHPR3  3
       PCCHPR4  3
       PCCHPR5  3
       PCCHPR6  3
       PCCHPR7  3
       PCCHPR8  3
       PCCHPR9  3
       PCCHPR10 3
       PRDAY1   3
       DRG      3
       MDC      3
       DRGVER   3
       DRG10    3
       MDC10    3
       PAY1     3
       PAY1_N   3
       TOTCHG   6
       TOTCHG_X 7
       HOSPID   4
;


LABEL 
      SEQ_SID ='I:HCUP SID record sequence number'
      YEAR    ='Calendar year'
      DSHOSPID='I:Data source hospital ID number'
      DSTYPE  ='I:Data source type'
      HOSPST  ='Hospital state postal code'
      MDID_S  ='I:Attending physician number (synthetic)'
      SURGID_S='I:Primary surgeon number (synthetic)'
      AGE     ='I:Age in years at admission'
      SEX     ='I:Sex'
      RACE    ='I:Race'
      DQTR    ='I:Discharge quarter'
      LOS     ='I:Length of stay (cleaned)'
      LOS_X   ='I:Length of stay (uncleaned)'
      DISP    ='I:Disposition of patient'
      DIED    ='I:Died during hospitalization'
      NEOMAT  ='I:Neonatal and/or maternal DX and/or PR'
      ATYPE   ='I:Admission type'
      ASOURCE ='I:Admission source'
      DXSYS   ='I:Diagnosis coding system'
      DSNDX   ='I:Max number of diagnoses from source'
      NDX     ='I:Number of diagnoses on this discharge'
      DX1     ='I:Principal diagnosis'
      DX2     ='I:Diagnosis 2'
      DX3     ='I:Diagnosis 3'
      DX4     ='I:Diagnosis 4'
      DX5     ='I:Diagnosis 5'
      DX6     ='I:Diagnosis 6'
      DX7     ='I:Diagnosis 7'
      DX8     ='I:Diagnosis 8'
      DX9     ='I:Diagnosis 9'
      DX10    ='I:Diagnosis 10'
      DXV1    ='I:Validity flag: principal diagnosis'
      DXV2    ='I:Validity flag: diagnosis 2'
      DXV3    ='I:Validity flag: diagnosis 3'
      DXV4    ='I:Validity flag: diagnosis 4'
      DXV5    ='I:Validity flag: diagnosis 5'
      DXV6    ='I:Validity flag: diagnosis 6'
      DXV7    ='I:Validity flag: diagnosis 7'
      DXV8    ='I:Validity flag: diagnosis 8'
      DXV9    ='I:Validity flag: diagnosis 9'
      DXV10   ='I:Validity flag: diagnosis 10'
      DCCHPR1 ='I:CCHPR: principal diagnosis'
      DCCHPR2 ='I:CCHPR: diagnosis 2'
      DCCHPR3 ='I:CCHPR: diagnosis 3'
      DCCHPR4 ='I:CCHPR: diagnosis 4'
      DCCHPR5 ='I:CCHPR: diagnosis 5'
      DCCHPR6 ='I:CCHPR: diagnosis 6'
      DCCHPR7 ='I:CCHPR: diagnosis 7'
      DCCHPR8 ='I:CCHPR: diagnosis 8'
      DCCHPR9 ='I:CCHPR: diagnosis 9'
      DCCHPR10='I:CCHPR: diagnosis 10'
      PRSYS   ='I:Procedure coding system'
      DSNPR   ='I:Max number of procedures from source'
      NPR     ='I:Number of procedures on this discharge'
      PR1     ='I:Principal procedure'
      PR2     ='I:Procedure 2'
      PR3     ='I:Procedure 3'
      PR4     ='I:Procedure 4'
      PR5     ='I:Procedure 5'
      PR6     ='I:Procedure 6'
      PR7     ='I:Procedure 7'
      PR8     ='I:Procedure 8'
      PR9     ='I:Procedure 9'
      PR10    ='I:Procedure 10'
      PRV1    ='I:Validity flag: principal procedure'
      PRV2    ='I:Validity flag: procedure 2'
      PRV3    ='I:Validity flag: procedure 3'
      PRV4    ='I:Validity flag: procedure 4'
      PRV5    ='I:Validity flag: procedure 5'
      PRV6    ='I:Validity flag: procedure 6'
      PRV7    ='I:Validity flag: procedure 7'
      PRV8    ='I:Validity flag: procedure 8'
      PRV9    ='I:Validity flag: procedure 9'
      PRV10   ='I:Validity flag: procedure 10'
      PCCHPR1 ='I:CCHPR: principal procedure'
      PCCHPR2 ='I:CCHPR: procedure 2'
      PCCHPR3 ='I:CCHPR: procedure 3'
      PCCHPR4 ='I:CCHPR: procedure 4'
      PCCHPR5 ='I:CCHPR: procedure 5'
      PCCHPR6 ='I:CCHPR: procedure 6'
      PCCHPR7 ='I:CCHPR: procedure 7'
      PCCHPR8 ='I:CCHPR: procedure 8'
      PCCHPR9 ='I:CCHPR: procedure 9'
      PCCHPR10='I:CCHPR: procedure 10'
      PRDAY1  ='I:No. of days from admission to PR1'
      DRG     ='I:DRG in effect on discharge date'
      MDC     ='I:MDC in effect on discharge date'
      DRGVER  ='I:DRG grouper version used on disch date'
      DRG10   ='I:DRG, Version 10'
      MDC10   ='I:MDC, Version 10'
      PAY1    ='I:Primary expected payer, uniform'
      PAY1_N  ='I:Primary expected payer, nonuniform'
      TOTCHG  ='I:Total charges (cleaned)'
      TOTCHG_X='I:Total charges (from data source)'
      HOSPID  ='HCUP hospital ID number (SSHHH)'
;


FORMAT
       SEQ_SID   Z13.
       HOSPID    Z5.
;


INPUT 
      @1      SEQ_SID   13.
      @14     YEAR      N2PF.
      @16     DSHOSPID  $CHAR13.
      @29     DSTYPE    1.
      @30     HOSPST    $CHAR2.
      @32     MDID_S    $CHAR16.
      @48     SURGID_S  $CHAR16.
      @64     AGE       N3PF.
      @67     SEX       N2PF.
      @69     RACE      N2PF.
      @71     DQTR      1.
      @72     LOS       N5PF.
      @77     LOS_X     N6PF.
      @83     DISP      N2PF.
      @85     DIED      N2PF.
      @87     NEOMAT    1.
      @88     ATYPE     N2PF.
      @90     ASOURCE   N2PF.
      @92     DXSYS     N2PF.
      @94     DSNDX     N2PF.
      @96     NDX       N2PF.
      @98     DX1       $CHAR5.
      @103    DX2       $CHAR5.
      @108    DX3       $CHAR5.
      @113    DX4       $CHAR5.
      @118    DX5       $CHAR5.
      @123    DX6       $CHAR5.
      @128    DX7       $CHAR5.
      @133    DX8       $CHAR5.
      @138    DX9       $CHAR5.
      @143    DX10      $CHAR5.
      @148    DXV1      N2PF.
      @150    DXV2      N2PF.
      @152    DXV3      N2PF.
      @154    DXV4      N2PF.
      @156    DXV5      N2PF.
      @158    DXV6      N2PF.
      @160    DXV7      N2PF.
      @162    DXV8      N2PF.
      @164    DXV9      N2PF.
      @166    DXV10     N2PF.
      @168    DCCHPR1   N3PF.
      @171    DCCHPR2   N3PF.
      @174    DCCHPR3   N3PF.
      @177    DCCHPR4   N3PF.
      @180    DCCHPR5   N3PF.
      @183    DCCHPR6   N3PF.
      @186    DCCHPR7   N3PF.
      @189    DCCHPR8   N3PF.
      @192    DCCHPR9   N3PF.
      @195    DCCHPR10  N3PF.
      @198    PRSYS     N2PF.
      @200    DSNPR     N2PF.
      @202    NPR       N2PF.
      @204    PR1       $CHAR4.
      @208    PR2       $CHAR4.
      @212    PR3       $CHAR4.
      @216    PR4       $CHAR4.
      @220    PR5       $CHAR4.
      @224    PR6       $CHAR4.
      @228    PR7       $CHAR4.
      @232    PR8       $CHAR4.
      @236    PR9       $CHAR4.
      @240    PR10      $CHAR4.
      @244    PRV1      N2PF.
      @246    PRV2      N2PF.
      @248    PRV3      N2PF.
      @250    PRV4      N2PF.
      @252    PRV5      N2PF.
      @254    PRV6      N2PF.
      @256    PRV7      N2PF.
      @258    PRV8      N2PF.
      @260    PRV9      N2PF.
      @262    PRV10     N2PF.
      @264    PCCHPR1   N3PF.
      @267    PCCHPR2   N3PF.
      @270    PCCHPR3   N3PF.
      @273    PCCHPR4   N3PF.
      @276    PCCHPR5   N3PF.
      @279    PCCHPR6   N3PF.
      @282    PCCHPR7   N3PF.
      @285    PCCHPR8   N3PF.
      @288    PCCHPR9   N3PF.
      @291    PCCHPR10  N3PF.
      @294    PRDAY1    N5PF.
      @299    DRG       N3PF.
      @302    MDC       N2PF.
      @304    DRGVER    N2PF.
      @306    DRG10     N3PF.
      @309    MDC10     N2PF.
      @311    PAY1      N2PF.
      @313    PAY1_N    N2PF.
      @315    TOTCHG    N10PF.
      @325    TOTCHG_X  N15P2F.
      @340    HOSPID    N5PF.
;


