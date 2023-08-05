DATA UT_SIDC_1998_CORE; 
INFILE EBCORE LRECL = 284; 

LENGTH 
       KEY                 8
       ADRG                3
       ADRGSEV             3
       AGE                 3
       AGEDAY              3
       AGEMONTH            3
       AMONTH              3
       ASOURCE             3
       ASOURCE_X           $1
       ATYPE               3
       AWEEKEND            3
       DIED                3
       DISPUB92            3
       DISPUNIFORM         3
       DISP_X              $2
       DQTR                3
       DRG                 3
       DRG10               3
       DRG18               3
       DRGVER              3
       DSHOSPID            $13
       DX1                 $5
       DX2                 $5
       DX3                 $5
       DX4                 $5
       DX5                 $5
       DX6                 $5
       DX7                 $5
       DX8                 $5
       DX9                 $5
       DX10                $5
       DXCCS1              4
       DXCCS2              4
       DXCCS3              4
       DXCCS4              4
       DXCCS5              4
       DXCCS6              4
       DXCCS7              4
       DXCCS8              4
       DXCCS9              4
       DXCCS10             4
       FEMALE              3
       HOSPST              $2
       LOS                 4
       LOS_X               4
       MDC                 3
       MDC10               3
       MDC18               3
       NDX                 3
       NEOMAT              3
       NPR                 3
       PAY1                3
       PAY2                3
       PAY1_X              $2
       PAY2_X              $2
       PAY3_X              $2
       PR1                 $4
       PR2                 $4
       PR3                 $4
       PR4                 $4
       PR5                 $4
       PR6                 $4
       PRCCS1              3
       PRCCS2              3
       PRCCS3              3
       PRCCS4              3
       PRCCS5              3
       PRCCS6              3
       TOTCHG              6
       TOTCHG_X            7
       YEAR                3
       ZIP_S               $5
       AYEAR               3
       DMONTH              3
       BMONTH              3
       BYEAR               3
;


LABEL 
      KEY                 ='HCUP record identifier'
      ADRG                ='All Patient Refined DRG'
      ADRGSEV             ='All Patient Refined DRG severity level'
      AGE                 ='Age in years at admission'
      AGEDAY              ='Age in days (when age < 1 year)'
      AGEMONTH            ='Age in months (when age < 11 years)'
      AMONTH              ='Admission month'
      ASOURCE             ='Admission source (uniform)'
      ASOURCE_X           ='Admission source (as received from source)'
      ATYPE               ='Admission type'
      AWEEKEND            ='Admission day is a weekend'
      DIED                ='Died during hospitalization'
      DISPUB92            ='Disposition of patient (UB-92 standard coding)'
      DISPUNIFORM         ='Disposition of patient (uniform)'
      DISP_X              ='Disposition of patient (as received from source)'
      DQTR                ='Discharge quarter'
      DRG                 ='DRG in effect on discharge date'
      DRG10               ='DRG, version 10'
      DRG18               ='DRG, version 18'
      DRGVER              ='DRG grouper version used on discharge date'
      DSHOSPID            ='Data source hospital identifier'
      DX1                 ='Principal diagnosis'
      DX2                 ='Diagnosis 2'
      DX3                 ='Diagnosis 3'
      DX4                 ='Diagnosis 4'
      DX5                 ='Diagnosis 5'
      DX6                 ='Diagnosis 6'
      DX7                 ='Diagnosis 7'
      DX8                 ='Diagnosis 8'
      DX9                 ='Diagnosis 9'
      DX10                ='Diagnosis 10'
      DXCCS1              ='CCS: principal diagnosis'
      DXCCS2              ='CCS: diagnosis 2'
      DXCCS3              ='CCS: diagnosis 3'
      DXCCS4              ='CCS: diagnosis 4'
      DXCCS5              ='CCS: diagnosis 5'
      DXCCS6              ='CCS: diagnosis 6'
      DXCCS7              ='CCS: diagnosis 7'
      DXCCS8              ='CCS: diagnosis 8'
      DXCCS9              ='CCS: diagnosis 9'
      DXCCS10             ='CCS: diagnosis 10'
      FEMALE              ='Indicator of sex'
      HOSPST              ='Hospital state postal code'
      LOS                 ='Length of stay (cleaned)'
      LOS_X               ='Length of stay (uncleaned)'
      MDC                 ='MDC in effect on discharge date'
      MDC10               ='MDC, version 10'
      MDC18               ='MDC, version 18'
      NDX                 ='Number of diagnoses on this record'
      NEOMAT              ='Neonatal and/or maternal DX and/or PR'
      NPR                 ='Number of procedures on this record'
      PAY1                ='Primary expected payer (uniform)'
      PAY2                ='Secondary expected payer (uniform)'
      PAY1_X              ='Primary expected payer (as received from source)'
      PAY2_X              ='Secondary expected payer (as received from source)'
      PAY3_X              ='Tertiary expected payer (as received from source)'
      PR1                 ='Principal procedure'
      PR2                 ='Procedure 2'
      PR3                 ='Procedure 3'
      PR4                 ='Procedure 4'
      PR5                 ='Procedure 5'
      PR6                 ='Procedure 6'
      PRCCS1              ='CCS: principal procedure'
      PRCCS2              ='CCS: procedure 2'
      PRCCS3              ='CCS: procedure 3'
      PRCCS4              ='CCS: procedure 4'
      PRCCS5              ='CCS: procedure 5'
      PRCCS6              ='CCS: procedure 6'
      TOTCHG              ='Total charges (cleaned)'
      TOTCHG_X            ='Total charges (as received from source)'
      YEAR                ='Calendar year'
      ZIP_S               ='Patient zip code (synthetic)'
      AYEAR               ='Admission year'
      DMONTH              ='Discharge month'
      BMONTH              ='Birth month'
      BYEAR               ='Birth year'
