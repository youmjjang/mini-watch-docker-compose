# Mini-watch — 5과목 Day3 실제 요청 분석

기존 Day1/Day2 게시판·감시 서비스에 Day3 분석을 이어서 적용했다. 기존 DB, 사용자, 메모, Compose 볼륨을 초기화하지 않는다. 기존 클라우드 설명은 [README-day2.md](README-day2.md), [deployment-plan.md](deployment-plan.md)에 있다.

## 1. 구성과 개념

- `general/app.py`의 `app.after_request(record_request)`가 HTTP 응답 후 `general/request_logging.py::record_request`를 호출한다.
- `record_request`는 `method`, `path`, `status_code`를 기록하며, `print`는 일반 컨테이너 표준 출력이고, `requests.post(MONITOR_URL, X-Event-Token: EVENT_TOKEN)`는 별개의 감시 API 전송이다. 표준 출력만으로 DB 저장 성공을 보장하지 않는다.
- `monitor/backend/routes/events.py`가 `EVENT_TOKEN`을 검증하고 `event_rules.py::make_event`가 GET / 200을 `post_list`, 404를 `request_error`로 분류한다.
- `repositories/events.py::create_event`가 `http_events`에 저장한다. 숫자 `id`와 `occurred_at`은 감시 DB에서 생성되며, 시각은 실제 요청 발생 시각이 아닌 DB 수신·저장 시각이다.
- 일반 Compose의 `MONITOR_URL`은 감시 컨테이너 주소이며, 두 Compose의 `EVENT_TOKEN`은 일치해야 한다. 동일한 로컬 Docker 외부 네트워크 `m5d1-events`를 공유한다. 실제 운영 비밀값을 브라우저 또는 Git에 넣지 않는다.
- `learning/capture_case.py`는 일반 앱에 실제 GET / 와 GET /training-missing을 요청한 뒤 시작 시점의 마지막 ID 이후 DB 행을 읽는다. SQL INSERT, 고정 JSON과 고정 숫자 화면으로 대체하지 않는다.
- `learning/normalize.py::normalize_event`는 원본을 복사해 `http-<DB ID>`, `source=http_live`, `kind=event_type`을 만든다. 원본 필드와 시각을 보존하고 IP나 사용자 정보를 지어내지 않는다.
- `learning/http_rules.py::select_views`는 GET, /, 200, post_list 네 조건을 모두 만족한 행을 반환한다. 같은 선택 목록으로 조회 횟수와 근거 ID를 계산한다.
- `find_following_errors`는 마지막 조회 수신시각 뒤 **0초 초과 30초 이하**의 404만 전체 정규화 행에서 고른다. 조회가 없으면 오류도 비운다.
- `learning/report.py::build_report`는 `count >= threshold`로 HTTP 카드 하나를 만들고, 조회 행과 뒤따른 404를 `records`, `evidence`에 연결한다. **12회 조회와 404 1건이면 관찰값 12, 근거 13행**이다.
- `routes/analysis.py`, `learning/support.py`는 관찰 시작 시 마지막 ID를 경계로 기록한다. 첫 결과를 호출한 시점의 최근 60초 DB 수신 기록 중 ID 경계 이후 행을 조회한다. 타이머로 60초간 수집하는 방식이 아니다. 첫 결과의 `reference_time`과 `after_id`는 기준 10↔20 변경 때 그대로 재사용한다. 새 관찰은 화면 상태와 경계만 초기화하며 DB 기록을 삭제하지 않는다.
- `AnalysisClient.js`는 기존 로그인 후 새 관찰, 기준 입력, 결과 조회, 6열 근거 표를 표시한다. `http-숫자`는 원본 DB ID를 가리킨다. 로그인과 입력 검증을 유지한다.
- 이 자료는 동일 서비스 내 시간상 인접성만 보여 준다. 동일 IP·사용자·인과관계·침해를 입증하지 않으며, 기준 미해당도 정상이라는 증거가 아니다. 교육용 PCAP·IOC를 실제 HTTP 카드에 섞지 않는다.

## 2. 로컬 실행 (Windows CMD)

기존 프로젝트 루트에서 실행한다. 기존 DB/계정과 두 Compose 프로젝트를 유지한다. 새 DB나 볼륨을 생성하거나 지우지 않는다.

실행 전, 개인 로컬 셸에 **동일한** 전송 토큰을 설정한다. 아래 변수는 예시 이름이며 실제 값은 Git에 올리지 않는다.

