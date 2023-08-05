# coding=utf-8
# Copyright 2013 Janusz Skonieczny
import logging
from flask import Blueprint, url_for, request, current_app
from flask_login import login_user, current_user
from flask_security.utils import do_flash
from flask_babel import gettext as _

from werkzeug.exceptions import abort
from werkzeug.local import LocalProxy
from werkzeug.utils import redirect

logger = logging.getLogger("flask_social_blueprint")


class SocialBlueprint(Blueprint):
    def __init__(self, name, import_name, connection_adapter=None, providers=None, *args, **kwargs):
        super(SocialBlueprint, self).__init__(name, import_name, *args, **kwargs)
        self.connection_adapter = connection_adapter
        self.providers = providers or {}

    def get_provider(self, provider_name):
        provider = self.providers[provider_name]
        if not provider:
            abort(404)
        return provider

    def authenticate(self, provider):
        """
        Starts OAuth authorization flow, will redirect to 3rd party site.
        """
        callback_url = url_for(".callback", provider=provider, _external=True)
        provider = self.get_provider(provider)
        return provider.authorize(callback_url)

    def callback(self, provider):
        """
        Handles 3rd party callback and processes it's data
        """
        provider = self.get_provider(provider)
        return provider.authorized_handler(self.login)(provider=provider)

    def login(self, raw_data, provider):
        logger.debug("raw_data: %s" % raw_data)
        if not raw_data:
            do_flash(_("OAuth authorization failed"), "danger")
            abort(400)
        profile = provider.get_profile(raw_data)
        connection = self.connection_adapter.by_profile(profile)
        if not connection:
            return self.no_connection(profile, provider)
        return self.login_connection(connection, profile, provider)

    def no_connection(self, profile, provider):
        try:
            connection = self.create_connection(profile, provider)
        except Exception as ex:
            logging.warn(ex, exc_info=True)
            do_flash(_("Could not register: {}").format(ex.message), "warning")
            return self.login_failed_redirect(profile, provider)

        return self.login_connection(connection, profile, provider)

    def login_connection(self, connection, profile, provider):
        user = connection.get_user()
        assert user, "Connection did not returned a User instance"
        login_user(user)
        return self.login_redirect(profile, provider)

    def login_redirect(self, profile, provider):
        return redirect("/")

    def login_failed_redirect(self, profile, provider):
        return redirect("/")

    def create_connection(self, profile, provider):
        return self.connection_adapter.from_profile(current_user, profile)

    @classmethod
    def create_bp(cls, name, connection_adapter, providers, *args, **kwargs):
        bp = SocialBlueprint(name, __name__, connection_adapter, providers, *args, **kwargs)
        bp.route('/login/<provider>', endpoint="login")(bp.authenticate)
        bp.route('/callback/<provider>', endpoint="callback")(bp.callback)
        return bp

    @classmethod
    def setup_providers(cls, config):
        providers = {}
        for provider, provider_config in config.items():
            module_path, class_name = provider.rsplit('.', 1)
            from importlib import import_module
            module = import_module(module_path)
            provider = getattr(module, class_name)(**provider_config)
            providers[provider.name] = provider
        return providers

    @classmethod
    def init_bp(cls, app, connection_adapter, *args, **kwargs):
        config = app.config.get("SOCIAL_BLUEPRINT")
        providers = cls.setup_providers(config)
        bp = cls.create_bp('social', connection_adapter, providers, *args, **kwargs)
        app.register_blueprint(bp)


bp = LocalProxy(lambda: current_app.blueprints[request.blueprint])

