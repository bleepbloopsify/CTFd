from flask import current_app as app, render_template


# 404
def page_not_found(error):
    return render_template('errors/404.html', error=error.description), 404


# 403
def forbidden(error):
    return render_template('errors/403.html', error=error.description), 403


# 500
def general_error(error):
    if getattr(error, 'description') is not None:
      return render_template('errors/500.html', error=error.description), 500
    else:
      return render_template('errors/500.html', error=error), 500


# 502
def gateway_error(error):
    return render_template('errors/502.html', error=error.description), 502