```cmd
set EVENT_TOKEN=<로컬에서 직접 정한 비밀 토큰>
docker network inspect m5d1-events >nul 2>&1 || docker network create m5d1-events
docker compose -f compose-monitor.yaml up -d --build
docker compose -f compose-general.yaml up -d --build
```

기존 로그인 계정은 Day1 준비 상태를 사용한다. 변경 후 API를 재시작하고 Next.js는 반드시 재빌드한다.

```cmd
docker compose -f compose-monitor.yaml restart monitor-api
docker compose -f compose-monitor.yaml up -d --build monitor-web
docker compose -f compose-monitor.yaml restart monitor-gateway
```

실제 요청으로 **4회 + 404 1회** 만들기 (호스트 임시 파일에만 기록하고 성공 시 교체).

```cmd
if not exist monitor\backend\learning\data mkdir monitor\backend\learning\data
docker compose -f compose-monitor.yaml exec -T monitor-api python -m learning.capture_case 4 > monitor\backend\learning\data\observation-next.json && move /Y monitor\backend\learning\data\observation-next.json monitor\backend\learning\data\observation.json
docker compose -f compose-monitor.yaml exec -T monitor-api python -m learning.lesson2
docker compose -f compose-monitor.yaml exec -T monitor-api python -m learning.lesson3
```

감시 화면 http://localhost:8082 에 기존 계정으로 로그인하고 기준 10에서 **새 관찰 시작**을 누른다. 그다음 별도 Windows CMD에서 아래를 실행한다. 다른 탭에서 일반 게시판을 새로고침하지 않는다.

```cmd
docker compose -f compose-monitor.yaml exec -T monitor-api python -m learning.capture_case 12 > monitor\backend\learning\data\observation-next.json && move /Y monitor\backend\learning\data\observation-next.json monitor\backend\learning\data\observation.json
docker compose -f compose-monitor.yaml exec -T monitor-api python -m learning.lesson4
docker compose -f compose-monitor.yaml exec -T monitor-api python -m learning.lesson5
```

요청을 만든 후 **1분 안에 첫 결과 불러오기**를 누른다. 근거 표를 펼쳐 원본 ID와 404를 확인한다. 새 관찰을 다시 시작하지 않은 채 기준을 20으로 바꾸어 다시 조회하고 10으로 복구한다. 이때 기준시각과 근거 ID는 유지되고 판정만 바뀐다. 이후 새 관찰 시작을 눌러 추가 일반 요청 없이 조회하면 관찰값은 0이어야 한다.

수집 실패나 60초 경과 시 이전 파일을 결과로 오인하지 않는다. 원인 확인 후 새 관찰 → 재캡처 → 1분 내 첫 분석을 다시 진행한다.

```cmd
docker compose -f compose-general.yaml logs --tail 20 general-api
docker compose -f compose-monitor.yaml logs --tail 20 monitor-api
docker compose -f compose-monitor.yaml exec monitor-db psql -U sample -d monitor_db -c "SELECT id, occurred_at, method, path, status_code, event_type FROM http_events ORDER BY id DESC LIMIT 15;"
```

## 3. 예상 결과와 확인 상태

| 실습 | 예상 관찰값 | 예상 판정 | 근거 |
| --- | ---: | --- | --- |
| 4회 + 404, 기준 10 | 4 | 기준 미해당 | 원본 5행, 조회 선택 4행 |
| 12회 + 404, 기준 10 | 12 | 검토 후보 | 13행 |
| 동일 구간, 기준 20 | 12 | 기준 미해당 | 같은 13행 |
| 동일 구간, 기준 10 복구 | 12 | 검토 후보 | 같은 13행 |
| 새 관찰 후 추가 요청 없음 | 0 | 기준 미해당 | 없음 |

**확인 상태:** GitHub 코드 적용은 완료. 이 작업 환경에서는 사용자의 로컬 Docker·DB·계정에 접근할 수 없어 위 실제 요청과 화면 결과는 **미실행** 상태다. 표는 기대값이지 실행 증빙이 아니다.

제출 시 이 프로젝트의 전체 소스, Compose, Dockerfile, nginx gateway, SQL, 의존성·잠금 파일을 유지한다. 개인 `.env`, 비밀번호·토큰, DB 덤프, 실행 로그, `observation.json`, 임시 JSON, node_modules, .next, 가상환경, 캐시는 제외한다. 과제는 Git 커밋 SHA나 배포 주소·스크린샷을 요구하지 않는다.
