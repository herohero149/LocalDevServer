import http.server
import socketserver
import threading
import os
import time
import sys
import mimetypes
from http import HTTPStatus
import websocket
import asyncio
import websockets

PORT = 8000
WATCHED_EXTENSIONS = {'.html', '.css', '.js'}

# Simple HTTP Handler to serve files from cwd
class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Disable cache for dev
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def send_head(self):
        path = self.translate_path(self.path)
        if os.path.isdir(path):
            for index in ["index.html", "index.htm"]:
                index_path = os.path.join(path, index)
                if os.path.exists(index_path):
                    path = index_path
                    break
            else:
                return self.list_directory(path)
        ctype = self.guess_type(path)

        try:
            f = open(path, 'rb')
        except OSError:
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")
            return None

        # For html files, inject websocket reload script
        if path.endswith(".html"):
            content = f.read().decode('utf-8')
            f.close()
            content += """
<script>
(() => {
    let ws = new WebSocket('ws://localhost:8765');
    ws.onmessage = (msg) => {
        if(msg.data === 'reload') location.reload();
    };
})();
</script>
"""
            encoded = content.encode('utf-8')
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-type", ctype)
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            return io.BytesIO(encoded)
        else:
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-type", ctype)
            fs = os.fstat(f.fileno())
            self.send_header("Content-Length", str(fs[6]))
            self.end_headers()
            return f


def watch_files(on_change):
    files_mtimes = {}
    while True:
        changed = False
        for root, _, files in os.walk('.'):
            for file in files:
                if os.path.splitext(file)[1] in WATCHED_EXTENSIONS:
                    path = os.path.join(root, file)
                    try:
                        mtime = os.path.getmtime(path)
                    except FileNotFoundError:
                        continue
                    if path not in files_mtimes:
                        files_mtimes[path] = mtime
                    elif files_mtimes[path] != mtime:
                        files_mtimes[path] = mtime
                        changed = True
        if changed:
            on_change()
        time.sleep(1)


connected_clients = set()

async def ws_handler(websocket):
    connected_clients.add(websocket)
    try:
        async for _ in websocket:
            pass
    finally:
        connected_clients.remove(websocket)

def notify_reload():
    print("[*] Change detected, notifying clients...")
    loop = asyncio.get_event_loop()
    if connected_clients:
        tasks = [client.send('reload') for client in connected_clients]
        loop.run_until_complete(asyncio.wait(tasks))


def main():
    import io

    # HTTP server
    handler = Handler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"Serving at http://localhost:{PORT}")

        # Websocket server for hot reload
        start_server = websockets.serve(ws_handler, "localhost", 8765)

        loop = asyncio.get_event_loop()

        # Start websocket server in background
        loop.run_until_complete(start_server)

        # Start file watcher in separate thread
        watcher_thread = threading.Thread(target=watch_files, args=(notify_reload,), daemon=True)
        watcher_thread.start()

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")


if __name__ == "__main__":
    main()
