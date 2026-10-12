# Mini Watch — Docker Compose (SKT ALEPH M5 Day1)

수업 제공 [mini-watch / day06-start](https://github.com/zeroskill2400/mini-watch/tree/day06-start)의 **일반 Flask + PostgreSQL**, **감시 Flask + PostgreSQL + Next.js** 앱을 유지하고, 각각 독립적인 Docker Compose 프로젝트로 실행하도록 구성한 과제입니다.

## 구현 내용과 변경 파일

- `compose-general.yaml`: `m5d1-general` 프로젝트에 general-db/general-api/general-gateway; DB healthcheck, 서비스별 내부 망, shared events 망, DB named volume 설정
- `compose-monitor.yaml`: `m5d1-monitor` 프로젝트에 monitor-db/monitor-api/monitor-web/monitor-gateway; 동일한 원칙 적용
- `general/app.py`, `monitor/backend/app.py`: 컨테이너 간 접속이 가능하도록 Flask 리스너 `0.0.0.0:5000`으로 변경
- `general/request_logging.py`: 고정된 127.0.0.1 대신 `MONITOR_URL` 환경변수 사용; `http://monitor-api:5000/api/events`로 전송
- `monitor/next-frontend/next.config.mjs`: 로컬 개발 환경의 잘못된 127.0.0.1:5200 rewrite를 제거하고 Nginx gateway의 `/api/` 라우팅 사용
- 제공된 `general/Dockerfile`, `monitor/backend/Dockerfile`, `monitor/next-frontend/Dockerfile`: Flask는 requirements 설치 → 소스 복사 → python 실행, Next.js는 `npm ci` → `npm run build` → `npm run start -- --hostname 0.0.0.0`로 production 실행
- 제공된 `.dockerignore`, `gateways/general.conf`, `gateways/monitor.conf`, 두 `docker-init.sql`을 프로젝트 경로에 배치
- 기존 로그인·세션·게시글·이벤트 수신/조회·메모 저장/조회 로직은 강사 코드 기반을 유지

수업 계정·DB 비밀번호는 **로컬 실습 전용 예시**이며 실제 운영에 사용하면 안 됩니다. 실제 서비스에서는 환경변수/secret 관리, TLS, 별도 비밀번호가 필요합니다.

## 처음 실행하기 (Docker Desktop 실행 후, Windows CMD)

아래 명령은 `compose-general.yaml`과 `compose-monitor.yaml`이 있는 저장소 루트에서 실행합니다. 이미 본인 GitHub 저장소를 clone했다면 해당 폴더로 이동해 시작합니다.

```cmd
cd /d C:\work
git clone https://github.com/youmjjang/mini-watch-docker-compose.git
cd mini-watch-docker-compose
docker network create m5d1-events
docker compose -f compose-monitor.yaml config --quiet
docker compose -f compose-general.yaml config --quiet
docker compose -f compose-monitor.yaml up -d --build
```

감시 API를 먼저 준비합니다. `http://localhost:8082/api/auth/me`를 열면 미로그인 상태이더라도 HTTP **200** 및 JSON이 반환되어야 합니다. `curl -i http://localhost:8082/api/auth/me`로 상태 코드를 확인합니다. 200을 확인한 후 일반 서비스를 시작합니다.

```cmd
docker compose -f compose-monitor.yaml ps
docker compose -f compose-monitor.yaml logs monitor-api
curl -i http://localhost:8082/api/auth/me
docker compose -f compose-general.yaml up -d --build
docker compose -f compose-general.yaml ps
docker compose -f compose-general.yaml logs general-api
```

DB 초기 SQL은 처음 비어 있는 DB 볼륨이 생성될 때 자동으로 실행됩니다. 실습 계정은 아래처럼 준비합니다 (이미 등록했다면 반복 생성하지 않습니다).

```cmd
docker compose -f compose-general.yaml exec general-api python create_user.py
docker compose -f compose-monitor.yaml exec monitor-api python create_user.py
```

- 일반: http://localhost:8081 — `student` / `Learn123!`
- 감시: http://localhost:8082 — `operator` / `Learn123!`
- 감시 API 상태 확인: http://localhost:8082/api/auth/me

## 연결 확인 및 테스트 순서

1. **감시 API 200 확인 → 일반 API 실행**. 다른 Compose 컨테이너를 `depends_on`으로 설정하지 않았으므로 시작 순서를 지킵니다. 아직 기록 재전송 큐가 없어서 감시가 꺼진 동안 전송 실패한 기록은 나중에 자동 복구되지 않습니다.
2. 일반 `8081` 로그인 화면에서 `student` 계정으로 잘못된 비밀번호를 먼저 입력해 401 로그인 실패를 발생시키고, 그다음 `Learn123!`로 성공(200) 후 게시글을 엽니다.
3. 감시 `8082`에서 `operator`로 로그인하고 **기록 불러오기**를 클릭합니다. `login_failure` / `401` 및 `login_success` / `200`이 표시되어야 합니다.
4. 감시 메모에서 제목 **Docker 점검**, 내용 **로그인 실패와 성공을 확인했다**를 저장하고 새로고침한 후 다시 불러와 같은 메모가 표시되는지 확인합니다.
5. 아래의 `down`으로 두 Compose를 따로 종료하고 감시 → 일반 순서로 `up -d` 후 이전 기록과 메모가 다시 보이는지 확인합니다.

다음 명령으로 네트워크와 컨테이너 상태를 검증합니다.

```cmd
docker compose -f compose-general.yaml config --quiet
docker compose -f compose-monitor.yaml config --quiet
docker compose -f compose-general.yaml ps
docker compose -f compose-monitor.yaml ps
docker compose -f compose-general.yaml logs general-api
docker compose -f compose-monitor.yaml logs monitor-api
docker network inspect m5d1-events
docker compose -f compose-general.yaml exec general-api getent hosts monitor-api
```

`config --quiet`는 YAML/Compose 설정 유효성, `ps`는 기동 상태, `logs`는 API 실행·요청 오류, `network inspect`는 양쪽 API의 공유 망 참여, `getent hosts monitor-api`는 **컨테이너 DNS 이름 조회**만 확인합니다. DNS가 성공하더라도 HTTP 요청 성공이나 DB 기록 저장을 증명하지는 않습니다. 실제 로그인 실패·성공 이벤트 및 메모의 저장·재조회를 별도로 확인합니다.

## 네트워크, 포트, DB 보존

| 서비스 | 네트워크 | PC 공개 포트 |
| --- | --- | --- |
| general-gateway | general-front-net | 127.0.0.1:8081 → 80 |
| general-api | general-front-net, general-data-net, m5d1-events | 없음 |
| general-db | general-data-net | 없음 |
| monitor-gateway | monitor-front-net | 127.0.0.1:8082 → 80 |
| monitor-web | monitor-front-net | 없음 |
| monitor-api | monitor-front-net, monitor-data-net, m5d1-events | 없음 |
| monitor-db | monitor-data-net | 없음 |

`general-front-net`, `general-data-net`, `monitor-front-net`, `monitor-data-net`는 각 Compose 프로젝트가 관리하는 **별도의 내부 통신망**입니다. 두 프로젝트에서 네트워크 키/별칭을 똑같이 써도 Compose 프로젝트마다 별개 네트워크로 생성됩니다. 기록 전송에는 반드시 외부에서 먼저 생성한 **같은 실제 네트워크 `m5d1-events`**를 `external: true` 및 `name: m5d1-events`로 참조하고 두 API를 가입시켜야 합니다. DB는 이 공유 망에 가입하지 않습니다.

각 API의 DB 주소는 `general-db:5432`, `monitor-db:5432`이며 각각 `general_db`, `monitor_db`를 사용합니다. 일반 API의 기록 수신 대상 주소는 `http://monitor-api:5000/api/events`입니다. **컨테이너 사이에서 localhost:8081/8082를 사용하지 않습니다.** 두 gateway만 호스트 포트를 노출합니다.

PostgreSQL 데이터 디렉터리 `/var/lib/postgresql/data`는 별도의 named volume `m5d1-general_general-data`, `m5d1-monitor_monitor-data`에 저장됩니다. `docker-init.sql`은 새 볼륨 최초 생성 시 실행되며, 기존 볼륨에 다시 적용되지 않습니다.

```cmd
docker compose -f compose-general.yaml down
docker compose -f compose-monitor.yaml down
docker compose -f compose-monitor.yaml up -d
docker compose -f compose-general.yaml up -d
```

`down`에는 **`-v`를 사용하지 않습니다**. `down -v` 또는 named volume 직접 삭제는 실습 데이터 유실을 일으킬 수 있습니다. 공유 망도 기본 `down`으로 삭제하지 않습니다.

## 선택 심화: 공유 망 분리와 복구

최종 제출 설정은 양쪽 API가 공유 망에 연결된 상태입니다. 테스트 목적으로 아래 명령을 실행하면 general-api에서 `monitor-api` 이름 조회 및 이벤트 전송이 실패할 수 있습니다.

```cmd
docker network disconnect m5d1-events m5d1-general-general-api-1
docker compose -f compose-general.yaml exec general-api getent hosts monitor-api
docker network connect m5d1-events m5d1-general-general-api-1
docker compose -f compose-general.yaml exec general-api getent hosts monitor-api
```

컨테이너 이름은 Compose 환경마다 다를 수 있으므로 먼저 `docker compose -f compose-general.yaml ps`로 실제 이름을 확인합니다. 네트워크 복구 뒤 **새 로그인 실패/성공**을 다시 만들어야 이전에 못 보낸 이벤트를 대신 검증할 수 있습니다.

## 선택 심화: restart / rebuild

두 Flask Dockerfile은 `COPY requirements.txt` 후 pip 설치, `COPY . .`로 소스를 이미지에 복사합니다. 일반·감시 API 소스 수정은 컨테이너의 마운트 볼륨으로 자동 반영되지 않습니다. 따라서 `restart`는 **같은 이미지로 다시 시작**할 뿐 수정 코드를 넣지 못하고, `up -d --build`는 수정된 소스를 포함하는 이미지를 **재빌드하고 재생성**합니다.

```cmd
docker compose -f compose-general.yaml restart general-api
docker compose -f compose-general.yaml up -d --build general-api
docker compose -f compose-monitor.yaml up -d --build monitor-api
```

## 선택 심화: DB 격리 검증

```cmd
docker compose -f compose-general.yaml exec general-api getent hosts general-db
docker compose -f compose-general.yaml exec general-api getent hosts monitor-db
```

일반 API에서 자기 DB 이름은 조회되지만 감시 DB 이름은 기본적으로 조회되지 않아야 합니다. **DNS 조회 성공 ≠ DB 계정 인증 성공 ≠ SQL 실행 성공**입니다. DB 망 분리는 DNS/접근 경계를 형성하고, 실제 권한 보장은 DB 인증 및 SQL 권한 설정에서 확인해야 합니다.

## Git 이력

Docker 작업은 본인 GitHub 저장소의 실제 커밋에서 확인할 수 있습니다.

- `216c4726fb3241f3cf9676c25dd4532567cbd54e` — 두 Compose의 API·Next.js·Nginx 구성, 독립 네트워크/공유 망, Flask 0.0.0.0:5000 리스너, MONITOR_URL 이벤트 전송, Next.js 라우팅 수정
- 앱 기반: 강사 공개 `zeroskill2400/mini-watch` 저장소의 `day06-start`; 강사 제공 `day1-materials/project-starter` 자산 사용

> 검증 상태: GitHub 파일과 소스 연결은 확인했지만, 작성 환경에서는 Docker Engine을 실행할 수 없어 실제 `docker compose config`, 이미지 빌드, 로그인, 기록/메모 영속성의 현장 테스트는 **실행하지 않았습니다**. Windows Docker Desktop에서 위 순서대로 확인해야 합니다.
