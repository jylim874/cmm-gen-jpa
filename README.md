# 📚 cmm-gen-jpa DB 설계 표준 가이드
본 문서는 `cmm-gen-jpa` (Spring Boot + JPA 자동 코드 생성기)의 효율성을 극대화하고, 최신 실무 JPA 아키텍처에 맞는 객체지향적 DB 설계를 위해 작성된 **데이터베이스 설계 방법론**입니다.
이 가이드라인을 준수하여 DB를 설계하면, 제너레이터가 복잡한 예외 처리 없이 완벽한 형태의 `Entity`, `Repository(QueryDSL)`, `Service`, `Controller` 코드를 자동으로 생성해 냅니다.

---

## 1. 명명 규칙 (Naming Convention)

가장 핵심적인 원칙은 **"이해하기 어려운 약어를 배제하고, 의미가 명확한 풀네임(Full Name)을 사용하는 것"**입니다. 

* **기본 표기법:** DB 테이블 및 컬럼명은 모두 소문자 `snake_case`를 사용합니다. (제너레이터가 자동으로 `CamelCase` 및 `PascalCase`로 변환합니다.)
* **약어 금지:** * ❌ `mbr_nm`, `reg_dt`
  * ⭕ `member_name`, `registration_date`
* **타입별 명명 룰:**
  * **Boolean:** 상태를 나타내는 `is_` 또는 `has_` 접두사를 사용합니다. (예: `is_active`, `has_discount`)
  * **Date / Time:** 날짜는 `_date` (예: `birth_date`), 일시는 `_at` (예: `created_at`) 접미사를 사용합니다.

## 2. 식별자 및 관계 설계 (ID & Relation)

JPA 환경에서 복합키(Composite Key) 사용은 엔티티 구조를 기하급수적으로 복잡하게 만듭니다. 이를 방지하기 위해 **단일 대리키 원칙**을 엄격히 적용합니다.

* **기본키 (PK):** * 모든 테이블(연결 테이블 포함)의 PK는 **`id`**라는 단일 컬럼으로 통일합니다.
  * 데이터 타입은 `BIGINT` (`BIGSERIAL` / `AUTO_INCREMENT`) 사용을 권장합니다.
  * 중복 방지가 필요한 경우 복합키 대신 **Unique Index (유니크 제약조건)**를 활용합니다.
* **외래키 (FK):**
  * `[대상_테이블명]_id` 규칙을 엄격하게 따릅니다. (예: 대상이 `user_account`라면 FK는 `user_account_id`)
  * 제너레이터는 컬럼명이 `_id`로 끝나는 것을 감지하여 자동으로 JPA `@ManyToOne` 연관관계를 매핑합니다.

## 3. 테이블 역할 분리 (Master vs Mapping)

#### ※ 다대다(N:M) 관계를 해소하고 완벽한 일대다(1:N) 객체 매핑을 구현하기 위해 테이블의 역할을 2가지로 명확히 분리합니다.

### 🏢 정보 객체 (Master Table)
* 비즈니스의 핵심 데이터를 담는 독립 테이블입니다.
* 순수 명사(단수형)를 사용합니다. (예: `user_account`, `product`, `order`)

### 🔗 연결 객체 (Mapping Table)
* 두 정보 객체를 연결하는 테이블입니다. 단순한 '관계'를 넘어, 그 자체로 고유한 `id`를 가진 독립된 엔티티로 취급합니다.
* **명명 규칙:** `[기준테이블]_[대상테이블]_map` 형식을 사용합니다.
  * ⭕ `user_role_map`, `order_product_map`
* DB 툴에서 관련 도메인 테이블들이 알파벳 순으로 깔끔하게 정렬되는 효과를 얻을 수 있습니다.

## 4. 공통 감사 컬럼 (Audit Columns)

JPA의 `Auditing` 기능을 100% 활용하고 데이터 이력을 추적하기 위해 모든 테이블에 아래 컬럼을 필수로 구성합니다. (향후 제너레이터를 통해 `@MappedSuperclass` 기반의 `BaseEntity`로 자동 추출됩니다.)

* `created_at` (생성일시 - Timestamp/Datetime)
* `created_by` (생성자 ID - Varchar/Bigint)
* `updated_at` (수정일시 - Timestamp/Datetime)
* `updated_by` (수정자 ID - Varchar/Bigint)

**💡 논리 삭제 (Soft Delete):** 데이터 복구 및 무결성 유지를 위해 물리적 `DELETE` 대신 논리 삭제를 권장합니다. 이를 위해 `is_deleted` (Boolean) 컬럼을 기본으로 포함합니다.

---

## 🚀 제너레이터(cmm-gen-jpa) 파이프라인 연동 방식

이 가이드에 맞춰 스키마가 설계되면 제너레이터는 다음과 같이 동작합니다.

1. **스키마 추출:** DB 시스템 테이블에서 컬럼명, 타입, PK/FK, Nullable 여부, Comment 등을 읽어옵니다.
2. **동적 파싱:** * `tb_`, `sys_` 등의 불필요한 시스템 Prefix는 `settings.yaml` 설정을 참조하여 자동으로 제거합니다.
   * 별도의 단어 사전 DB(Standard Word DB) 없이 파이썬 내장 알고리즘으로 `CamelCase` 자동 변환을 수행합니다.
3. **코드 생성:** JPA `@Entity`, QueryDSL 적용 `Repository`, `Service`, `Controller` 등 REST API의 A to Z를 즉시 실행 가능한 형태로 생성합니다.