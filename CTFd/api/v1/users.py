from flask import session, request
from flask_restplus import Namespace, Resource
from CTFd.models import db, Users, Solves, Awards, Fails, Tracking, Unlocks
from CTFd.utils.decorators import (
    authed_only,
    admins_only
)
from CTFd.utils.dates import unix_time_to_utc, unix_time
from CTFd.utils.user import get_current_user, is_admin
from CTFd.utils import get_config

from CTFd.schemas.submissions import SubmissionSchema
from CTFd.schemas.awards import AwardSchema
from CTFd.schemas.users import UserSchema


users_namespace = Namespace('users', description="Endpoint to retrieve Users")


@users_namespace.route('')
class UserList(Resource):
    def get(self):
        users = Users.query.filter_by(banned=False)
        response = UserSchema(view='user', many=True).dump(users)

        if response.errors:
            return {
                'success': False,
                'errors': response.errors
            }, 400

        return {
            'success': True,
            'data': response.data
        }


@users_namespace.route('/<user_id>')
@users_namespace.param('user_id', "User ID")
class User(Resource):
    def get(self, user_id):
        user = Users.query.filter_by(id=user_id).first_or_404()

        response = UserSchema('self').dump(user)

        if response.errors:
            return {
                'success': False,
                'errors': response.errors
            }, 400

        response.data['place'] = user.place
        response.data['score'] = user.score

        return {
            'success': True,
            'data': response.data
        }

    @admins_only
    def patch(self, user_id):
        user = Users.query.filter_by(id=user_id).first_or_404()
        data = request.get_json()
        response = UserSchema(view='admin', instance=user, partial=True).load(data)
        if response.errors:
            return {
                'success': False,
                'errors': response.errors
            }, 400

        db.session.commit()
        # response = UserSchema('admin').dump(response.data)
        db.session.close()

        return {
            'success': True,
            'data': response
        }

    @admins_only
    def delete(self, user_id):
        Unlocks.query.filter_by(user_id=user_id).delete()
        Awards.query.filter_by(user_id=user_id).delete()
        Fails.query.filter_by(user_id=user_id).delete()
        Solves.query.filter_by(user_id=user_id).delete()
        Tracking.query.filter_by(user_id=user_id).delete()
        Users.query.filter_by(user_id=user_id).delete()
        db.session.commit()
        db.session.close()

        return {
            'success': True
        }


@users_namespace.route('/me')
class User(Resource):
    def get(self):
        user = get_current_user()
        response = UserSchema('self').dump(user).data
        response['place'] = user.place
        response['score'] = user.score
        return {
            'success': True,
            'data': response
        }

    @authed_only
    def patch(self):
        user = get_current_user()
        data = request.get_json()
        response = UserSchema(view='self', instance=user, partial=True).load(data)
        if response.errors:
            return {
                'success': False,
                'errors': response.errors
            }, 400

        db.session.commit()
        # response = UserSchema('self').dump(response.data)
        db.session.close()
        return {
            'success': True,
            'data': response
        }

    @admins_only
    def delete(self):
        user_id = get_current_user().id
        Unlocks.query.filter_by(user_id=user_id).delete()
        Awards.query.filter_by(user_id=user_id).delete()
        Fails.query.filter_by(user_id=user_id).delete()
        Solves.query.filter_by(user_id=user_id).delete()
        Tracking.query.filter_by(user_id=user_id).delete()
        Users.query.filter_by(user_id=user_id).delete()
        db.session.commit()
        db.session.close()

        return {
            'success': True
        }


@users_namespace.route('/<user_id>/solves')
@users_namespace.param('user_id', "User ID or 'me'")
class UserSolves(Resource):
    def get(self, user_id):
        if user_id == 'me':
            user = get_current_user()
        else:
            user = Users.query.filter_by(id=user_id).first_or_404()

        solves = user.get_solves(
            admin=is_admin()
        )
        for solve in solves:
            setattr(solve, 'value', 100)

        view = 'user' if not is_admin() else 'admin'
        response = SubmissionSchema(view=view, many=True).dump(solves)

        if response.errors:
            return {
                'success': False,
                'errors': response.errors
            }, 400

        return {
            'success': True,
            'data': response.data
        }


@users_namespace.route('/<user_id>/fails')
@users_namespace.param('user_id', "User ID or 'me'")
class UserFails(Resource):
    def get(self, user_id):
        if user_id == 'me':
            user = get_current_user()
        else:
            user = Users.query.filter_by(id=user_id).first_or_404()

        fails = user.get_fails(
            admin=is_admin()
        )

        view = 'user' if not is_admin() else 'admin'
        response = SubmissionSchema(view=view, many=True).dump(fails)
        if response.errors:
            return {
                'success': False,
                'errors': response.errors
            }, 400

        return {
            'success': True,
            'data': response.data
        }


@users_namespace.route('/<user_id>/awards')
@users_namespace.param('user_id', "User ID or 'me'")
class UserAwards(Resource):
    def get(self, user_id):
        if user_id == 'me':
            user = get_current_user()
        else:
            user = Users.query.filter_by(id=user_id).first_or_404()

        awards = user.get_awards(
            admin=is_admin()
        )

        view = 'user' if not is_admin() else 'admin'
        response = AwardSchema(view=view, many=True).dump(awards)

        if response.errors:
            return {
                'success': False,
                'errors': response.errors
            }, 400

        return {
            'success': True,
            'data': response.data
        }
