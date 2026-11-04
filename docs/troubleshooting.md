# 트러블슈팅 기록

## 1. 권한 변경이 처음에는 “변화 없음”처럼 보인 문제

- **문제:** Ubuntu 컨테이너에서 바로 `chmod 755`와 `chmod 644`를 실행했더니, 전후 `stat` 값이 모두 755/644로 표시됐다.
- **원인 가설:** 새 디렉터리와 파일의 기본 권한이 이미 과제에서 요구하는 최종 값과 같을 수 있다.
- **확인:** `stat -c '%a %n'`으로 확인하니 디렉터리는 755, 파일은 644였다.
- **해결:** 먼저 디렉터리를 700, 파일을 600으로 명시적으로 바꾸고 다시 755/644로 변경했다. 전후 출력이 `700/600 → 755/644`로 확인됐다.
- **배운 점:** 권한 실습은 명령을 실행했다는 사실보다, 기준 상태와 결과 상태를 모두 남겨야 증명 가능하다.

## 2. Windows 호스트 경로와 Linux 컨테이너 경로가 다른 문제

- **문제:** Windows PowerShell의 경로는 `C:\Users\...\app`인데 NGINX 콘텐츠 경로는 `/usr/share/nginx/html`이다.
- **원인 가설:** Docker Desktop이 Windows 호스트 경로를 Linux 컨테이너 경로로 바인드 마운트할 때 구문 또는 파일 공유 문제가 발생할 수 있다.
- **확인:** `docker inspect e1-1-bind` 결과에서 `bind C:\...\app -> /usr/share/nginx/html RW=false`를 확인했고, 포트 18081의 HTTP 응답이 호스트 파일 내용을 반환했다.
- **해결:** PowerShell에서 `${PWD}\app:/usr/share/nginx/html:ro` 형태를 사용하고, 재시작 없이 v1→v2 문구가 바뀌는지 `curl`로 확인했다.
- **대안:** 환경에 따라 `--mount type=bind,src=<절대경로>,dst=/usr/share/nginx/html,readonly` 문법을 쓸 수 있다.

## 3. 컨테이너 실행 직후 health 상태가 `starting`인 문제

- **문제:** `docker run -d` 직후 `docker ps`는 컨테이너가 실행 중이지만 health 상태가 `starting`으로 표시될 수 있다.
- **원인 가설:** Dockerfile의 `HEALTHCHECK --start-period=5s`가 아직 끝나지 않았기 때문이다.
- **확인:** `/health`와 첫 페이지는 HTTP 200을 반환했고, 잠시 뒤 `docker ps`에서 `healthy`로 바뀌었다.
- **해결:** 실행 직후에는 `curl`로 서비스 응답을 확인하고, healthcheck 주기·start period 이후에 상태를 다시 확인한다.
- **배운 점:** 컨테이너 프로세스의 실행 상태와 애플리케이션 건강 상태는 같은 순간에 완성되지 않을 수 있다.
