# E1-1 최종 평가 보고서

## 1. 과제 목표와 완성 결과

이 과제의 목표는 “내 컴퓨터에서만 되는 실행”이 아니라, 터미널 명령·Dockerfile·포트·스토리지·Git 기록으로 누구나 같은 절차를 재현할 수 있는 개발 작업실을 만드는 것이다.

최종 결과물은 `nginx:1.27-alpine`을 기반으로 만든 `e1-1-workstation-web:1.0` 커스텀 이미지와 그 검증 문서다. Windows PowerShell에서 Docker Desktop Linux 엔진을 실제로 사용했고, `hello-world`, Ubuntu 명령, 권한, Docker 운영, 포트 매핑, 바인드 마운트, 볼륨 영속성, GitHub 원격 연결을 확인했다.

| 평가 대상 | 최종 상태 | 증거 |
| --- | --- | --- |
| Docker 엔진 | Docker Desktop 29.9.2 동작 | [실행 로그 3절](verification-log.md#3-docker-설치기본-운영) |
| 커스텀 이미지 | NGINX 설정·정적 페이지·환경 변수·헬스체크 포함 | [실행 로그 4절](verification-log.md#4-dockerfile-커스텀-이미지) |
| 웹 접속 | `http://localhost:18080`에서 HTTP 200 | [실행 로그 5절](verification-log.md#5-포트-매핑접속운영-로그) |
| 바인드 마운트 | v1 → v2 변경이 재시작 없이 반영 | [실행 로그 6절](verification-log.md#6-바인드-마운트-반영) |
| Docker 볼륨 | 컨테이너 삭제 후에도 `persistent-data-ok` 유지 | [실행 로그 7절](verification-log.md#7-docker-볼륨-영속성) |
| GitHub | `origin`이 `manbok2028/E1-1`로 연결되고 최종 푸시 | [실행 로그 9절](verification-log.md#9-gitgithub-연동) |
| Compose 보너스 | 웹 서버+상태 서비스 멀티 컨테이너, 서비스 이름 통신, 환경 변수 주입 | [실행 로그 8절](verification-log.md#8-compose-보너스-운영-명령환경-변수멀티-컨테이너) |

## 2. 설계 판단

정적 NGINX 서버를 선택한 이유는 웹 서버의 핵심 구조(이미지 빌드, 컨테이너 실행, 포트 매핑, 바인드 마운트)를 작은 구성으로 분명하게 보여 주기 위해서다. `nginx:alpine`은 검증된 기존 베이스 이미지이고, 내 Dockerfile은 포트 설정·콘텐츠·헬스체크를 추가해 과제 목적에 맞는 커스텀 이미지를 만든다.

- **개발 중 변경 확인**에는 호스트 폴더를 연결하는 바인드 마운트를 사용했다.
- **컨테이너 삭제 뒤에도 남아야 할 데이터**에는 Docker 관리 볼륨을 사용했다.
- **반복 실행**에는 Dockerfile과 Compose 파일을 저장소에 넣어 명령을 문서화했다.
- **보너스 멀티 컨테이너**에는 Compose 네트워크에서 웹 서버가 `status-api`를 서비스 이름으로 호출하도록 구성했다.
- **운영 확인**에는 `docker ps -a`, `docker logs`, `docker stats`, `/health`, `curl`을 사용했다.

## 3. 학습 목표 설명

| 목표 | 이 결과물에서의 설명 |
| --- | --- |
| 절대/상대 경로 | `C:\...\E1-1`은 절대 경로, `./app`·`../README.md`는 현재 위치 기준 상대 경로다. 이식성을 위해 Dockerfile과 문서는 상대 경로를 사용한다. |
| r/w/x 및 755·644 | Linux 컨테이너에서 700/600을 755/644로 변경했다. 숫자는 r=4, w=2, x=1의 합으로 읽는다. |
| 커스텀 이미지 | `FROM nginx:1.27-alpine` 위에 설정·콘텐츠·환경 변수·헬스체크를 추가하고 `docker build`로 새 태그를 만들었다. |
| 포트 매핑 | 호스트 18080에서 격리된 컨테이너 8080으로 요청을 전달해 브라우저/`curl`에서 접근할 수 있다. |
| Docker 볼륨 | 컨테이너의 삭제 대상 파일 시스템과 별도로 Docker가 관리하는 저장소다. 새 컨테이너에서도 파일을 읽어 영속성을 확인했다. |
| Git과 GitHub | Git은 로컬 이력 관리, GitHub는 원격 협업·공유 공간이다. remote와 push로 연결을 검증한다. |

## 4. 평가자가 확인할 순서

1. 저장소의 `Dockerfile`, `nginx/default.conf`, `app/index.html`을 확인한다.
2. README의 재현 명령으로 이미지 빌드와 `18080:8080` 실행을 재현한다.
3. `curl.exe -i http://localhost:18080/`과 `curl.exe -i http://localhost:18080/health`에서 HTTP 200을 확인한다.
4. `docs/verification-log.md`에서 실제 명령과 결과를 대조한다.
5. `docker run` 바인드 마운트 명령을 실행한 뒤 `app/index.html`의 v2 문구를 바꿔 변경이 즉시 반영되는지 확인한다.
6. 볼륨 명령으로 컨테이너 삭제 후 데이터가 유지되는지 확인한다.
7. `git remote -v`, `git log --oneline -1`, GitHub 저장소의 최신 커밋을 대조한다.

## 5. 보안·개인정보 보호

Docker/GitHub 인증 정보는 환경 또는 자격 증명 관리자에 두며 저장소에 넣지 않는다. `.gitignore`는 `.env`, 키 파일을 제외한다. 실행 로그에는 Git 이메일을 마스킹하고, 토큰·비밀번호·인증 코드·개인키를 기록하지 않았다.

## 6. 보너스 과제 실행 결과

선택 과제 중 Docker Compose 기본·운영, 멀티 컨테이너 네트워크 통신, 환경 변수 활용을 실제로 실행했다. 구성 파일은 [docker-compose.yml](../docker-compose.yml)에 있으며, 모든 명령과 출력은 [실행 로그 8절](verification-log.md#8-compose-보너스-운영-명령환경-변수멀티-컨테이너)에 남겼다.

### 6-1. Compose 기본 실행과 운영 명령

```powershell
docker compose up -d --build
docker compose ps
docker compose logs --tail 20
docker compose down
```

실행 결과, `e1-1-compose-web` 컨테이너는 호스트 `18082` 포트와 컨테이너 `8080` 포트를 연결해 실행됐고, 종료 명령 뒤에는 Compose 컨테이너와 네트워크가 정리됐다. 이는 긴 `docker run` 명령을 저장소 안의 선언형 실행 설정으로 관리하는 Compose의 목적을 확인한 것이다.

### 6-2. 멀티 컨테이너와 서비스 디스커버리

Compose에 다음 두 서비스를 정의했다.

| 서비스 | 역할 | 네트워크 확인 |
| --- | --- | --- |
| `workstation-web` | NGINX 기반 정적 웹 서버 | `18082:8080`으로 외부 공개 |
| `status-api` | `hashicorp/http-echo` 기반 상태 응답 서비스 | Compose 내부 DNS 이름 `status-api:5678` |

웹 컨테이너에서 서비스 이름을 도메인처럼 사용해 실제 통신을 검증했다.

```powershell
docker compose exec -T workstation-web wget -qO- http://status-api:5678
```

```text
compose-network-ok
```

이는 컨테이너 IP 주소를 하드코딩하지 않고도 Compose 네트워크가 서비스 이름을 찾아 연결한다는 증거다. 실제 Compose 로그에도 `status-api:5678 ... "GET / HTTP/1.1" 200`이 기록됐다.

### 6-3. 환경 변수 활용

`docker-compose.yml`의 `workstation-web` 서비스에 다음 환경 변수를 주입했다.

```yaml
environment:
  APP_MODE: compose-lab
```

실제 컨테이너 내부에서 확인한 명령과 결과는 다음과 같다.

```powershell
docker compose exec -T workstation-web sh -c 'echo $APP_MODE'
```

```text
compose-lab
```

환경 변수를 코드나 이미지 자체에 고정하지 않고 실행 설정에서 주입하면, 같은 이미지를 개발·검증·운영 환경에서 서로 다른 설정으로 재사용할 수 있다.

### 6-4. 선택하지 않은 보너스 범위

GitHub SSH 키 등록은 개인 계정에 장기 인증 수단을 추가하는 보안 작업이므로, 저장소 코드나 문서에 키를 만들거나 비공개 키를 기록하지 않았다. 현재 저장소는 HTTPS 원격과 실제 `git push`로 GitHub 연동을 검증했다. SSH 방식이 필요한 경우에는 사용자가 자신의 VS Code/GitHub 인증을 마친 뒤 공개키만 GitHub 계정에 등록하고, 비공개 키는 로컬 보안 저장소에만 보관해야 한다.

## 7. 결론

이 결과물은 명령 한 줄의 성공을 보여 주는 데 그치지 않고, 이미지와 컨테이너의 구분, 네트워크 포트 연결, 바인드 마운트의 실시간 반영, 볼륨의 영속성, 원격 Git 협업을 실제 결과로 연결했다. 따라서 평가자는 README와 연결 문서만으로 동일한 개발 작업실을 재현하고 각 요구사항을 검증할 수 있다.
