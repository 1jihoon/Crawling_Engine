# Crawling Engine (Python)

공공/민간 자격증 사이트의 정보를 자동 수집·정규화하여 **표준 JSON 산출물**을 생성하는 크롤링 엔진입니다.  
운영 관점에서 **실패 제어(타임아웃/재시도/스냅샷)와 로그 기반 재현/트러블슈팅**을 우선해 설계했습니다.

Pipeline: fetch → parse → normalize → output(JSON)

## 👨‍💻 Core Contributions (기여도)
- **Lead Developer ([Lee_Jihoon])**: 
    - 프로젝트 전체 아키텍처 설계 및 핵심 크롤링 엔진 로직 구현 (전체 코드의 95% 이상 담당)
    - 600개 이상의 자격증 사이트 대응을 위한 다중 규칙 엔진 개발
    - Docker 기반 통합 인프라 및 운영 환경 구축 (PostgreSQL, Selenium Grid 최적화)

> [!IMPORTANT]
> ### 📢 Notice: Intellectual Property Protection (Patent Pending)
> * 본 프로젝트에 적용된 **'비정형 데이터 대응 다중 규칙 엔진'** 로직은 현재 **특허 출원 절차를 진행 중**에 있습니다.
> * 600개 이상의 자격증 사이트(Q-Net 등)의 각기 다른 구조를 통합 처리하는 독자적인 기술이 포함되어 있으며, 무단 도용 및 상업적 이용을 금합니다.

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
- `public_cert_api/` : 공공(Q-Net) 크롤러 모음
- `private-cert-crawl/` : 민간/사설 크롤러 모음

## 보안
- 쿠키/토큰/계정정보는 저장소에 커밋하지 않습니다. (`cookies.txt`, `.env` 등은 `.gitignore` 처리)
- 과도한 트래픽을 유발하지 않도록 요청 간격/재시도를 제한합니다.


---

## 상세 설계 배경 및 문제 해결 과정

### 1. 프로젝트 시작 배경

큐넷, 자격증넷 등 기존 자격증 사이트들은 일정, 시험 정보, CBT 기능이 각각 분산되어 있어,
사용자가 관심 있는 자격증만을 모아 한눈에 관리하기 어렵다는 불편함이 있었습니다.

그래서 팀원들과 논의한 끝에 단순히 정보를 모으는 것을 넘어 데이터를 정규화하고,
인프라를 직접 구축해보는 것을 겪어보고 싶은 바램을 바탕으로

자격증 일정·시험 정보·CBT·즐겨찾기 기능을 하나의 서비스로 통합해
제공하자는 결론에 도달했고, 이를 졸업작품 주제로 선정했습니다.

---

### 2. 문제 ① 크롤링 파이프라인 설계

가장 처음 마주한 문제는 크롤링 자체가 아니라,
**"인터넷에 흩어진 정보를 어떤 구조로 수집·정리할 것인가"**였습니다.

이에 따라  
**fetch(HTML 수집) → parse(JSON 변환) → normalize(정규화 및 DB 적재)**  
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

그 결과 약 **80~90%** 수준의 데이터 정합성을 확보했고,
완벽한 자동화보다 운영 가능성과 데이터 품질을 우선하는 방향으로
구현 범위를 설정했습니다.

모든 것을 자동화하고 싶단 큰 포부를 가지고 임했지만, 큐넷의 불규칙한 데이터 구조를 마주하고
고민한 끝에 **완벽한 자동화보단 데이터의 품질**이 우선이라 깨달았고, 그에 따라 복잡한 아키텍쳐 설계 과정에서 GPT와 치열하게 논의했습니다. AI가 바라는 효율적인 코드와 제가 생각하는 유지보수성 사이에서 균형을 맞추면 도구를 제어하고 최종 의사 결정을 내리는 엔지니어의 역할을 익혔습니다.



### 4. 문제 ③ 크롤링 엔진 활용
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

### 4-2. 문제 ④: 파싱 엔진 고도화 및 데이터 무결성 확보

9개의 민간 자격증과 큐넷의 공공 자격증 파이프라인의 데이터 정밀도와 시스템 성능을 개선하기 위해 진행한 리팩토링 과정입니다. 단순히 코드를 고치는 것을 넘어, 환경 간의 간섭을 최소화하고 데이터 품질을 표준화하는 데 집중했습니다.

