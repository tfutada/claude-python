"""
Flask - Synchronous Web Framework
=================================

Flask is synchronous: each request blocks the worker thread.
"""

from flask import Flask, jsonify
import time

app = Flask(__name__)


@app.route("/")
def index():
    """Sync endpoint - blocks worker thread."""
    return jsonify({"message": "Hello from Flask"})


@app.route("/slow")
def slow():
    """Blocks for 10 seconds - no other requests can be handled by this worker."""
    time.sleep(10) # GIL is released during sleep, but the thread is blocked. OS kerel takeof sleep timer.
    fibonacci(35)  # Simulate CPU work holding the GIL even multiple threads mode.
    return jsonify({"message": "Done after 10s"})


if __name__ == "__main__":
    print("""
Flask (Sync)
============
GET /      - Fast endpoint
GET /slow  - Blocks for 2 seconds

Test with: curl http://localhost:5001/slow
    """)
    app.run(debug=True, port=5001, threaded=True)
