-- =========================================================
-- TB_TCKT (티켓) 기본 CRUD — Oracle 11g
-- 바인드 변수(:param) 사용 (SQL Injection 방지)
-- =========================================================

-- 1) 목록조회 (ROWNUM 3중 페이징 + 선택적 상태/검색 조건)
SELECT * FROM (
  SELECT ROWNUM RN, A.* FROM (
    SELECT ID, TITLE, STATUS, PRIORITY, POSITION,
           PLANNED_START_DATE, DUE_DATE, STARTED_AT, COMPLETED_AT,
           CREATED_AT, UPDATED_AT
      FROM TB_TCKT
     WHERE 1=1
       AND (:status   IS NULL OR STATUS = :status)
       AND (:keyword  IS NULL OR TITLE LIKE '%' || :keyword || '%')
     ORDER BY STATUS, POSITION, ID
  ) A WHERE ROWNUM <= :lastIndex
) WHERE RN > :firstIndex;

-- 2) 단건조회 (PK)
SELECT ID, TITLE, DESCRIPTION, STATUS, PRIORITY, POSITION,
       PLANNED_START_DATE, DUE_DATE, STARTED_AT, COMPLETED_AT,
       CREATED_AT, UPDATED_AT
  FROM TB_TCKT
 WHERE ID = :id;

-- 3) 등록 (시퀀스 채번, 기본값은 DEFAULT 적용 컬럼 생략 가능)
INSERT INTO TB_TCKT (
  ID, TITLE, DESCRIPTION, STATUS, PRIORITY, POSITION,
  PLANNED_START_DATE, DUE_DATE
) VALUES (
  SEQ_TB_TCKT.NEXTVAL, :title, :description,
  NVL(:status, 'BACKLOG'), NVL(:priority, 'MEDIUM'), NVL(:position, 1),
  :plannedStartDate, :dueDate
);

-- 3-1) 채번된 ID 회수가 필요한 경우 (RETURNING)
-- INSERT INTO TB_TCKT (...) VALUES (SEQ_TB_TCKT.NEXTVAL, ...) RETURNING ID INTO :outId;

-- 4) 수정 (수정일시 자동 갱신)
UPDATE TB_TCKT
   SET TITLE              = :title,
       DESCRIPTION        = :description,
       STATUS             = :status,
       PRIORITY           = :priority,
       POSITION           = :position,
       PLANNED_START_DATE = :plannedStartDate,
       DUE_DATE           = :dueDate,
       STARTED_AT         = :startedAt,
       COMPLETED_AT       = :completedAt,
       UPDATED_AT         = SYSTIMESTAMP
 WHERE ID = :id;

-- 4-1) 상태 변경 (칸반 이동: 상태/순서 + 자동 시각 처리)
UPDATE TB_TCKT
   SET STATUS       = :status,
       POSITION     = :position,
       STARTED_AT   = CASE WHEN :status = 'TODO' AND STARTED_AT   IS NULL THEN SYSTIMESTAMP ELSE STARTED_AT   END,
       COMPLETED_AT = CASE WHEN :status = 'DONE' AND COMPLETED_AT IS NULL THEN SYSTIMESTAMP ELSE COMPLETED_AT END,
       UPDATED_AT   = SYSTIMESTAMP
 WHERE ID = :id;

-- 5) 삭제 (PK)
DELETE FROM TB_TCKT WHERE ID = :id;

-- 6) 총건수 (페이징용)
SELECT COUNT(*) AS TOT_CNT
  FROM TB_TCKT
 WHERE 1=1
   AND (:status  IS NULL OR STATUS = :status)
   AND (:keyword IS NULL OR TITLE LIKE '%' || :keyword || '%');
