from flask import render_template, Blueprint, redirect, url_for, request

from CTFd.utils import config
from CTFd.utils import get_config
from CTFd.utils.modes import get_model
from CTFd.utils.user import get_current_team
from CTFd.utils.decorators import authed_only, require_team
from CTFd.utils.decorators.visibility import check_score_visibility

from CTFd.utils.scores import get_standings

scoreboard = Blueprint('scoreboard', __name__)


@scoreboard.route('/scoreboard')
@check_score_visibility # remember to set this to true
@authed_only
@require_team
def listing():
    team = get_current_team()

    regions = ['', 'CSAW US-Canada', 'CSAW Europe', 'CSAW Israel', 'CSAW India', 'CSAW MENA', 'CSAW Mexico']
    region = team.region # if this is admin we show everything and the filter

    if region == '--':
        return render_template(
            'scoreboard.html',
            errors=['Scores are only visible to qualifying teams']
        )

    if config.hide_scores():
        return render_template(
            'scoreboard.html',
            errors=['Scores are currently hidden']
        )

    filters = []
    Model = get_model()
    if region and region != 'root' and region != '--':
        filters.append(Model.region == region)

    standings = get_standings(filters=filters)
    if region and region != 'root' and region != '--':
        standings = filter(lambda s: s[4] == region, standings)

    return render_template(
        'scoreboard.html',
        standings=standings,
        regions=regions,
        region=region, # if this is admin we show everything and the filter
        score_frozen=config.is_scoreboard_frozen()
    )
