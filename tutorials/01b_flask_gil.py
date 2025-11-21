"""
Flask - GIL Blocking Demo
=========================

Demonstrates that CPU-bound tasks block ALL threads due to Python's GIL,
even with threaded=True. The GIL ensures only one thread executes Python
bytecode at a time.

Compare:
- /slow-io    : I/O wait (releases GIL) - concurrent requests work
- /slow-cpu   : CPU work (holds GIL) - blocks other requests
"""

from flask import Flask, jsonify
import time

app = Flask(__name__)


def fibonacci(n):
    """CPU-intensive recursive Fibonacci - holds the GIL."""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


@app.route("/")
def index():
    return jsonify({"message": "Flask GIL Demo"})


@app.route("/slow-io")
def slow_io():
    """
    I/O-bound: time.sleep() releases the GIL.
    Multiple requests can wait concurrently.
    """
    time.sleep(5)
    return jsonify({"type": "io", "message": "Done after 5s sleep"})


@app.route("/slow-cpu")
def slow_cpu():
    """
    CPU-bound: Fibonacci holds the GIL.
    Other threads must wait - no true parallelism.
    """
    result = fibonacci(38)  # Takes ~3-5 seconds
    return jsonify({"type": "cpu", "result": result})


if __name__ == "__main__":
    print("""
Flask GIL Demo (threaded=True)
==============================
GET /           - Fast endpoint
GET /slow-io    - I/O wait 5s (releases GIL)
GET /slow-cpu   - CPU Fibonacci (holds GIL)

Test GIL blocking:
  # Terminal 1: Start CPU task
  curl http://localhost:5002/slow-cpu

  # Terminal 2: Try fast endpoint (will be blocked!)
  curl http://localhost:5002/

Compare with I/O:
  # Terminal 1: Start I/O task
  curl http://localhost:5002/slow-io

  # Terminal 2: Fast endpoint works immediately
  curl http://localhost:5002/
    """)
    # threaded=True but GIL still blocks CPU-bound work
    app.run(debug=True, port=5002, threaded=True)
