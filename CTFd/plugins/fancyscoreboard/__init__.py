from .routes import routes

def load(app):
  print("Hello! Loaded from fancyscoreboard")

  app.register_blueprint(routes, url_prefix='/fancyscoreboard')
