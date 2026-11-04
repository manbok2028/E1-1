# PNG 증빙 파일

이 폴더의 PNG는 `scripts/generate_evidence_png.py`가 실행 시점의 실제 Docker 명령 출력과 HTTP 응답을 렌더링해 만든 시각 증빙이다. 예시 이미지를 임의로 제작하지 않는다.

| 파일 | 실제로 검증하는 내용 |
| --- | --- |
| `01-hello-docker.png` | `docker run --rm hello-world` 성공 출력 |
| `02-port-mapping-curl.png` | `http://localhost:18080/`의 HTTP 200·응답 HTML |
| `02-web-page.png` | 실행 중인 NGINX 웹 화면 캡처 |
| `03-permission-before-after.png` | Linux 권한 700/600 → 755/644 개선 |
| `04-bind-mount-before-after.png` | 바인드 마운트 v1 → v2 즉시 반영 |
| `05-volume-persistence.png` | 컨테이너 삭제 뒤 새 컨테이너에서 볼륨 데이터 읽기 |
| `06-compose-multicontainer.png` | Compose 환경 변수·서비스 이름 통신 |

재생성 방법:

```powershell
python -m pip install -r requirements-evidence.txt
python scripts/generate_evidence_png.py
```

실행 중 임시 컨테이너·임시 볼륨·임시 호스트 폴더는 모두 정리된다. 기존 `e1-1-web`과 `e1-1-bind` 컨테이너는 변경하지 않는다.
