# 요구사항 대응표

| 요구사항 | 구현·검증 결과 | 확인 위치 |
| --- | --- | --- |
| 프로젝트 개요·목표 | 재현 가능한 개발 작업실의 목적과 구성 | [README](../README.md), [평가 보고서](evaluation-report.md) |
| OS/셸/터미널·Docker·Git 버전 | Windows PowerShell, Docker Desktop 29.9.2, Git 2.55.0 확인 | [실행 로그](verification-log.md) |
| CLI 기본 조작 | 위치·숨김 목록·이동·생성·복사·이름변경·내용 확인·삭제 실제 실행 | [실행 로그 1절](verification-log.md#1-터미널-기본-조작) |
| 파일·디렉터리 권한 | Ubuntu에서 700/600 → 755/644 전후 `stat` 확인 | [실행 로그 2절](verification-log.md#2-linux-권한-실습) |
| Docker 설치/데몬/운영 | `docker --version`, `docker info`, images, ps, logs, stats | [실행 로그 3·5절](verification-log.md) |
| hello-world·Ubuntu | hello-world 성공, Ubuntu 내부 `pwd`, `ls`, `echo` 실행 | [실행 로그 3절](verification-log.md#3-docker-설치기본-운영) |
| Dockerfile 커스텀 이미지 | NGINX 베이스에 설정·콘텐츠·ENV·LABEL·HEALTHCHECK 추가 | [Dockerfile](../Dockerfile), [실행 로그 4절](verification-log.md#4-dockerfile-커스텀-이미지) |
| 포트 매핑·접속 | `18080:8080`, curl HTTP 200 및 health 응답 | [README](../README.md), [실행 로그 5절](verification-log.md#5-포트-매핑접속운영-로그) |
| 바인드 마운트 | `app`을 읽기 전용으로 연결, v1→v2 즉시 반영 | [실행 로그 6절](verification-log.md#6-바인드-마운트-반영) |
| 볼륨 영속성 | 컨테이너 A 삭제 뒤 B와 일회성 컨테이너에서 파일 재확인 | [실행 로그 7절](verification-log.md#7-docker-볼륨-영속성) |
| Git·GitHub | global 설정(마스킹), `origin`, 원격 main, 최종 push | [실행 로그 9절](verification-log.md#9-gitgithub-연동) |
| 트러블슈팅 2건 이상 | 권한 기본값, 바인드 마운트 경로, health 상태 관찰 | [트러블슈팅](troubleshooting.md) |
| 보너스 Compose | `up`, `ps`, `logs`, `down` 실제 실행 | [docker-compose.yml](../docker-compose.yml), [실행 로그 8절](verification-log.md#8-compose-보너스) |
