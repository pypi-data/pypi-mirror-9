# -*- coding: utf-8 -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2015 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU Affero General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option)
#  any later version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for
#  more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Application Entry Point
"""

from __future__ import unicode_literals

import os
import logging

import edbob
from edbob.pyramid.forms.formalchemy import TemplateEngine

import rattail.db
from rattail.config import RattailConfig
from rattail.exceptions import ConfigurationError
from rattail.db.util import get_engines
from rattail.db.continuum import configure_versioning
from rattail.db.types import GPCType

import formalchemy
from pyramid.config import Configurator
from pyramid.authentication import SessionAuthenticationPolicy

import tailbone.db
from tailbone.auth import TailboneAuthorizationPolicy
from tailbone.forms import GPCFieldRenderer


log = logging.getLogger(__name__)


def make_rattail_config(settings):
    """
    Make a Rattail config object from the given settings.
    """
    # Initialize rattail config and embed it in the settings dict, to make it
    # available to web requests later.
    path = settings.get('edbob.config')
    if not path or not os.path.exists(path):
        raise ConfigurationError("Please set 'edbob.config' in [app:main] section of config "
                                 "to the path of your config file.  Lame, but necessary.")
    edbob.init('rattail', path)
    log.info("using rattail config file: {0}".format(path))
    rattail_config = RattailConfig(edbob.config)
    settings['rattail_config'] = rattail_config

    # Load all Rattail database engines from config, and store in settings
    # dict.  This is necessary e.g. in the case of a host server, to have
    # access to its subordinate store servers.
    rattail_engines = get_engines(rattail_config)
    settings['rattail_engines'] = rattail_engines

    # Configure the database session classes.  Note that most of the time we'll
    # be using the Tailbone Session, but occasionally (e.g. within batch
    # processing threads) we want the Rattail Session.  The reason is that
    # during normal request processing, the Tailbone Session is preferable as
    # it includes Zope Transaction magic.  Within an explicitly-spawned thread
    # however, this is *not* desirable.
    rattail.db.Session.configure(bind=rattail_engines['default'])
    tailbone.db.Session.configure(bind=rattail_engines['default'])

    # Configure (or not) Continuum versioning.
    configure_versioning(rattail_config)

    return rattail_config


def provide_postgresql_settings(settings):
    """
    Add some PostgreSQL-specific settings to the app config.  Specifically,
    this enables retrying transactions a second time, in an attempt to
    gracefully handle database restarts.
    """
    settings.setdefault('tm.attempts', 2)


def make_pyramid_config(settings):
    """
    Make a Pyramid config object from the given settings.
    """
    config = Configurator(settings=settings)

    # Configure user authentication / authorization.
    config.set_authentication_policy(SessionAuthenticationPolicy())
    config.set_authorization_policy(TailboneAuthorizationPolicy())

    # Bring in some Pyramid goodies.
    config.include('pyramid_beaker')
    config.include('pyramid_mako')
    config.include('pyramid_tm')

    # Configure FormAlchemy.
    formalchemy.config.engine = TemplateEngine()
    formalchemy.FieldSet.default_renderers[GPCType] = GPCFieldRenderer

    return config


def configure_postgresql(pyramid_config):
    """
    Add some PostgreSQL-specific tweaks to the final app config.  Specifically,
    adds the tween necessary for graceful handling of database restarts.
    """
    pyramid_config.add_tween('edbob.pyramid.tweens.sqlerror_tween_factory',
                             under='pyramid_tm.tm_tween_factory')


def main(global_config, **settings):
    """
    This function returns a Pyramid WSGI application.
    """
    rattail_config = make_rattail_config(settings)
    pyramid_config = make_pyramid_config(settings)
    return pyramid_config.make_wsgi_app()
