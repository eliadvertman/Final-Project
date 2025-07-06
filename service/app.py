# app.py
from http.server import HTTPServer, BaseHTTPRequestHandler
import os

PORT = 8080

# Define a custom request handler by inheriting from BaseHTTPRequestHandler
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    # Handle GET requests
    def do_GET(self):
        # Set the response status code to 200 (OK)
        self.send_response(200)
        # Set the Content-type header to text/html
        self.send_header('Content-type', 'text/html')
        # End the headers section
        self.end_headers()

        # Define the message to send as the response body
        message = "<h1>Hello from the Python Webserver!</h1>"
        message += f"<p>This server is running on port {PORT}.</p>"
        message += f"<p>Current working directory: {os.getcwd()}</p>"

        # Encode the message to bytes and send it as the response body
        self.wfile.write(bytes(message, "utf8"))

# Main entry point of the script
if __name__ == "__main__":
    # Create an HTTP server instance
    # The server will listen on all available interfaces (0.0.0.0) and the specified PORT
    httpd = HTTPServer(('0.0.0.0', PORT), SimpleHTTPRequestHandler)
    print(f"Starting httpd server on port {PORT}")
    # Start the server and keep it running indefinitely until interrupted
    httpd.serve_forever()

