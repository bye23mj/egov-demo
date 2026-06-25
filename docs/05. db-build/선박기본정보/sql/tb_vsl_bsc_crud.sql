-- TB_VSL_BSC 기본 CRUD (Oracle 11g, 바인드 변수 — SQL Injection 방지)
-- INSERT (인조키는 시퀀스 채번)
INSERT INTO TB_VSL_BSC (VSL_BSC_ID, DIV_NM, VSL_NO, VSL_NM, VSL_SE_NM, VSL_MTPRPT_NM, TOT_TON, LNCH_DE)
VALUES (SEQ_TB_VSL_BSC.NEXTVAL, :div_nm, :vsl_no, :vsl_nm, :vsl_se_nm, :vsl_mtprpt_nm, :tot_ton, TO_DATE(:lnch_de,'YYYY-MM-DD'));

-- SELECT (단건)
SELECT * FROM TB_VSL_BSC WHERE VSL_BSC_ID = :vsl_bsc_id;

-- SELECT (선박번호 조회 — 중복 가능)
SELECT VSL_BSC_ID, VSL_NO, VSL_NM, VSL_SE_NM, TOT_TON FROM TB_VSL_BSC WHERE VSL_NO = :vsl_no ORDER BY VSL_BSC_ID;

-- SELECT (페이징 — ROWNUM)
SELECT * FROM (
  SELECT a.*, ROWNUM rn FROM (
    SELECT VSL_BSC_ID, VSL_NO, VSL_NM, TOT_TON FROM TB_VSL_BSC ORDER BY VSL_BSC_ID
  ) a WHERE ROWNUM <= :end_row
) WHERE rn > :start_row;

-- UPDATE
UPDATE TB_VSL_BSC SET VSL_NM = :vsl_nm, TOT_TON = :tot_ton, LAYUP_YN = :layup_yn
WHERE VSL_BSC_ID = :vsl_bsc_id;

-- DELETE
DELETE FROM TB_VSL_BSC WHERE VSL_BSC_ID = :vsl_bsc_id;

COMMIT;
