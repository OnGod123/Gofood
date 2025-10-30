"""
home.py
--------

This module defines the HTTP route handler for the application's root URL (`/`).
It is implemented using Flask's `Blueprint` mechanism for modular route organization.

The handler replicates the behavior of a production landing endpoint
(similar to `https://www.heyfood.africa/`), handling GET requests and returning
a rendered HTML page (`home.html`).  

It also includes granular try/except blocks to isolate and log potential errors
during request processing, improving debuggability.

Each major section of the request lifecycle (headers, cookies, referrer,
template rendering) is independently protected by error handling, ensuring
that one failure does not compromise the entire request pipeline.

Modules imported:
-----------------
- `traceback`: Provides formatted stack traces for detailed error output.
- `flask.Blueprint`: Used to modularize routes and avoid circular imports.
- `flask.request`: Gives access to incoming HTTP request data (headers, cookies, etc.).
- `flask.render_template`: Renders Jinja2 HTML templates located under `templates/`.
- `flask.make_response`: Builds custom HTTP responses with modified headers.
- `flask.jsonify`: Returns JSON-encoded responses for error/debug feedback.

Blueprint:
----------
home_bp : Blueprint
    The Flask blueprint that groups all routes related to the home page.

Functions:
----------
home() -> Response
    Handles GET requests to the root URL ('/').
    Captures client metadata (method, headers, cookies, referrer),
    safely renders the home template, and attaches additional headers.

    Returns:
        - HTML page (200 OK) when successful.
        - JSON-formatted error (500 Internal Server Error) when any step fails.

Error handling strategy:
------------------------
Each step of the handler (e.g., header parsing, cookie extraction, template rendering)
is wrapped in its own try/except block.  
Any exception is captured into a shared `debug_data` dictionary that records both
the failure point and partial context.  
If an unrecoverable error occurs, a structured JSON response containing this
debug information and a stack trace is returned.
"""

import traceback
from flask import Blueprint, request, render_template, make_response, jsonify

# ------------------------------------------------------------------------------
# Blueprint definition
# ------------------------------------------------------------------------------
home_bp = Blueprint('home', __name__)

# ------------------------------------------------------------------------------
# Route definition: /
# ------------------------------------------------------------------------------
@home_bp.route('/', methods=['GET'])
def home():
    """
    Home page route handler for HeyFood-style landing.

    This endpoint handles GET requests to the root path (`/`).
    It performs multiple diagnostic and request-parsing steps to
    collect metadata from the client request, such as headers,
    cookies, and referrer information.

    The function safely renders an HTML template (`home.html`) while
    setting custom response headers for debugging and cache control.

    Each section of logic is independently wrapped in try/except blocks,
    allowing the application to report fine-grained errors if anything fails.

    Returns
    -------
    flask.Response
        - On success: a rendered HTML response (status code 200)
        - On failure: a JSON object containing the error message,
          captured debug information, and a traceback (status code 500)
    """
    debug_data = {}  # Dictionary to collect debug info for every phase

    try:
        # ----------------------------------------------------------------------
        # 1️⃣ Capture core request information
        # ----------------------------------------------------------------------
        try:
            debug_data['method'] = request.method                # HTTP method (GET, POST, etc.)
            debug_data['url'] = request.url                      # Full request URL
            debug_data['remote_addr'] = request.remote_addr      # Client IP address
        except Exception as e:
            debug_data['method_error'] = f"Error parsing basic request info: {e}"

        # ----------------------------------------------------------------------
        # 2️⃣ Parse headers safely
        # ----------------------------------------------------------------------
        try:
            debug_data['headers'] = dict(request.headers)        # All request headers
            user_agent = request.headers.get('User-Agent', 'Unknown')  # Browser identification
            accept_lang = request.headers.get('Accept-Language', 'N/A')  # Client language preference
        except Exception as e:
            debug_data['header_error'] = f"Error reading headers: {e}"

        # ----------------------------------------------------------------------
        # 3️⃣ Parse cookies safely
        # ----------------------------------------------------------------------
        try:
            debug_data['cookies'] = request.cookies              # Client cookies as dict
        except Exception as e:
            debug_data['cookie_error'] = f"Error parsing cookies: {e}"

        # ----------------------------------------------------------------------
        # 4️⃣ Get referrer (previous page URL)
        # ----------------------------------------------------------------------
        try:
            referer = request.referrer                           # Source page (if user came from another URL)
            debug_data['referer'] = referer
        except Exception as e:
            debug_data['referer_error'] = f"Error getting referrer: {e}"

        # ----------------------------------------------------------------------
        # 5️⃣ Render template and build HTTP response
        # ----------------------------------------------------------------------
        try:
            # Render the home page with template variables
            response = make_response(
                render_template(
                    'home.html',
                    user_agent=user_agent,
                    accept_lang=accept_lang,
                    referer=referer
                )
            )

            # Add cache and debug headers
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
            response.headers['X-Debug'] = 'True'

            return response

        except Exception as e:
            debug_data['template_error'] = f"Error rendering template: {e}"
            raise e

    # --------------------------------------------------------------------------
    # Final exception catcher
    # --------------------------------------------------------------------------
    except Exception as final_error:
        debug_data['traceback'] = traceback.format_exc()
        return jsonify({
            'status': 'error',
            'error': str(final_error),
            'debug': debug_data
        }), 500

