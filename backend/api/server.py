from __future__ import annotations

import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

BACKEND_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from api.package_build import PackageBuildService
from api.spec_generation import ApiError, SpecGenerationService


def create_spec_service() -> SpecGenerationService:
    return SpecGenerationService(schema_path=REPO_ROOT / "schemas" / "asset-spec.schema.json")


class ApiHandler(BaseHTTPRequestHandler):
    spec_service = create_spec_service()
    package_service = PackageBuildService()

    def do_GET(self) -> None:
        if self.path == "/health":
            self._send_json(200, {"status": "ok"})
            return
        self._send_json(404, {"error": {"code": "not_found", "message": "Route not found."}})

    def do_POST(self) -> None:
        if self.path == "/api/specs/generate":
            self._handle_specs_generate()
            return

        if self.path == "/api/packages/build":
            self._handle_packages_build()
            return

        self._send_json(404, {"error": {"code": "not_found", "message": "Route not found."}})

    def _handle_specs_generate(self) -> None:
        try:
            payload = self._read_json_body()
            response = self.spec_service.generate(payload)
            self._send_json(200, response)
        except ApiError as error:
            self._send_json(
                error.status_code,
                {"error": {"code": error.code, "message": error.message}},
            )
        except RuntimeError as error:
            self._send_json(
                502,
                {"error": {"code": "provider_error", "message": str(error)}},
            )
        except json.JSONDecodeError:
            self._send_json(
                400,
                {"error": {"code": "invalid_json", "message": "Request body must be valid JSON."}},
            )

    def _handle_packages_build(self) -> None:
        try:
            payload = self._read_json_body()
            response = self.package_service.build(payload)
            self._send_json(200, response)
        except ApiError as error:
            self._send_json(
                error.status_code,
                {"error": {"code": error.code, "message": error.message}},
            )
        except json.JSONDecodeError:
            self._send_json(
                400,
                {"error": {"code": "invalid_json", "message": "Request body must be valid JSON."}},
            )

    def _read_json_body(self) -> dict[str, Any]:
        content_length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(content_length).decode("utf-8")
        payload = json.loads(body or "{}")
        if not isinstance(payload, dict):
            raise ApiError(400, "invalid_body", "Request body must be a JSON object.")
        return payload

    def _send_json(self, status_code: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: Any) -> None:
        return


def main() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 8000), ApiHandler)
    print("Serving AI Game Mod Studio API at http://127.0.0.1:8000")
    server.serve_forever()


if __name__ == "__main__":
    main()
