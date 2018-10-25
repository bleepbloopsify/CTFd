from flask import request
from flask_restplus import Namespace, Resource
from CTFd.models import db, Configs
from CTFd.schemas.config import ConfigSchema
from CTFd.utils.decorators import (
    admins_only
)
from CTFd.utils import get_config, set_config

configs_namespace = Namespace('configs', description="Endpoint to retrieve Configs")


@configs_namespace.route('')
class ConfigList(Resource):
    @admins_only
    def get(self):
        configs = Configs.query.all()
        schema = ConfigSchema(many=True)
        response = schema.dump(configs)
        if response.errors:
            return {
                'success': False,
                'errors': response.errors,
            }, 400

        return {
            'success': True,
            'data': response.data
        }

    @admins_only
    def post(self):
        req = request.get_json()
        schema = ConfigSchema()
        response = schema.load(req)

        if response.errors:
            return {
                'success': False,
                'errors': response.errors
            }, 400

        db.session.add(response.data)
        db.session.commit()
        db.session.close()

        return {
            'success': True,
            'data': response.data
        }

    @admins_only
    def patch(self):
        req = request.get_json()

        for key, value in req.items():
            set_config(key=key, value=value)

        return {
            'success': True
        }


@configs_namespace.route('/<config_key>')
class Config(Resource):
    @admins_only
    def get(self, config_key):

        return {
            'success': True,
            'data': get_config(config_key)
        }

    @admins_only
    def patch(self, config_key):
        config = Configs.query.filter_by(key=config_key).first_or_404()
        data = request.get_json()
        response = ConfigSchema(instance=config, partial=True).load(data)

        if response.errors:
            return response.errors, 400

        db.session.commit()
        # response = ConfigSchema().dump(response.data)
        db.session.close()

        return {
            'success': True,
            'data': response.data
        }

    @admins_only
    def delete(self, config_key):
        config = Configs.query.filter_by(key=config_key).first_or_404()

        db.session.delete(config)
        db.session.commit()
        db.session.close()

        return {
            'success': True,
        }