* **현상 및 기술적 부채 (Technical Debt)**
   - **파싱 병목 현상**: 기존 html.parser 엔진이 대용량 DOM 구조를 처리할 때 발생하는 성능 저하 및 특수 태그 해석 오류 확인

   - **데이터 오염 잔존**: 공공/민간 사이트의 비정형 HTML 구조에서 유입되는 불필요한 태그, 특수문자, 비정상 공백이 최종 JSON 결과물에 포함되어 데이터 품질 저해

* **엔지니어링적 해결 (Engineering Solutions)**

   - **범용 파싱 엔진(lxml) 도입**: 공공/민간 크롤러 전체에 lxml 엔진을 전격 적용하여 파싱 속도를 최적화하고 예외적인 태그 구조에 대한 유연한 대응력 확보

   - **중앙 집중형 정제 모듈(민간) 구축**: engine_common/utils_text.py 내에 독립적인 sanitize_text 함수를 설계. 이를 통해 모든 하위 모듈이 동일한 정제 규칙을 따르도록 중앙 제어형 아키텍처 구현

   - **공공 파이프라인(Q-Net) 고도화**: 공공 자격증 핵심 로직인 parse_tabs_min.py 내에 sanitize_text를 통합 적용하여, 수십 개의 시험 탭에서 추출되는 텍스트의 품질을 일괄적으로 정규화 

   - **민간 파이프라인 전면 리팩토링**: 9개 민간 자격증 개별 크롤러의 get_text 옵션을 표준화하고, 2중 필터링 로직을 이식하여 산출물 데이터의 무결성(Data Integrity) 달성


* **점진적 리팩토링 전략 (Incremental Refactoring)**

  - **통합 표준화** : 서로 다른 구조를 가진 공공/민간 프로젝트가 engine_common 유틸리티를 공유하게 함으로써 **코드 중복 제거 및 유지보수성 극대화**

  - **환경 간 일관성 검증**: Fedora(Linux)와 Windows 환경 모두에서 동일한 정제 결과가 산출되도록 환경 종속성을 제거하고 전수 테스트 통과


**"단순한 크롤링을 넘어, 공공과 민간의 데이터 파이프라인을 하나의 정제 표준으로 통합함으로써 시스템의 확장성과 데이터 신뢰성을 동시에 확보했습니다."**


## 5. Docker 기반 통합 인프라 및 멀티 플랫폼 지원

본 프로젝트는 단순한 코드 구현을 넘어, **'어떤 환경에서도 즉시 배포 및 실행 가능한 엔진'**을 구축하기 위해 Docker 기반의 통합 인프라를 도입했습니다. 이를 통해 Windows와 Linux 사이의 환경 의존성 문제를 완벽히 해결했습니다. 

| 항목 | 상세 내용 |
| :--- | :--- |
| **지원 OS** | Windows 10/11 (Docker Desktop), Fedora Linux (Docker Engine) |
| **인프라 표준화** | Docker Image를 통한 라이브러리 파편화 및 `psycopg2-binary==2.9.11` 적용으로 OS별 라이브러리 충돌 해결 |
| **리소스 최적화** | Shared Memory (2GB) 할당으로 대용량 자격증 페이지 수집 안정성 확보 |
| **구조적 유연성** | Host Volume Binding을 통해 기존 폴더 구조를 유지하며 컨테이너와 데이터 동기화 |
| **검증 완료** | 공공(Q-Net) 및 민간(KAIT) 자격증 데이터 정규화 테스트 통과  |

* **주요 엔지니어링 의사결정 (Decision & Rationale)**
  - **설계의 일관성**: 프로젝트의 기존 폴더 및 파일 구조를 강제로 변경하지 않고, docker-compose.yml의 볼륨 매핑 기능을 정교하게 설계하여 호스트의 소스를 컨테이너 내부 경로로 직접 연결했습니다. 이는 개발 생산성을 유지하면서도 운영 환경의 독립성을 확보한 핵심 전략입니다.
  - **환경의 제약 극복**: 리눅스(Fedora) 환경의 엄격한 보안 정책(SELinux)을 고려하여 :Z 플래그를 도입했고, 크롬 브라우저의 고질적인 메모리 부족(Tab Crashed) 문제를 인프라 레벨(shm_size)에서 근본적으로 해결했습니다.

