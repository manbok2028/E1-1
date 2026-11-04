"""Generate PNG evidence from live Docker commands for the E1-1 submission.

The script re-runs safe, isolated checks and renders the *actual command and
stdout/stderr* into terminal-style PNG files under evidence/screenshots.
It also captures the running web page with Chrome headless. Temporary Docker
containers, a temporary volume, and a temporary host directory are removed in
finally blocks.

Run from the repository root:
    python scripts/generate_evidence_png.py
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "evidence" / "screenshots"
IMAGE = "e1-1-workstation-web:1.0"
CHROME = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")


def run(*command: str, check: bool = True) -> tuple[int, str]:
    """Run a command and return a normalized transcript without secrets."""

    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    output = completed.stdout.strip() or "(no output)"
    if check and completed.returncode:
        raise RuntimeError(f"Command failed ({completed.returncode}): {' '.join(command)}\n{output}")
    return completed.returncode, output


def command_text(command: tuple[str, ...]) -> str:
    return " ".join(command)


def font(size: int, mono: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        Path(r"C:\Windows\Fonts\consola.ttf") if mono else Path(r"C:\Windows\Fonts\malgun.ttf"),
        Path(r"C:\Windows\Fonts\arial.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def render_terminal(filename: str, title: str, command: str, output: str) -> None:
    """Render a readable terminal transcript to a PNG image."""

    OUTPUT.mkdir(parents=True, exist_ok=True)
    body_font = font(22, mono=True)
    title_font = font(28)
    lines = [f"$ {command}", "", *output.splitlines()]
    wrapped: list[str] = []
    for line in lines:
        wrapped.extend(textwrap.wrap(line, width=88, replace_whitespace=False) or [""])

    line_height = 31
    width = 1680
    height = max(300, 122 + line_height * (len(wrapped) + 1))
    image = Image.new("RGB", (width, height), "#10161f")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((24, 20, width - 24, height - 20), radius=18, fill="#172131", outline="#3b4b62", width=2)
    draw.ellipse((50, 46, 64, 60), fill="#ff6b6b")
    draw.ellipse((74, 46, 88, 60), fill="#ffd166")
    draw.ellipse((98, 46, 112, 60), fill="#72e6a6")
    draw.text((140, 38), title, font=title_font, fill="#eaf1ff")

    y = 94
    for line in wrapped:
        color = "#76e6b6" if line.startswith("$ ") else "#d9e4f2"
        draw.text((54, y), line, font=body_font, fill=color)
        y += line_height
    image.save(OUTPUT / filename)


def remove_container(name: str) -> None:
    run("docker", "rm", "-f", name, check=False)


def hello_world() -> None:
    command = ("docker", "run", "--rm", "hello-world")
    _, output = run(*command)
    render_terminal("01-hello-docker.png", "01 · Docker hello-world actual output", command_text(command), output)


def web_page() -> None:
    command = ("curl.exe", "-i", "http://localhost:18080/")
    _, output = run(*command)
    render_terminal("02-port-mapping-curl.png", "02 · Port mapping HTTP response", command_text(command), output)
    if not CHROME.exists():
        raise RuntimeError(f"Chrome not found: {CHROME}")
    screenshot = OUTPUT / "02-web-page.png"
    run(
        str(CHROME),
        "--headless",
        "--disable-gpu",
        "--no-first-run",
        f"--screenshot={screenshot}",
        "--window-size=1440,1000",
        "http://localhost:18080/",
    )


def permission_fix() -> None:
    shell = (
        "mkdir -p /tmp/permission-lab; touch /tmp/permission-lab/example.txt; "
        "chmod 700 /tmp/permission-lab; chmod 600 /tmp/permission-lab/example.txt; "
        "echo before; stat -c '%a %n' /tmp/permission-lab /tmp/permission-lab/example.txt; "
        "chmod 755 /tmp/permission-lab; chmod 644 /tmp/permission-lab/example.txt; "
        "echo after; stat -c '%a %n' /tmp/permission-lab /tmp/permission-lab/example.txt"
    )
    command = ("docker", "run", "--rm", "ubuntu:latest", "bash", "-lc", shell)
    _, output = run(*command)
    render_terminal("03-permission-before-after.png", "03 · Permission issue fixed (before → after)", command_text(command), output)


def bind_mount_fix() -> None:
    container = "e1-1-evidence-bind"
    with tempfile.TemporaryDirectory(prefix="e1-1-bind-") as folder:
        host = Path(folder)
        index = host / "index.html"
        index.write_text("<h1 id='proof'>bind-mount-before-v1</h1>", encoding="utf-8")
        remove_container(container)
        try:
            run("docker", "run", "-d", "--name", container, "-p", "18083:8080", "-v", f"{host}:/usr/share/nginx/html:ro", IMAGE)
            _, before = run("curl.exe", "-sS", "http://localhost:18083/")
            index.write_text("<h1 id='proof'>bind-mount-after-v2</h1>", encoding="utf-8")
            _, after = run("curl.exe", "-sS", "http://localhost:18083/")
            _, mount = run("docker", "inspect", container, "--format", "{{range .Mounts}}{{.Type}} {{.Source}} -> {{.Destination}} RW={{.RW}}{{end}}")
            mount = mount.replace(str(host), "<temporary-host-dir>")
            transcript = f"BEFORE\n{before}\n\nAFTER (no rebuild / no restart)\n{after}\n\nMOUNT\n{mount}"
            render_terminal("04-bind-mount-before-after.png", "04 · Bind mount live-reload proof", "docker run -v <host>:/usr/share/nginx/html:ro ...", transcript)
        finally:
            remove_container(container)


def volume_persistence() -> None:
    volume = "e1-1-evidence-volume"
    first = "e1-1-evidence-volume-a"
    second = "e1-1-evidence-volume-b"
    remove_container(first)
    remove_container(second)
    run("docker", "volume", "rm", volume, check=False)
    try:
        _, created = run("docker", "volume", "create", volume)
        run("docker", "run", "-d", "--name", first, "-v", f"{volume}:/data", "ubuntu:latest", "sleep", "infinity")
        _, written = run("docker", "exec", first, "bash", "-lc", "printf 'persistent-data-ok\\n' > /data/proof.txt; cat /data/proof.txt")
        run("docker", "rm", "-f", first)
        run("docker", "run", "-d", "--name", second, "-v", f"{volume}:/data", "ubuntu:latest", "sleep", "infinity")
        _, reread = run("docker", "exec", second, "bash", "-lc", "cat /data/proof.txt")
        transcript = f"VOLUME CREATED\n{created}\n\nWRITE IN CONTAINER A\n{written}\n\nDELETE CONTAINER A\nremoved\n\nREAD IN NEW CONTAINER B\n{reread}"
        render_terminal("05-volume-persistence.png", "05 · Docker volume persistence proof", "docker volume create / run / rm / run / cat", transcript)
    finally:
        remove_container(first)
        remove_container(second)
        run("docker", "volume", "rm", volume, check=False)


def compose_bonus() -> None:
    try:
        run("docker", "compose", "up", "-d", "--build")
        _, mode = run("docker", "compose", "exec", "-T", "workstation-web", "sh", "-lc", "echo $APP_MODE")
        _, network = run("docker", "compose", "exec", "-T", "workstation-web", "wget", "-qO-", "http://status-api:5678")
        _, status = run("docker", "compose", "ps")
        transcript = f"APP_MODE\n{mode}\n\nSERVICE-DISCOVERY RESPONSE\n{network}\n\nCOMPOSE PS\n{status}"
        render_terminal("06-compose-multicontainer.png", "06 · Compose multi-container bonus proof", "docker compose up / exec / ps / down", transcript)
    finally:
        run("docker", "compose", "down", check=False)


def main() -> None:
    if shutil.which("docker") is None:
        raise SystemExit("Docker CLI is required.")
    hello_world()
    web_page()
    permission_fix()
    bind_mount_fix()
    volume_persistence()
    compose_bonus()
    print(f"PNG evidence created: {OUTPUT}")


if __name__ == "__main__":
    main()
