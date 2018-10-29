from flask import request, render_template, session, Blueprint

from CTFd.models import Users, Solves, Awards
from CTFd.utils import get_config
from CTFd.utils.decorators import authed_only
from CTFd.utils import config
from CTFd.utils.dates import unix_time_to_utc
from CTFd.utils.decorators.visibility import check_account_visibility, check_score_visibility

users = Blueprint('users', __name__)


@users.route('/users')
@check_account_visibility
def listing():
    # TODO: Implement this logic to either mimic the teams page or to only be visible when the ctf is in user only mode
    page = request.args.get('page', 1)
    page = abs(int(page))
    results_per_page = 50
    page_start = results_per_page * (page - 1)
    page_end = results_per_page * (page - 1) + results_per_page

    count = Users.query.filter_by(banned=False, hidden=False).count()
    users = Users.query.filter_by(banned=False, hidden=False).slice(page_start, page_end).all()

    pages = int(count / results_per_page) + (count % results_per_page > 0)
    return render_template(
        'users/users.html',
        users=users,
        pages=pages,
        curr_page=page
    )


@users.route('/profile')
@users.route('/user')
@authed_only
def private():
    user_id = session['id']

    freeze = get_config('freeze')
    user = Users.query.filter_by(id=user_id).first_or_404()
    solves = Solves.query.filter_by(user_id=user_id)
    awards = Awards.query.filter_by(user_id=user_id)

    place = user.place
    score = user.score

    if freeze:
        freeze = unix_time_to_utc(freeze)
        if user_id != session.get('id'):
            solves = solves.filter(Solves.date < freeze)
            awards = awards.filter(Awards.date < freeze)

    solves = solves.all()
    awards = awards.all()

    return render_template(
        'users/user.html',
        solves=solves,
        awards=awards,
        user=user,
        score=score,
        place=place,
        score_frozen=config.is_scoreboard_frozen()
    )


@users.route('/users/<int:user_id>')
@check_account_visibility
@check_score_visibility
def public(user_id):
    # TODO: This should be visible if user's login as themselves (user+team login, or user only login)
    user = Users.query.filter_by(id=user_id).first_or_404()
    return render_template('users/user.html', user=user)