단순히 작동하는 코드가 아니라, 어떤 운영환경(LINUX)에서도 돌아가게 만드는 엔진에 집중했습니다.
특히 윈도우와 페도라 사이의 라이브러리 충돌(psycopg2-binary)을 해결하며, 인프라 환경에 따른 
의존성 관리의 중요성을 배웠습니다.

---

> **이 프로젝트는 단순히 데이터를 긁어오는 도구가 아닙니다. 윈도우에서 개발하고 리눅스 서버에 배포하는 실제 현업의 파이프라인을 Docker로 표준화하여, **'명령어 단 한 줄'**로 모든 가동이 가능하게 만든 엔지니어링의 결과물입니다."**


## 6. 데이터 수집 및 엔진 파이프라인 실행 과정

본 엔진이 민간 영역과 공공 영역의 서로 다른 도메인 타깃을 대상으로 데이터를 수집, 정제, 모니터링하는 전체 파이프라인 실증 자료입니다. 각 아키텍처는 대상 사이트의 특성에 맞춰 독립적으로 가동됩니다.

---

### 🔄 6-1. 크롤링 배치 가동 (Execution)
> **파이썬 기반의 데이터 수집 배치를 가동하는 단계입니다. 대상 도메인의 특성에 맞춰 최적화된 스크립트가 실행됩니다.**

#### 🔹 A. 민간 자격증 수집 엔진
![민간 크롤러 가동 화면](./images/private_crawling.png)
* **정형 데이터 추출**: 민간 자격증 일정 및 내용 페이지의 HTML 구조를 정밀 분석하여, 필요한 자격증 정보만을 정확하게 수집합니다.

#### 🏛️ B. 공공 자격증 수집 엔진
![공공 크롤러 가동 화면](./images/public_crawling.png)
* **대량 데이터 안정성:** 대량의 국가 자격증 데이터를 보유한 공공 플랫폼의 특성을 고려하여, 시스템에 과도한 부하를 주지 않고 차단을 방지하기 위해 요청 주기 제어 및 안정적인 세션 우회 메커니즘을 반영하여 안전하게 데이터를 수집합니다.

---

---

### 📄 6-2. 실시간 크롤링 로그 확인 (Runtime Log)
> **수집 프로세스가 진행되면서 실시간으로 컨테이너 및 파일 시스템에 기록되는 표준 출력(Stdout) 로그입니다.**

#### 🔹 A. 민간 수집 엔진 실시간 로그
![민간 크롤링 실시간 로그](./images/private_log.png)
* **정형화된 로깅:** 민간 자격증 내용,일정,수집 성공 여부가 구조화된 포맷으로 출력되어 정상 가동 상태를 실시간으로 증명합니다.

#### 🏛️ B. 공공 수집 엔진 실시간 로그
![공공 크롤링 실시간 로그](./images/public_log.png)
* **트래픽 및 응답 추적:** 큐넷의 각 탭별 성공 여부, 배치 스케줄링의 진행 상태를 실시간으로 인덱싱하며 누락 없는 로그 수집 기반을 확보합니다.

---

### 📦 6-3. 최종 정제 데이터 출력 (JSON Result)
> **수집 완료 후 데이터 누수 없이 최종적으로 정제(Parsing)되어 저장된 구조화 데이터 파일입니다.**

#### 🔹 A. 민간 데이터 최종 정제 결과물 (JSON)
![민간 최종 JSON 결과물](./images/private_norm.json.png)
* **데이터 모델링:** 민간 사이트의 비정형 가독 요소들을 분석 타깃에 맞게 키-밸류(Key-Value) 형태로 정밀 파싱하여 표준 `JSON` 포맷으로 구조화한 모습입니다.

#### 🏛️ B. 공공 데이터 최종 정제 결과물 (JSON)
![공공 최종 JSON 결과물](./images/public_norm.json.png)
* **표준 규격 정제:** 다양한 형태로 흩어져 있던 공공 기관의 기초 데이터들을 일관된 데이터 스키마 규칙에 맞춰 유실 없이 변환 및 영속화 완료한 모습입니다.

