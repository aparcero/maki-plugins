"""Check the actual request from the installed Maki, with isolated config/auth."""

import json
import os
from itertools import product
from pathlib import Path
import shutil
import subprocess
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from package_fixture import install_package



class ZaiLocalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not shutil.which("maki"):
            raise RuntimeError("just check requires maki 0.7.0+ on PATH")
        if (Path.home() / ".maki").exists():
            raise RuntimeError("Legacy ~/.maki would override isolated configuration")

    def test_requests_use_glm_effort_levels(self):
        with tempfile.TemporaryDirectory(prefix="maki-zai-local-test-") as directory:
            root = Path(directory)
            config = root / "config/maki"
            config.mkdir(parents=True)
            install_package(root)
            (config / "plugin.toml").write_text('[permissions]\nenv = false\nnet = false\n')
            env = {k: v for k, v in os.environ.items() if k in (
                "PATH", "HOME", "USERPROFILE", "SYSTEMROOT", "WINDIR", "TEMP", "TMP", "LANG",
            )}
            for kind in ("CONFIG", "DATA", "STATE", "CACHE"):
                env[f"XDG_{kind}_HOME"] = str(root / kind.lower())
            if os.name == "nt":
                env["APPDATA"] = str(root / "config")
                env["LOCALAPPDATA"] = str(root / "data")
            env["ZHIPU_API_KEY"] = "local-test-placeholder"
            requests = []

            class Server(BaseHTTPRequestHandler):
                def log_message(self, *_args):
                    pass

                def do_POST(self):
                    body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                    requests.append((self.path, self.headers.get("Authorization"), body))
                    chunk = {"id": "fixture", "object": "chat.completion.chunk",
                             "choices": [{"index": 0, "delta": {"role": "assistant", "content": "OK"},
                                          "finish_reason": "stop"}]}
                    data = f"data: {json.dumps(chunk)}\n\ndata: [DONE]\n\n".encode()
                    self.send_response(200)
                    self.send_header("Content-Type", "text/event-stream")
                    self.send_header("Content-Length", str(len(data)))
                    self.end_headers()
                    self.wfile.write(data)

            server = ThreadingHTTPServer(("127.0.0.1", 0), Server)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                (config / "providers.toml").write_text(
                    '[zai-local]\n'
                    f'base_url = "http://127.0.0.1:{server.server_port}/api/coding/paas/v4"\n'
                )
                efforts = ((None, "low"), ("adaptive", "max"), ("low", "low"),
                           ("high", "high"), ("max", "max"), (False, "low"))
                for model, (effort, expected) in product(("glm-5.3", "glm-5.4"), efforts):
                    with self.subTest(model=model, effort=effort):
                        setup = "" if effort is None else (
                            "maki.setup({ always_thinking = " + json.dumps(effort) + " })\n"
                        )
                        (config / "init.lua").write_text(setup)
                        before = len(requests)
                        result = subprocess.run(
                            ["maki", "-p", "--model", f"zai-local/{model}", "--max-turns", "1", "Say OK."],
                            cwd=root, env=env, capture_output=True, text=True, timeout=60,
                        )
                        self.assertEqual(result.returncode, 0, result.stderr + result.stdout[-2000:])
                        self.assertEqual(len(requests), before + 1)
                        path, authorization, body = requests[-1]
                        self.assertEqual(path, "/api/coding/paas/v4/chat/completions")
                        self.assertEqual(authorization, "Bearer local-test-placeholder")
                        self.assertEqual(body["model"], model)
                        self.assertEqual(body["reasoning_effort"], expected)
                        self.assertEqual(body["thinking"], {"type": "enabled"})
            finally:
                server.shutdown()
                server.server_close()
                thread.join()
