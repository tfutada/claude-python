"""
Flask Tutorial - WSGI Web Framework Basics
==========================================

Flask is a lightweight WSGI web framework. It's synchronous by default,
meaning each request blocks until completion.

Key concepts:
- Routes and URL routing
- Request/Response handling
- Templates (Jinja2)
- Blueprints for modularity
- Application context
"""

from flask import Flask, jsonify, request, g
import time

app = Flask(__name__)

# =============================================================================
# 1. Basic Routes
# =============================================================================

@app.route("/")
def index():
    """Simple route returning HTML."""
    return "<h1>Flask Tutorial</h1><p>Welcome to Flask!</p>"


@app.route("/api/hello")
def hello():
    """JSON API endpoint."""
    return jsonify({"message": "Hello from Flask!"})


# =============================================================================
# 2. Route Parameters
# =============================================================================

@app.route("/user/<username>")
def show_user(username):
    """Dynamic route with URL parameter."""
    return jsonify({"username": username})


@app.route("/post/<int:post_id>")
def show_post(post_id):
    """Type-converted URL parameter."""
    return jsonify({"post_id": post_id, "type": type(post_id).__name__})


# =============================================================================
# 3. HTTP Methods
# =============================================================================

@app.route("/api/items", methods=["GET", "POST"])
def items():
    """Handle multiple HTTP methods."""
    if request.method == "POST":
        data = request.get_json()
        return jsonify({"created": data}), 201
    return jsonify({"items": ["item1", "item2", "item3"]})


@app.route("/api/items/<int:item_id>", methods=["GET", "PUT", "DELETE"])
def item(item_id):
    """CRUD operations on single item."""
    if request.method == "PUT":
        data = request.get_json()
        return jsonify({"updated": item_id, "data": data})
    elif request.method == "DELETE":
        return jsonify({"deleted": item_id})
    return jsonify({"item_id": item_id})


# =============================================================================
# 4. Query Parameters
# =============================================================================

@app.route("/search")
def search():
    """Access query parameters from URL."""
    query = request.args.get("q", "")
    page = request.args.get("page", 1, type=int)
    return jsonify({
        "query": query,
        "page": page,
        "results": [f"Result for '{query}' page {page}"]
    })


# =============================================================================
# 5. Before/After Request Hooks
# =============================================================================

@app.before_request
def before_request():
    """Execute before each request. Good for auth, timing, etc."""
    g.start_time = time.time()


@app.after_request
def after_request(response):
    """Execute after each request. Good for logging, headers."""
    if hasattr(g, "start_time"):
        elapsed = time.time() - g.start_time
        response.headers["X-Response-Time"] = f"{elapsed:.4f}s"
    return response


# =============================================================================
# 6. Error Handlers
# =============================================================================

@app.errorhandler(404)
def not_found(error):
    """Custom 404 error handler."""
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def server_error(error):
    """Custom 500 error handler."""
    return jsonify({"error": "Internal server error"}), 500


# =============================================================================
# 7. Blueprints - Modular Routes
# =============================================================================

from flask import Blueprint

api_bp = Blueprint("api", __name__, url_prefix="/api/v2")

@api_bp.route("/status")
def api_status():
    """Blueprint route example."""
    return jsonify({"status": "ok", "version": "2.0"})

app.register_blueprint(api_bp)


# =============================================================================
# 8. Demonstration of Synchronous Nature
# =============================================================================

@app.route("/slow")
def slow_endpoint():
    """
    Demonstrates Flask's synchronous nature.
    This blocks the worker thread for 2 seconds.
    In production, use async frameworks or Celery for long tasks.
    """
    time.sleep(2)
    return jsonify({"message": "Slow response after 2 seconds"})


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    print("""
Flask Tutorial Server
=====================
Endpoints:
  GET  /              - Index page
  GET  /api/hello     - Hello JSON
  GET  /user/<name>   - User info
  GET  /post/<id>     - Post info
  GET  /search?q=...  - Search with query params
  GET  /api/items     - List items
  POST /api/items     - Create item
  GET  /api/v2/status - Blueprint example
  GET  /slow          - Slow endpoint (2s)
    """)
    app.run(debug=True, port=5000)