* **데이터 구조화:** 수집된 비정형 데이터들이 엔드포인트 및 가독성을 고려하여 표준 `JSON` 포맷으로 유실 없이 변환 및 저장 완료된 모습입니다.

---

### 📊 6-4. Prometheus 메트릭 수집 연동 (Metric Exporter)
> **정상적으로 종료된 배치 결과 및 수집 메트릭 데이터가 Prometheus 시계열 데이터베이스로 정상 인덱싱되는 모습입니다.**

![프로메테우스 메트릭 타깃](./images/prometheus.png)

* **시계열 데이터 변환:** 파이프라인의 성공률, 소요 시간 등의 메트릭이 익스포터(Exporter)를 통해 프로메테우스 가용 타깃으로 정상 스크래핑(Scraping)되고 있음을 증명합니다.

---


## 7. Prometheus & Loki 기반 통합 모니터링 및 로그 중앙화 구축

본 프로젝트가 프로덕션 환경(실제 운영 환경)에서 안정적으로 가동되는지 실시간으로 감시하고 예외 로그를 추적하기 위해 인프라 모니터링 시스템을 연동했습니다.

### 📊 7-1. 실시간 배치 가동 및 크롤링 성공률 대시보드 (Grafana)
> **배치 엔진의 작동 상태, 태스크별 성공/실패율, 시스템 자원(CPU/메모리) 소비량을 실시간 시각화한 대시보드 화면입니다.**

![자격증 모니터링 대시보드 실물](./images/dashboard.png)

* **도넛 차트 기반 메트릭 관제:** 수집된 자격증 스케줄 및 실시간 크롤러 배치 파이프라인의 성공률을 즉각적으로 파악할 수 있도록 타임시리즈 데이터를 도넛 형태로 인덱싱하여 구성했습니다.

---

### 💻 7-2. 분산 컨테이너 실시간 로그 수집 상태 (Loki & Promtail)
> **컨테이너 내부 및 파이프라인 전체에서 발생하는 다량의 텍스트 로그를 실시간으로 인덱싱하여 통합 관제하는 화면입니다.**

![배치 엔진 로그 시스템](./images/loki_log.png)

* **장애 추적 최적화:** 에러 발생 시 파일 서버에 일일이 접근할 필요 없이, Grafana 웹 콘솔 상에서 `error` 키워드 필터링을 통해 시스템 예외 원인을 초단위로 추적 및 디버깅할 수 있는 환경을 확보했습니다.

---

### 📑 메트릭 및 로그 수집 아키텍처
* **Prometheus & Pushgateway:** 크롤러 파이프라인의 메트릭(작업 성공률, 소요 시간 등)을 실시간 수집 및 저장
* **Grafana:** 수집된 메트릭 데이터를 시각화하여 대시보드로 시스템 상태 모니터링
* **Promtail & Loki:** 컨테이너 내부 및 시스템에서 발생하는 로그 데이터를 중앙집중형으로 수집하고 인덱싱하여 빠른 에러 디버깅 환경 확보

### 💡 주요 엔지니어링 의사결정 (Decision & Rationale)
* **시스템 가시성 확보:** 텍스트 로그를 일일이 확인하던 방식에서 벗어나, Grafana 대시보드를 통해 CPU/메모리 자원 및 파이프라인 상태를 시각적으로 한눈에 파악할 수 있도록 고도화했습니다.
* **장애 추적 시간 단축:** Loki와 Promtail의 도입을 통해 분산된 컨테이너의 로그를 한곳으로 모아, 시스템 예외 발생 시 원인 분석 및 예외 처리(Troubleshooting) 시간을 대폭 단축했습니다.

## 8. 환경 설정 가이드 (Environment Setup)

본 프로젝트는 원활한 개발 및 운영을 위해 두 가지 실행 환경을 제공합니다. 

* **Option 1 (가상환경):** 코드 수정 및 로컬 테스트 등 **개발 단계**에서 빠른 피드백을 위해 사용합니다.
* **Option 2 (Docker):** 실제 운영 환경과 동일한 조건에서 **엔진을 시연하거나 배포**할 때 사용하며, 환경 의존성 없이 즉시 실행 가능합니다. (권장)

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

