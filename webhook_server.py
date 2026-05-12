from dotenv import load_dotenv
import hashlib
import hmac
import os
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler

# loads .env file
load_dotenv()

# Key for GitHub to use for sign requests
# Stored in the .env file
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', '')

filePath = os.getenv('FILE_PATH', '')

# class inherited from BaseHTTPRequestHandler from the import
class WebhookHandler(BaseHTTPRequestHandler):

	# function for whenever post is sent to the raspberry pi
	def do_POST(self):

		# read the incoming request body
		content_length = int(self.headers.get("Content-Length", 0))
		body = self.rfile.read(content_length)

		# grabs GitHub's authentication to send post to webhook server
		signature = self.headers.get("X-Hub-Signature-256", "")

		# sha-256 is the hashing used for getting the expected output from the secret and body being hashed together
		expected = "sha256=" + hmac.new(WEBHOOK_SECRET.encode(), body, hashlib.sha256).hexdigest()

		# compares the signature sent by GitHub to the one expected to be received
		# utilizes 'hmac.compare_digest' instead of '==' because of security vulnerabilities
		if not hmac.compare_digest(signature, expected):
			# secret doesn't match so ignore the request with an error response code and message sent back
			self.send_response(403)
			self.end_headers()
			self.wfile.write(b"Forbidden")
			print("Rejected: invalid signature")
			return

		# Secret matches so pull latest code and restart bot
		print("Valid webhook received, updating...")

		# pulls the updated repository from GitHub to update bot
		subprocess.run(["git", "pull"], cwd=filePath)

		# restarts the bot using the 'restart_bot.sh' file
		subprocess.run(["bash", f"{filePath}/restart_bot.sh"])

		# sends response code and message basically saying everything went well
		self.send_response(200)
		self.end_headers()
		self.wfile.write(b"Updated")

	def do_GET(self):
		# ignore any non-POST requests
		# sends an error 404 response code
		self.send_response(404)
		self.end_headers()

# start the server on port 9000
server = HTTPServer(("0.0.0.0", 9000), WebhookHandler)
print("Webhook server running on port 9000...")
server.serve_forever()
