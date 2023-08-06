from __future__ import print_function
"""
Powa main application.
"""
import os

__VERSION__ = '2.0.1'
__VERSION_NUM__ = [int(part) for part in __VERSION__.split('.')]
POWA_ROOT = os.path.dirname(__file__)

from tornado.web import Application, URLSpec as U
from powa.options import parse_options
from tornado.options import options
from powa import ui_modules, ui_methods
from powa.framework import AuthHandler
from powa.user import LoginHandler, LogoutHandler
from powa.overview import Overview
from powa.database import DatabaseSelector, DatabaseOverview
from powa.query import QueryOverview
from powa.qual import QualOverview
from powa.config import ConfigOverview


class IndexHandler(AuthHandler):
    """
    Handler for the main page.
    """

    def get(self):
        return self.redirect("/overview/")


URLS = [
    U(r"/login/", LoginHandler, name="login"),
    U(r"/logout/", LogoutHandler, name="logout"),
    U(r"/database/select", DatabaseSelector, name="database_selector"),
    U(r"/", IndexHandler, name="index")
]


for dashboard in (Overview,
                  DatabaseOverview,
                  QueryOverview,
                  QualOverview,
                  ConfigOverview):
    URLS.extend(dashboard.url_specs())


def make_app(**kwargs):
    """
    Parse the config file and instantiate a tornado app.
    """
    parse_options()

    return Application(
        URLS,
        ui_modules=ui_modules,
        ui_methods=ui_methods,
        login_url="/login/",
        static_path=os.path.join(POWA_ROOT, "static"),
        cookie_secret=options.cookie_secret,
        template_path=os.path.join(POWA_ROOT,  "templates"),
        **kwargs)
