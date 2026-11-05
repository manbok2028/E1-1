# E1-1 · 내 컴퓨터에 개발자용 작업실 꾸미기

> Linux CLI, Docker, Git/GitHub를 실제 명령으로 점검하고, NGINX 기반 커스텀 웹 서버를 컨테이너화한 개발 워크스테이션 실습 결과물입니다.

## 빠른 안내

- 최종 평가 보고서: [docs/evaluation-report.md](docs/evaluation-report.md)
- 실제 실행 명령과 출력: [docs/verification-log.md](docs/verification-log.md)
- Docker 볼륨 영속성 실습: [docs/volume-lab.md](docs/volume-lab.md)
- 요구사항별 근거: [docs/requirement-mapping.md](docs/requirement-mapping.md)
- 문제 해결 기록: [docs/troubleshooting.md](docs/troubleshooting.md)
- 실제 Docker 명령·웹 응답 PNG: [evidence/screenshots](evidence/screenshots)

PNG는 [`scripts/generate_evidence_png.py`](scripts/generate_evidence_png.py)가 실제 Docker 명령을 다시 실행해 생성한다. 필요한 렌더링 의존성은 [`requirements-evidence.txt`](requirements-evidence.txt)에 분리했다.

## 재현 실행

```powershell
# 1) 이미지 빌드
docker build -t e1-1-workstation-web:1.0 .

# 2) 포트 매핑 실행
docker run -d --name e1-1-web -p 18080:8080 e1-1-workstation-web:1.0
curl.exe http://localhost:18080

# 3) 상태와 로그 확인
docker ps -a
docker logs e1-1-web
docker stats --no-stream e1-1-web
```

### 보너스: Compose 멀티 컨테이너

`docker-compose.yml`은 웹 서버와 `status-api`를 같은 Compose 네트워크에서 실행한다. 웹 컨테이너 내부에서 서비스 이름으로 상태 API를 호출하고, Compose 환경 변수도 확인할 수 있다.

```powershell
docker compose up -d --build
docker compose exec workstation-web sh -c 'echo $APP_MODE'
docker compose exec workstation-web wget -qO- http://status-api:5678
docker compose logs --tail 20
docker compose down
```

### 필수 확인: Docker 볼륨 영속성

컨테이너를 삭제해도 데이터가 유지되는지를 실제로 확인했다. `e1-1-data`에 파일을 기록하고 컨테이너 `e1-1-vol`을 삭제한 뒤, 새 컨테이너에서 같은 파일을 다시 읽었다.

```powershell
docker volume create e1-1-data
docker run -d --name e1-1-vol -v e1-1-data:/data ubuntu:latest sleep infinity
docker exec e1-1-vol bash -lc "printf 'volume-persistence-confirmed-2026-11-05\n' > /data/evaluator-proof.txt"
docker rm -f e1-1-vol
docker run --rm -v e1-1-data:/data ubuntu:latest bash -lc "cat /data/evaluator-proof.txt"
```

실제 출력은 `volume-persistence-confirmed-2026-11-05`였다. 전체 기록은 [볼륨 실습 문서](docs/volume-lab.md)에, 기존 시각 증빙은 [05-volume-persistence.png](evidence/screenshots/05-volume-persistence.png)에 있다.

Windows PowerShell에서는 다음 스크립트로 공개 포트·컨테이너 상태를 다시 확인할 수 있습니다.

```powershell
.\scripts\verify-workstation.ps1
```

> 포트 `18080`이 이미 사용 중이면 `-p 18081:8080`처럼 호스트 포트만 바꾸면 됩니다. 컨테이너 내부 포트는 NGINX 설정의 `8080`을 그대로 둡니다.

## 결과물 구성

```text
E1-1/
├── app/                  # NGINX가 제공하는 정적 웹 페이지
├── nginx/                # 컨테이너 내부 8080 포트 설정
├── scripts/              # 재현 확인 PowerShell 스크립트
├── docs/                 # 로그·보고서·요구사항 대응표·트러블슈팅
├── Dockerfile            # nginx:alpine 기반 커스텀 이미지
└── docker-compose.yml    # 선택(보너스): Compose 실행 정의
```

## 보안 원칙

이 저장소에는 토큰, 비밀번호, 개인키, 인증 코드, Docker Hub/GitHub 자격 증명을 저장하지 않습니다. 명령 로그의 Git 설정은 이름·이메일처럼 필요한 범위만 기록하며, 민감한 값은 출력하지 않습니다.
