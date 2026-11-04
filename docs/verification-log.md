# 실제 실행·검증 로그

> 실행일: 2026-11-04 · 실행 환경: Windows PowerShell + Docker Desktop Linux engine  
> 보안 원칙: 토큰·비밀번호·개인키는 기록하지 않았고, Git 이메일은 마스킹했다.

## 1. 터미널 기본 조작

PowerShell에서 현재 위치 확인, 숨김 파일 포함 목록, 하위 폴더 이동, 디렉터리/빈 파일 생성, README 복사, 이름 변경, 내용 확인, 삭제를 실행했다. 실습용 `evidence/terminal-lab`은 확인 후 삭제했다.

```powershell
PWD=C:\Users\kim man bok\OneDrive\문서\코디세이 2\E1-1
Get-ChildItem -Force
New-Item -ItemType Directory evidence\terminal-lab
Set-Location evidence\terminal-lab
New-Item -ItemType Directory relative-work
New-Item -ItemType File empty-note.txt
Copy-Item ..\..\README.md .\readme-copy.md
Move-Item .\readme-copy.md .\renamed-readme.md
Get-Content .\renamed-readme.md -TotalCount 2
Remove-Item .\renamed-readme.md
Remove-Item ..\terminal-lab -Recurse -Force
```

실제 핵심 출력:

```text
MOVED_TO=C:\Users\kim man bok\OneDrive\문서\코디세이 2\E1-1\evidence\terminal-lab
# E1-1 · 내 컴퓨터에 개발자용 작업실 꾸미기
DELETED_README_COPY=True
DELETED_LAB=True
```

`C:\...\E1-1\README.md`처럼 드라이브부터 쓰는 것은 **절대 경로**이고, 현재 폴더 기준으로 `./relative-work`, `../README.md`처럼 쓰는 것은 **상대 경로**다. 재현 문서에서는 다른 컴퓨터에서도 실행할 수 있도록 가능한 한 상대 경로를 사용했다.

## 2. Linux 권한 실습

Windows 호스트 권한과 Linux 권한 표기는 다르므로 Ubuntu 컨테이너 안에서 확인했다. 디렉터리·파일 각각을 더 제한적인 권한으로 만든 뒤 요구 권한으로 변경해 전후 차이를 확인했다.

```powershell
docker run --rm ubuntu:latest bash -lc "mkdir -p /tmp/permission-lab; touch /tmp/permission-lab/example.txt; chmod 700 /tmp/permission-lab; chmod 600 /tmp/permission-lab/example.txt; echo before; stat -c '%a %n' /tmp/permission-lab /tmp/permission-lab/example.txt; chmod 755 /tmp/permission-lab; chmod 644 /tmp/permission-lab/example.txt; echo after; stat -c '%a %n' /tmp/permission-lab /tmp/permission-lab/example.txt"
```

```text
before
700 /tmp/permission-lab
600 /tmp/permission-lab/example.txt
after
755 /tmp/permission-lab
644 /tmp/permission-lab/example.txt
```

- `r`(read), `w`(write), `x`(execute)를 소유자·그룹·기타 사용자 순서로 세 자리 숫자로 표현한다.
- `7 = 4+2+1(rwx)`, `6 = 4+2(rw-)`, `5 = 4+1(r-x)`, `4 = 4(r--)`이다.
- 따라서 디렉터리 `755`는 소유자는 읽기/쓰기/진입, 나머지는 읽기/진입만 가능하고, 파일 `644`는 소유자만 쓰고 나머지는 읽기만 가능하다.

## 3. Docker 설치·기본 운영

```powershell
docker --version
docker info --format 'Server={{.ServerVersion}} OS={{.OperatingSystem}} Driver={{.Driver}}'
docker run --rm hello-world
docker run --rm ubuntu:latest bash -lc "echo container-shell-ok; pwd; ls -1 / | head -n 5"
docker images
```

실제 핵심 출력:

```text
Docker version 29.9.2, build a82e528
Server=29.9.2 OS=Docker Desktop Driver=overlayfs
Hello from Docker!
container-shell-ok
/
bin
boot
dev
etc
home
```

`docker run --rm hello-world`는 실행 후 자동 삭제되는 일회성 컨테이너를 보여 준다. Ubuntu는 `bash -lc`로 내부 명령을 실행했다. `attach`는 컨테이너의 주 프로세스 표준 입출력에 붙으므로 해당 프로세스 종료가 컨테이너 종료로 이어질 수 있고, `docker exec`는 이미 실행 중인 컨테이너에 별도 프로세스를 추가 실행하므로 주 프로세스를 유지한 채 점검할 때 사용한다.

## 4. Dockerfile 커스텀 이미지

기존 베이스 이미지는 `nginx:1.27-alpine`이다. 이 이미지에 다음을 직접 추가했다.

| 커스텀 포인트 | 목적 |
| --- | --- |
| `nginx/default.conf` | 컨테이너 내부 서비스 포트를 `8080`으로 명시하고 `/health` 제공 |
| `app/` 정적 콘텐츠 | 이 과제만의 웹 응답 제공 |
| `LABEL` | 이미지의 제목·설명·소스 추적 |
| `ENV APP_MODE` | 설정과 코드의 분리 예시 |
| `HEALTHCHECK` | 컨테이너 내부 HTTP 응답을 주기적으로 확인 |

```powershell
docker build -t e1-1-workstation-web:1.0 .
docker run --rm e1-1-workstation-web:1.0 nginx -t
docker image inspect e1-1-workstation-web:1.0 --format 'IMAGE={{.RepoTags}} EXPOSED={{json .Config.ExposedPorts}} HEALTHCHECK={{.Config.Healthcheck.Test}}'
```

