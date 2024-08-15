from equigence import app
from flask import render_template


@app.errorhandler(404)
def page_not_found(error):
    """404 page route."""
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    """500 page route."""
    return render_template('errors/500.html'), 500

@app.errorhandler(403)
def forbidden(error):
    """403 page route."""
    return render_template('errors/403.html'), 403
