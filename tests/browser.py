"""Optional real Chrome checks. Needs Node.js and Playwright accessible through NODE_PATH."""
import os
import subprocess
import threading
import uuid

from integration import ROOT, TEST_DB, admin_connection, execute_schema
from werkzeug.serving import make_server


if __name__ == "__main__":
    connection = admin_connection()
    server = None
    try:
        execute_schema(connection)
        os.environ["DB_NAME"] = TEST_DB
        os.environ["SECRET_KEY"] = uuid.uuid4().hex
        from app import app
        server = make_server("127.0.0.1", 0, app)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        result = subprocess.run([os.environ.get("NODE_BINARY", "node"), str(ROOT / "tests/browser.test.js"),
                                 f"http://127.0.0.1:{server.server_port}"], cwd=ROOT)
        raise SystemExit(result.returncode)
    finally:
        if server:
            server.shutdown()
            server.server_close()
        with connection.cursor() as cursor:
            cursor.execute(f"DROP DATABASE IF EXISTS `{TEST_DB}`")
        connection.close()
        print("Disposable browser-test database removed; local application data was not used.")
