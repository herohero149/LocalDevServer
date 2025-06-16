import http.server
import socketserver
import threading
import os
import time
import sys
import io
import mimetypes
import html
from http import HTTPStatus
import websocket
import asyncio
import websockets
import socket
from datetime import datetime
import webbrowser

def find_free_port(start_port, max_attempts=10):
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('', port))
                return port
            except OSError:
                continue
    raise RuntimeError(f"Could not find a free port after {max_attempts} attempts")

# Try to get port from command line, fallback to finding a free port
try:
    PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
except ValueError:
    print("Invalid port number. Using default.")
    PORT = 8000

try:
    PORT = find_free_port(PORT)
    WS_PORT = find_free_port(PORT + 1)
except RuntimeError as e:
    print(f"Error: {e}")
    sys.exit(1)

WATCHED_EXTENSIONS = {'.html', '.css', '.js'}

# Simple HTTP Handler to serve files from cwd
class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Set the directory to the location of dev_server.py
        super().__init__(*args, directory=os.path.dirname(os.path.abspath(__file__)), **kwargs)

    def end_headers(self):
        # Disable cache for dev
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def list_directory(self, path):
        try:
            list = os.listdir(path)
        except OSError:
            self.send_error(HTTPStatus.NOT_FOUND, "No permission to list directory")
            return None

        list.sort(key=lambda a: (a.lower(), a))
        displaypath = html.escape(self.path)

        # Read the template
        template_path = os.path.join(os.path.dirname(__file__), 'public', 'template.html')
        try:
            with open(template_path, 'r') as f:
                template = f.read()
        except OSError:
            self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR, "Template not found")
            return None

        # Generate file list HTML
        file_list = []
        for name in list:
            fullname = os.path.join(path, name)
            displayname = linkname = name
            if os.path.isdir(fullname):
                displayname = name + "/"
                linkname = name + "/"
            if os.path.islink(fullname):
                displayname = name + "@"

            icon = '📁' if os.path.isdir(fullname) else self.get_file_icon(name)
            
            # File size
            try:
                size = os.path.getsize(fullname)
                if size > 1024*1024:
                    size_str = f'{size/(1024*1024):.1f} MB'
                elif size > 1024:
                    size_str = f'{size/1024:.1f} KB'
                else:
                    size_str = f'{size} bytes'
            except OSError:
                size_str = 'N/A'
            
            # Last modified date
            try:
                mt = os.path.getmtime(fullname)
                mt_str = datetime.fromtimestamp(mt).strftime('%Y-%m-%d %H:%M:%S')
            except OSError:
                mt_str = 'N/A'

            file_list.append(f'''
                <tr>
                    <td><a href="{html.escape(linkname)}">{icon} {html.escape(displayname)}</a></td>
                    <td class="size">{size_str}</td>
                    <td class="date">{mt_str}</td>
                </tr>
            ''')

        # Fill the template
        content = template.format(
            path=displaypath,
            absolutePath=os.path.abspath(path),
            fileList='\n'.join(file_list)
        )

        # Inject websocket reload script
        ws_script = f'''
        <script>
            (() => {{
                let ws = new WebSocket('ws://localhost:{WS_PORT}');
                ws.onmessage = (msg) => {{
                    if(msg.data === 'reload') location.reload();
                }};
            }})();
        </script>
        </body>
        '''
        content = content.replace('</body>', ws_script)

        encoded = content.encode('utf-8')
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        return io.BytesIO(encoded)

    def get_file_icon(self, filename):
        if filename.endswith(('.html', '.htm')):
            return '📄'
        elif filename.endswith('.css'):
            return '🎨'
        elif filename.endswith('.js'):
            return '⚡'
        elif filename.endswith(('.jpg', '.jpeg', '.png', '.gif')):
            return '🖼️'
        return '📄'

    def send_head(self):
        path = self.translate_path(self.path)
        if os.path.isdir(path):
            return self.list_directory(path)
            
        ctype = self.guess_type(path)
        try:
            f = open(path, 'rb')
        except OSError:
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")
            return None

        if path.endswith(('.html', '.htm')):
            content = f.read().decode('utf-8')
            f.close()
            # Inject reload script
            if '<head>' in content:
                insert_pos = content.index('<head>') + 6
            elif '<html>' in content:
                insert_pos = content.index('<html>') + 6
            else:
                insert_pos = 0
                
            reload_script = f'''
                <script>
                    (() => {{
                        let ws = new WebSocket('ws://localhost:{WS_PORT}');
                        ws.onmessage = (msg) => {{
                            if(msg.data === 'reload') location.reload();
                        }};
                    }})();
                </script>
            '''
            content = content[:insert_pos] + reload_script + content[insert_pos:]
            encoded = content.encode('utf-8')
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-type", ctype)
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            return io.BytesIO(encoded)
        
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
    if connected_clients:
        tasks = [client.send('reload') for client in connected_clients]
        asyncio.get_event_loop().run_until_complete(asyncio.wait(tasks))


async def main():
    # HTTP server
    handler = Handler
    try:
        with socketserver.TCPServer(("", PORT), handler) as httpd:
            url = f"http://localhost:{PORT}"
            print(f"Serving at {url}")
            # Open the browser automatically
            threading.Thread(target=lambda: (time.sleep(1), webbrowser.open(url)), daemon=True).start()

            # Websocket server for hot reload
            try:
                start_server = await websockets.serve(ws_handler, "localhost", WS_PORT)
                print(f"WebSocket server running on ws://localhost:{WS_PORT}")
            except OSError as e:
                print(f"Error starting WebSocket server: {e}")
                return

            # Start file watcher in separate thread
            watcher_thread = threading.Thread(target=watch_files, args=(notify_reload,), daemon=True)
            watcher_thread.start()

            loop = asyncio.get_event_loop()
            try:
                await loop.run_in_executor(None, httpd.serve_forever)
            except KeyboardInterrupt:
                print("\nServer stopped.")
    except OSError as e:
        print(f"Error starting HTTP server: {e}")
        return


if __name__ == "__main__":
    asyncio.run(main())