```text
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
IMAGE=[e1-1-workstation-web:1.0] EXPOSED={"80/tcp":{},"8080/tcp":{}} HEALTHCHECK=[CMD-SHELL wget -q -O /dev/null http://127.0.0.1:8080/ || exit 1]
```

이미지는 실행 가능한 설계도(레이어 묶음)이고, 컨테이너는 그 이미지로부터 만들어진 실행 중인 인스턴스다. 따라서 같은 이미지를 여러 컨테이너로 실행할 수 있으며, 컨테이너를 삭제해도 이미지는 남는다.

## 5. 포트 매핑·접속·운영 로그

```powershell
docker run -d --name e1-1-web -p 18080:8080 e1-1-workstation-web:1.0
curl.exe -i http://localhost:18080/
curl.exe -i http://localhost:18080/health
docker ps -a --filter 'name=e1-1-web'
docker logs e1-1-web
docker stats --no-stream e1-1-web
```

실제 핵심 출력:

```text
HTTP/1.1 200 OK
Server: nginx/1.27.5
<title>E1-1 개발 워크스테이션</title>

HTTP/1.1 200 OK
ok

0.0.0.0:18080->8080/tcp   e1-1-web
CPU 0.00%   MEM 14.35MiB / 7.609GiB
```

호스트의 `18080`은 내 PC에서 접속하는 문이고, 컨테이너의 `8080`은 격리된 NGINX가 듣는 문이다. 둘은 네트워크 공간이 다르므로 `-p 호스트포트:컨테이너포트` 매핑이 필요하다. 브라우저 대신 `curl.exe -i http://localhost:18080/`로 주소·포트·HTTP 응답을 한 번에 기록했다.

## 6. 바인드 마운트 반영

```powershell
docker run -d --name e1-1-bind -p 18081:8080 -v "${PWD}\app:/usr/share/nginx/html:ro" e1-1-workstation-web:1.0
curl.exe -sS http://localhost:18081/ | Select-String 'mount-state'
docker inspect e1-1-bind --format 'Mount={{range .Mounts}}{{.Type}} {{.Source}} -> {{.Destination}} RW={{.RW}}{{end}}'
```

변경 전 실제 응답:

```text
바인드 마운트 초기 콘텐츠 (v1)
Mount=bind C:\Users\kim man bok\OneDrive\문서\코디세이 2\E1-1\app -> /usr/share/nginx/html RW=false
```

호스트의 `app/index.html`을 v2 문구로 변경한 뒤 **컨테이너 재시작·이미지 재빌드 없이** 다시 요청했다.

```text
호스트 변경이 재빌드 없이 반영된 콘텐츠 (v2)
```

즉 바인드 마운트는 호스트의 개발 파일을 컨테이너에 직접 연결하므로, 개발 중 변경 반영을 빠르게 확인하는 데 적합하다.

## 7. Docker 볼륨 영속성

```powershell
docker volume create e1-1-workstation-data
docker run -d --name e1-1-volume-a -v e1-1-workstation-data:/data ubuntu:latest sleep infinity
docker exec e1-1-volume-a bash -lc "printf 'persistent-data-ok\n' > /data/proof.txt; cat /data/proof.txt"
docker rm -f e1-1-volume-a
docker run -d --name e1-1-volume-b -v e1-1-workstation-data:/data ubuntu:latest sleep infinity
docker exec e1-1-volume-b bash -lc "cat /data/proof.txt"
docker rm -f e1-1-volume-b
docker run --rm -v e1-1-workstation-data:/data ubuntu:latest bash -lc "cat /data/proof.txt"
```

실제 핵심 출력:

```text
Name=e1-1-workstation-data Mountpoint=/var/lib/docker/volumes/e1-1-workstation-data/_data
persistent-data-ok
e1-1-volume-a  # 첫 컨테이너 삭제
persistent-data-ok  # 새 컨테이너에서 읽기 성공
Mount=volume e1-1-workstation-data -> /data
persistent-data-ok  # 두 번째 컨테이너 삭제 뒤에도 읽기 성공
```

볼륨은 특정 컨테이너의 쓰기 레이어와 분리되어 Docker가 관리하는 저장 공간이다. 그래서 컨테이너를 삭제해도 볼륨 자체를 삭제하지 않는 한 데이터가 유지된다.

## 8. Compose 보너스

```powershell
docker compose up -d --build
docker compose ps
curl.exe -sS http://localhost:18082/ | Select-String 'mount-state'
docker compose logs --tail 12
docker compose down
```

실제 결과는 `e1-1-compose-web`이 `0.0.0.0:18082->8080/tcp`으로 실행되고, HTTP `200` 로그와 v2 문구가 반환된 뒤 `docker compose down`으로 네트워크·컨테이너가 정리된 것이다. Compose는 긴 `docker run` 명령을 `docker-compose.yml`이라는 버전 관리 가능한 실행 설정으로 바꿔 준다.

## 9. Git·GitHub 연동

```powershell
git config --global --list
git remote -v
git ls-remote origin refs/heads/main
```

민감정보를 마스킹한 실제 핵심 출력:

```text
user.name=김만복
user.email=***@***
init.defaultbranch=main
origin https://github.com/manbok2028/E1-1.git (fetch)
origin https://github.com/manbok2028/E1-1.git (push)
0bf6e0d6... refs/heads/main
```

Git은 내 컴퓨터에서 변경 이력·브랜치를 관리하는 도구이고, GitHub는 그 Git 저장소를 원격으로 공유하고 협업하는 플랫폼이다. 이 저장소는 원격 `origin`이 `manbok2028/E1-1`에 연결되어 있으며, 최종 커밋 푸시로 연동을 다시 확인한다.