;


FORMAT
       KEY                 Z14.
;


INPUT 
      @1      KEY                 14.
      @15     ADRG                N3PF.
      @18     ADRGSEV             N2PF.
      @20     AGE                 N3PF.
      @23     AGEDAY              N3PF.
      @26     AGEMONTH            N3PF.
      @29     AMONTH              N2PF.
      @31     ASOURCE             N2PF.
      @33     ASOURCE_X           $CHAR1.
      @34     ATYPE               N2PF.
      @36     AWEEKEND            N2PF.
      @38     DIED                N2PF.
      @40     DISPUB92            N2PF.
      @42     DISPUNIFORM         N2PF.
      @44     DISP_X              $CHAR2.
      @46     DQTR                1.
      @47     DRG                 N3PF.
      @50     DRG10               N3PF.
      @53     DRG18               N3PF.
      @56     DRGVER              N2PF.
      @58     DSHOSPID            $CHAR13.
      @71     DX1                 $CHAR5.
      @76     DX2                 $CHAR5.
      @81     DX3                 $CHAR5.
      @86     DX4                 $CHAR5.
      @91     DX5                 $CHAR5.
      @96     DX6                 $CHAR5.
      @101    DX7                 $CHAR5.
      @106    DX8                 $CHAR5.
      @111    DX9                 $CHAR5.
      @116    DX10                $CHAR5.
      @121    DXCCS1              N4PF.
      @125    DXCCS2              N4PF.
      @129    DXCCS3              N4PF.
      @133    DXCCS4              N4PF.
      @137    DXCCS5              N4PF.
      @141    DXCCS6              N4PF.
      @145    DXCCS7              N4PF.
      @149    DXCCS8              N4PF.
      @153    DXCCS9              N4PF.
      @157    DXCCS10             N4PF.
      @161    FEMALE              N2PF.
      @163    HOSPST              $CHAR2.
      @165    LOS                 N5PF.
      @170    LOS_X               N6PF.
      @176    MDC                 N2PF.
      @178    MDC10               N2PF.
      @180    MDC18               N2PF.
      @182    NDX                 N2PF.
      @184    NEOMAT              1.
      @185    NPR                 N2PF.
      @187    PAY1                N2PF.
      @189    PAY2                N2PF.
      @191    PAY1_X              $CHAR2.
      @193    PAY2_X              $CHAR2.
      @195    PAY3_X              $CHAR2.
      @197    PR1                 $CHAR4.
      @201    PR2                 $CHAR4.
      @205    PR3                 $CHAR4.
      @209    PR4                 $CHAR4.
      @213    PR5                 $CHAR4.
      @217    PR6                 $CHAR4.
      @221    PRCCS1              N3PF.
      @224    PRCCS2              N3PF.
      @227    PRCCS3              N3PF.
      @230    PRCCS4              N3PF.
      @233    PRCCS5              N3PF.
      @236    PRCCS6              N3PF.
      @239    TOTCHG              N10PF.
      @249    TOTCHG_X            N15P2F.
      @264    YEAR                N4PF.
      @268    ZIP_S               $CHAR5.
      @273    AYEAR               N4PF.
      @277    DMONTH              N2PF.
      @279    BMONTH              N2PF.
      @281    BYEAR               N4PF.
;


