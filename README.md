````markdown
# Lightweight Local Dev Server with Hot Reload ⚡🔥

> Serve your project folder instantly with auto-refresh on code changes — zero bloat, pure productivity.

---

## Features 🚀

- 📂 Serves files from your current directory  
- 🔄 Hot reloads browser on `.html`, `.css`, `.js` changes  
- ⚡ Super lightweight — minimal code, minimal hassle  
- 🛠️ Zero setup, just run and code  
- 🔒 No external dependencies except one tiny Python lib (`websockets`)  

---

## Quickstart ⚡

1. Clone/download the `dev_server.py` script  
2. Install required lib:

   ```bash
   pip install websockets
````

3. Run the server:

   ```bash
   python dev_server.py
   ```

4. Open your browser at:

   ```
   http://localhost:8000
   ```

5. Edit your `.html`, `.css`, or `.js` files — browser auto-refreshes instantly

---

## How it works 🧠

* Runs an HTTP server serving files in the current directory
* Injects a tiny WebSocket client script into HTML pages
* Watches files for changes, notifies browser clients via WebSocket to reload

---

## Why use this? 🤔

* No bulky frameworks or dev servers needed
* Great for quick prototyping or static sites
* Hot reload keeps your flow unbroken
* Perfect for developers who love minimalism and speed

---

## License 📝

Licensed under **GNU GPL v3.0** — freedom to use, modify, and share.

---

Made with ⚡ by Adithya — powering your dev hustle, one reload at a time.

```
```
