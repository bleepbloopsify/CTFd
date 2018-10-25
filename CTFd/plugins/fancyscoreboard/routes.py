from flask import Blueprint, render_template

routes = Blueprint('fancyscoreboard', __name__)

@routes.route('')
def render_scoreboard():
  return render_template('fancy_scoreboard.html')

