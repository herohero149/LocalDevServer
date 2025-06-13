# Modern Local Dev Server with Hot Reload ⚡🔥

> A sleek, modern development server with live reload capability, beautiful UI, and zero configuration needed.

---

## ✨ Features 

- 📂 Modern, animated file browser interface
- 🔄 Hot reloads browser on `.html`, `.css`, `.js` changes
- 🎨 Beautiful, responsive design with dark mode support
- 🚀 Super lightweight and fast
- 🛠️ Zero configuration needed
- 📱 Mobile-friendly interface
- 🌓 Automatic dark mode support
- 🔍 Sortable file listings
- 💻 Built with modern Python

---

## 🚀 Quick Start

1. Clone this repository or download the files:
   ```bash
   git clone https://github.com/ArchieTUX/LocalDevServer.git
   cd LocalDevServer
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the server:
   ```bash
   python dev_server.py
   ```
   Or specify a custom port:
   ```bash
   python dev_server.py 8080
   ```

4. Open your browser:
   ```
   http://localhost:8000
   ```

5. Start editing your files - the browser will automatically refresh on changes!

---

## 🔧 How it Works

- Runs a modern HTTP server with WebSocket support
- Provides a beautiful, animated file browser interface
- Automatically watches for file changes
- Injects a tiny WebSocket client for hot reload
- Handles all static files with proper MIME types
- Supports both light and dark themes

## Why use this? 🤔

* No bulky frameworks or dev servers needed
* Great for quick prototyping or static sites
* Hot reload keeps your flow unbroken
* Perfect for developers who love minimalism and speed

## 💡 Tips

- The server automatically finds a free port if the default is in use
- All HTML files get hot-reload capability automatically
- Use dark mode for better visibility in low light
- Click column headers to sort files
- Works great with any static web project

## 🛟 Troubleshooting

If you see "Address already in use":
- The server will automatically try the next available port
- You can also specify a different port: `python dev_server.py 8080`

If hot reload isn't working:
- Make sure your browser supports WebSocket
- Check if the WebSocket port is not blocked by firewall

## 📝 License

This project is licensed under the MIT [License](LICENSE) — do whatever, just don’t sue me.

---

Made with ⚡ by Adithya — Making development smoother, one reload at a time.
