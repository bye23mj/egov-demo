SET ECHO OFF
SET FEEDBACK ON
WHENEVER SQLERROR CONTINUE;
CREATE OR REPLACE VIEW KOMSA.COMVNUSERMASTER (
    ESNTL_ID, USER_ID, PASSWORD, USER_NM, USER_ZIP,
    USER_ADRES, USER_EMAIL, GROUP_ID, USER_SE, ORGNZT_ID
) AS
    SELECT ESNTL_ID,
           MBER_ID            AS USER_ID,
           PASSWORD,
           MBER_NM            AS USER_NM,
           ZIP                AS USER_ZIP,
           ADRES              AS USER_ADRES,
           MBER_EMAIL_ADRES   AS USER_EMAIL,
           GROUP_ID,
           'GNR'              AS USER_SE,
           CAST(NULL AS VARCHAR2(20)) AS ORGNZT_ID
      FROM KOMSA.COMTNGNRLMBER
    UNION ALL
    SELECT ESNTL_ID,
           ENTRPRS_MBER_ID        AS USER_ID,
           ENTRPRS_MBER_PASSWORD  AS PASSWORD,
           CMPNY_NM               AS USER_NM,
           ZIP                    AS USER_ZIP,
           ADRES                  AS USER_ADRES,
           APPLCNT_EMAIL_ADRES    AS USER_EMAIL,
           GROUP_ID,
           'ENT'                  AS USER_SE,
           CAST(NULL AS VARCHAR2(20)) AS ORGNZT_ID
      FROM KOMSA.COMTNENTRPRSMBER
    UNION ALL
    SELECT ESNTL_ID,
           EMPLYR_ID          AS USER_ID,
           PASSWORD,
           USER_NM,
           ZIP                AS USER_ZIP,
           HOUSE_ADRES        AS USER_ADRES,
           EMAIL_ADRES        AS USER_EMAIL,
           GROUP_ID,
           'EMP'              AS USER_SE,
           ORGNZT_ID
      FROM KOMSA.COMTNEMPLYRINFO;

COMMENT ON TABLE KOMSA.COMVNUSERMASTER IS '사용자마스터뷰: 일반회원/기업회원/업무사용자정보 통합 조회 뷰';
EXIT;