4. **엔진 실행(가상환경에서 공공 자격증 추출)**
   ```bash
   python -m public_cert_api.run_public --root "../cert_data" --jmcd 1320 --mode http
   ```

5. **엔진 실행(가상환경에서 민간 자격증 추출)**
   ```bash
   python run_once.py --cert [자격증이름] --config private-cert-crawl/configs/cert_map.yaml
   # 예: linux_master
   ```

6. **도커 설치(Linux 기준)**
   ```bash
   # 1. Docker 및 Docker Compose 설치
   sudo dnf install -y docker docker-compose

   # 2. Docker 서비스 시작 및 부팅 시 자동 실행 설정
   sudo systemctl start docker
   sudo systemctl enable docker

   # 3. (선택) sudo 없이 도커 사용을 위한 사용자 그룹 추가
   sudo usermod -aG docker $USER
   # 이후 로그아웃 후 다시 로그인해야 적용됩니다.
   ```

7. **엔진 빌드 (최초 1회 또는 코드 수정 시)**
   ```bash
   docker compose build
   ```

8. **엔진 실행 (도커에서 공공 자격증 추출)**
   ```bash
   JMCD=1320 docker-compose up -d public-engine
   ```

9. **엔진 실행(도커에서 민간 자격증 추출)**
   ```bash
   CERT=linux_master docker-compose up -d private-engine
   ```

10. **전체 종목 일괄 수집**
    ```bash
    while read -r jmcd; do 
         echo "▶️ 현재 수집 중인 종목 코드: $jmcd"
         JMCD=$jmcd docker-compose up public-engine
    done < others.txt
    ```

12. **보안 및 권한 관리**
    ```bash
    # 1. 소유권 변경 (현재 사용자로 지정)
    sudo chown -R $USER:$USER ~/cert_data

    # 2. 디렉토리 권한 (755): 리스트 조회 및 진입 허용
    find ~/cert_data -type d -exec chmod 755 {} +

    # 3. 파일 권한 (644): 읽기/쓰기 허용 (실행 방지)
    find ~/cert_data -type f -exec chmod 644 {} +

    # 4. SELinux 보안 라벨 (Fedora 등 특정 환경 필요 시)  
    sudo chcon -Rt svirt_sandbox_file_t ~/cert_data
    ```     

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
   
4. **엔진 실행(가상환경에서 공공 자격증 추출)**
   ```bash
   python -m public_cert_api.run_public --root "../cert_data" --jmcd 1320 --mode http
   ```

5. **엔진 실행(가상환경에서 민간 자격증 추출)**
   ```bash
   python run_once.py --cert [자격증이름] --config private-cert-crawl/configs/cert_map.yaml
   # 예: linux_master
   ```

6. **Windows 환경**
   - **Docker Desktop 설치**: Docker 공식 홈페이지에서 설치 파일을 다운로드하여 설치합니다.
   - **가상화 설정**: BIOS에서 Virtualization(VT-x/AMD-V)이 활성화되어 있어야 하며, WSL2 기반 설정을 권장합니다.
   - **실행 확인**: 터미널에서 명령어를 입력하기 전, 반드시 Docker Desktop 앱을 실행하여 'Engine Running' 상태인지 확인해야 합니다.

7. **엔진 실행 (도커에서 공공 자격증 추출)**
   ```bash
   $env:JMCD="1320"; docker-compose up -d public-engine
   ```

8. **엔진 실행(도커에서 민간 자격증 추출)**
   ```bash
   $env:CERT="linux_master"; docker-compose up -d private-engine
   ```


9. **전체 종목 일괄 수집(Windows 환경은 Docker 파일 시스템 동기화로 인해 대량 수집 시 속도가 매우 느려질 수 있으므로, 가급적 Linux 환경 사용을 권장합니다)**
   ```bash
   foreach ($jmcd in Get-Content others.txt) {
      Write-Host "▶️ 현재 수집 중인 종목 코드: $jmcd"
      $env:JMCD = $jmcd.Trim()
      docker-compose up public-engine
   }
   ```
