# Crawling Engine (Python)

공공/민간 자격증 사이트의 정보를 자동 수집·정규화하여 **표준 JSON 산출물**을 생성하는 크롤링 엔진입니다.  
운영 관점에서 **실패 제어(타임아웃/재시도/스냅샷)와 로그 기반 재현/트러블슈팅**을 우선해 설계했습니다.

Pipeline: fetch → parse → normalize → output(JSON)

## 프로젝트 개요
- 자격증 정보가 여러 사이트에 분산되어 있어 관리가 어렵다는 문제에서 출발
- 공공/민간 자격증 데이터를 표준 JSON 구조로 통합
- 실패 제어와 재처리를 고려한 크롤링 파이프라인 설계

## 결과물
- 결과물은 별도의 작업 루트(`--root`) 아래에 생성됩니다.
  - 예: `Certificate_api/1320/1320.norm.json`


## 설계 포인트
- 공공(Q-Net) / 민간 사이트 **구조 차이를 파이프라인 수준에서 분리**해 확장성 확보
- adapter/util 계층으로 규칙을 분리해 **유지보수성과 데이터 품질**을 우선
- **타임아웃·재시도·스냅샷(HTML 저장)·중복 제거**로 실패 케이스 제어

## 코드 읽기 가이드
- `public_cert_api/` : 공공(Q-Net) 처리 러너
- `private-cert-crawl/` : 민간/사설 크롤러 모음

## 보안
- 쿠키/토큰/계정정보는 저장소에 커밋하지 않습니다. (`cookies.txt`, `.env` 등은 `.gitignore` 처리)
- 과도한 트래픽을 유발하지 않도록 요청 간격/재시도를 제한합니다.


---

## 상세 설계 배경 및 문제 해결 과정

### 1. 프로젝트 시작 배경

큐넷, 자격증넷 등 기존 자격증 사이트들은 일정, 시험 정보, CBT 기능이 각각 분산되어 있어,
사용자가 관심 있는 자격증만을 모아 한눈에 관리하기 어렵다는 불편함이 있었습니다.
팀원들과 논의한 끝에 자격증 일정·시험 정보·CBT·즐겨찾기 기능을 하나의 서비스로 통합해
제공하자는 결론에 도달했고, 이를 졸업작품 주제로 선정했습니다.

---

### 2. 문제 ① 크롤링 파이프라인 설계

가장 처음 마주한 문제는 크롤링 자체가 아니라,
**“인터넷에 흩어진 정보를 어떤 구조로 수집·정리할 것인가”**였습니다.

이에 따라  
fetch(HTML 수집) → parse(JSON 변환) → normalize(정규화 및 DB 적재)  
라는 공통 파이프라인을 기준으로 전체 구조를 설계했습니다.

또한 사이트별 HTML 규칙 차이를 흡수하기 위해 adapter 계층을 두고,
불필요한 문자 제거·빈 값 처리·형식 통일과 같은 공통 작업은
util 스크립트로 분리해 관리했습니다.

---

### 3. 문제 ② 공공·민간 자격증 데이터 구조 차이

공공 자격증(큐넷)과 민간 자격증 사이트는 데이터 구조와 신뢰도 측면에서 성격이 크게 달랐습니다.

이 문제를 해결하기 위해 공공 자격증과 민간 자격증을
동일한 규칙으로 처리하지 않고, 파이프라인 수준에서 분리하는 설계를 선택했습니다.

민간 자격증은 비교적 구조가 안정적인 만큼 자동화 비중을 높였고,
큐넷의 경우에는 자동화 가능한 영역과 수작업 검증이 필요한 영역을 구분해 접근했습니다.

그 결과 약 80~90% 수준의 데이터 정합성을 확보했고,
완벽한 자동화보다 운영 가능성과 데이터 품질을 우선하는 방향으로
구현 범위를 설정했습니다.


## 4. 문제 ③ 크롤링 엔진 활용
전체 서비스 중 **Core Crawling Engine(Python)** 부분을 전담하여 개발했습니다.  
Spring Boot와 **ProcessBuilder(CLI)** 방식으로 연동되며, 온디맨드(On-demand) 요청 시 실행됩니다.

```mermaid
flowchart LR
    User([사용자]) -->|1. 클릭 요청| Client["Frontend<br/>(React)"]
    Client -->|2. API 호출| Server["Backend<br/>(Spring Boot)"]
    
    subgraph "My Contribution (Core Engine)"
    Server == "3. CLI 실행 (ProcessBuilder)" ==> Python["🐍 Python Crawling Engine"]
    Python -->|4. 데이터 수집 & 파싱| Sites("대상 사이트<br/>(큐넷/민간 자격증 사이트)")
    end
    
    Python -- "5. 표준 JSON 반환" --> Server
    Server -->|6. 데이터 적재| DB[("DB<br/>(PostgreSQL)")]
    
    style Python fill:#f9f,stroke:#333,stroke-width:4px,color:black
    style Sites fill:#eee,stroke:#333,stroke-dasharray: 5 5
```

## 5. 멀티 플랫폼 지원 (Cross-platform Support) 

본 프로젝트는 개발 환경(Windows)과 운영 환경(Linux) 모두에서 동일하게 작동하도록 설계되었습니다. [cite: 2026-03-04]

| 항목 | 상세 내용 |
| :--- | :--- |
| **지원 OS** | Windows 10/11, Fedora Linux (Server) [cite: 2026-03-03, 2026-03-04] |
| **의존성 최적화** | `psycopg2-binary==2.9.11` 적용으로 OS별 라이브러리 충돌 해결 |
| **검증 완료** | 공공(Q-Net) 및 민간(KAIT) 자격증 데이터 정규화 테스트 통과 [cite: 2026-03-04] |

---

## 6. Linux 환경 설정 가이드 (Environment Setup)

## 1. Linux (Fedora 기준)
1. **시스템 패키지 설치**
   ```bash
   sudo dnf install gcc postgresql-devel
   ```

2. **가상환경 구축 및 의존성 설치**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **가상환경 활성화**
   ```bash
   source .venv/bin/activate
   ```

4. **엔진 실행 (공공 자격증)**
   ```bash
   python -m public_cert_api.run_public --root "$HOME/cert_data" --jmcd 1320 --mode http
   ```

5. **엔진 실행(민간 자격증)**
   ```bash
   python run_once.py --cert linux_master --config private-cert-crawl/configs/cert_map.yaml
   ```

## 6-2. Window  환경 설정 가이드 (Environment Setup)

## 1. Windows
1. **Python 설치**
   ```bash
   winget install Python.Python.3.11
   ```

2. **가상환경 구축 및 의존성 설치**
   ```bash
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```

3. **가상환경 활성화**
   ```bash
   .\.venv\Scripts\activate
   ```

4. **엔진 실행 (공공 자격증)**
   ```bash
   python -m public_cert_api.run_public --root "C:\cert_data" --jmcd 1320 --mode http
   ```

5. **엔진 실행(민간 자격증)**
   ```bash
   python run_once.py --cert linux_master --config private-cert-crawl/configs/cert_map.yaml
   ```
