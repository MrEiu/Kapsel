"""
KPS-Hub Standalone REST API Server.
Can run via FastAPI/uvicorn OR via Python standard library HTTP server (zero external dependencies).
Provides endpoints for packages, commands, mappings, search, snapshot bundle, and device sync.
"""

import json
from pathlib import Path
import sys
from urllib.parse import parse_qs, urlparse

from db import HubRepository
from seed import seed_database

# Initialize database if empty
repo = HubRepository()
if repo.get_stats()["packages_count"] == 0:
    seed_database(repo)


def build_fastapi_app():
    """Builds the FastAPI application if FastAPI is installed."""
    try:
        from fastapi import FastAPI, HTTPException, Query
        from fastapi.middleware.cors import CORSMiddleware
        from pydantic import BaseModel
    except ImportError:
        return None

    app = FastAPI(
        title="💊 KPS-Hub API",
        version="1.0.0",
        description="Central Cloud Repository REST API for Kapsel Terminal Capsule",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health():
        return {"status": "ok", "service": "KPS-Hub", "version": "1.0.0"}

    @app.get("/api/v1/stats")
    def stats():
        return repo.get_stats()

    @app.get("/api/v1/packages")
    def list_packages(platform: str = Query(None)):
        return {"packages": repo.list_packages(platform)}

    @app.get("/api/v1/packages/{software}")
    def get_package(software: str):
        pkg = repo.get_package(software)
        if not pkg:
            raise HTTPException(status_code=404, detail="Software not found")
        cmds = repo.get_commands_for_software(software)
        return {"package": pkg, "commands": cmds}

    @app.get("/api/v1/mappings")
    def list_mappings(shell: str = "pwsh"):
        return {"shell": shell, "mappings": repo.list_mappings(shell)}

    @app.get("/api/v1/search")
    def search(q: str = Query(..., min_length=1)):
        return repo.search_all(q)

    @app.get("/api/v1/bundle")
    def get_bundle():
        """Full snapshot bundle for client 1-click synchronization."""
        return repo.export_all()

    class UserRegisterRequest(BaseModel):
        username: str
        email: str = ""
        sync_key: str
        device_id: str

    @app.post("/api/v1/auth/register")
    def register_user(req: UserRegisterRequest):
        success = repo.register_user(req.username, req.email, req.sync_key, req.device_id)
        return {"success": success, "username": req.username}

    return app


# ==================== Standalone Pure-Python HTTP Fallback ====================

def run_stdlib_server(host: str = "0.0.0.0", port: int = 8000):
    from http.server import BaseHTTPRequestHandler, HTTPServer

    class HubHandler(BaseHTTPRequestHandler):
        def _send_json(self, data, status: int = 200):
            payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(payload)

        def do_GET(self):
            parsed = urlparse(self.path)
            path = parsed.path.rstrip("/")
            params = parse_qs(parsed.query)

            if path in ("", "/health"):
                return self._send_json({"status": "ok", "service": "KPS-Hub", "version": "1.0.0"})

            if path == "/api/v1/stats":
                return self._send_json(repo.get_stats())

            if path == "/api/v1/packages":
                platform = params.get("platform", [None])[0]
                return self._send_json({"packages": repo.list_packages(platform)})

            if path.startswith("/api/v1/packages/"):
                software = path.split("/")[-1]
                pkg = repo.get_package(software)
                if not pkg:
                    return self._send_json({"error": "Software not found"}, 404)
                cmds = repo.get_commands_for_software(software)
                return self._send_json({"package": pkg, "commands": cmds})

            if path == "/api/v1/mappings":
                shell = params.get("shell", ["pwsh"])[0]
                return self._send_json({"shell": shell, "mappings": repo.list_mappings(shell)})

            if path == "/api/v1/search":
                q = params.get("q", [""])[0]
                if not q:
                    return self._send_json({"error": "Query param 'q' required"}, 400)
                return self._send_json(repo.search_all(q))

            if path == "/api/v1/bundle":
                return self._send_json(repo.export_all())

            return self._send_json({"error": "Not Found"}, 404)

        def do_POST(self):
            parsed = urlparse(self.path)
            path = parsed.path.rstrip("/")
            content_len = int(self.headers.get("Content-Length", 0))
            post_body = self.rfile.read(content_len)

            try:
                data = json.loads(post_body.decode("utf-8"))
            except Exception:
                return self._send_json({"error": "Invalid JSON"}, 400)

            if path == "/api/v1/auth/register":
                username = data.get("username")
                sync_key = data.get("sync_key")
                device_id = data.get("device_id")
                email = data.get("email", "")
                if not username or not sync_key:
                    return self._send_json({"error": "username and sync_key required"}, 400)
                repo.register_user(username, email, sync_key, device_id)
                return self._send_json({"success": True, "username": username})

            return self._send_json({"error": "Not Found"}, 404)

        def log_message(self, format, *args):
            # Clean logging
            print(f"[KPS-Hub] {self.address_string()} - {format % args}")

    server = HTTPServer((host, port), HubHandler)
    print(f"🚀 KPS-Hub Standalone Server listening on http://{host}:{port}")
    print("   Endpoints:")
    print(f"   • Health:   http://{host}:{port}/health")
    print(f"   • Stats:    http://{host}:{port}/api/v1/stats")
    print(f"   • Packages: http://{host}:{port}/api/v1/packages")
    print(f"   • Mappings: http://{host}:{port}/api/v1/mappings?shell=pwsh")
    print(f"   • Bundle:   http://{host}:{port}/api/v1/bundle")
    server.serve_forever()


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Run KPS-Hub Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host address (default 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Port (default 8000)")
    parser.add_argument("--fastapi", action="store_true", help="Force FastAPI/uvicorn server")
    args = parser.parse_args()

    app = build_fastapi_app()
    if app and args.fastapi:
        import uvicorn
        print(f"🚀 Starting KPS-Hub with Uvicorn (FastAPI) on http://{args.host}:{args.port}...")
        uvicorn.run(app, host=args.host, port=args.port)
    else:
        run_stdlib_server(args.host, args.port)


if __name__ == "__main__":
    main()
