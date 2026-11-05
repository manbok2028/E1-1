# Docker 볼륨 영속성 실습 기록

## 실습 목표

Docker 볼륨이 컨테이너의 임시 파일 시스템과 분리되어, 컨테이너 삭제 뒤에도 파일을 보존하는지 검증한다.

## 2026-11-05 실제 실행

```powershell
# Docker가 관리하는 볼륨 생성
docker volume create e1-1-data

# 첫 컨테이너에 볼륨을 연결하고 증빙 파일 기록
docker run -d --name e1-1-vol -v e1-1-data:/data ubuntu:latest sleep infinity
docker exec e1-1-vol bash -lc "printf 'volume-persistence-confirmed-2026-11-05\n' > /data/evaluator-proof.txt; cat /data/evaluator-proof.txt"

# 첫 컨테이너만 삭제한다. e1-1-data 볼륨은 삭제하지 않는다.
docker rm -f e1-1-vol

# 새 일회성 컨테이너에 같은 볼륨을 연결해 파일을 다시 읽는다.
docker run --rm -v e1-1-data:/data ubuntu:latest bash -lc "cat /data/evaluator-proof.txt"
docker volume inspect e1-1-data
```

## 실제 결과

```text
volume-persistence-confirmed-2026-11-05  # 첫 컨테이너에서 기록 확인
e1-1-vol                                  # 첫 컨테이너 삭제 완료
volume-persistence-confirmed-2026-11-05  # 새 컨테이너에서 재확인 성공
Name=e1-1-data
Mountpoint=/var/lib/docker/volumes/e1-1-data/_data
```

## 결론

`evaluator-proof.txt`는 첫 컨테이너의 쓰기 레이어가 아니라 `e1-1-data` 볼륨에 저장되었다. 따라서 `docker rm -f e1-1-vol`로 컨테이너를 삭제해도 데이터가 유지된다. 데이터까지 완전히 제거하려면 별도로 `docker volume rm e1-1-data`를 실행해야 한다.

## 평가자가 확인할 위치

- 이 문서의 실제 실행 명령과 결과
- [README의 Docker 볼륨 영속성 안내](../README.md#필수-확인-docker-볼륨-영속성)
- 기존 전체 볼륨 검증 로그: [verification-log.md 7절](verification-log.md#7-docker-볼륨-영속성)
- PNG 증빙: [05-volume-persistence.png](../evidence/screenshots/05-volume-persistence.png)
