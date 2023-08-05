__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = 'Copyright (c) 2013-2015 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = (
    'BaseURLBootstrapThreeBootstrap3FluidMainWidget',
    'BaseBookmarkBootstrapThreeWidget'
)

from dash.contrib.plugins.url.dash_widgets import (
    BaseURLWidget, BaseBookmarkWidget
    )

# *************************************************************
# ******************* URL widgets *****************************
# *************************************************************

class BaseURLBootstrapThreeBootstrap3FluidMainWidget(BaseURLWidget):
    """
    Base URL plugin widget for Bootstrap 3 Fluid layout (placeholder `main`).
    """
    #layout_uid = 'bootstrap3_fluid'
    #placeholder_uid = 'main'
    #plugin_uid = 'url_bootstrap_three'
    media_css = (
        'bootstrap3/css/dash_plugin_url_bootstrap3.css',
    )

# *********************************************************
# *********************************************************
# *********************** Bookmark widgets ****************
# *********************************************************
# *********************************************************

class BaseBookmarkBootstrapThreeWidget(BaseBookmarkWidget):
    """
    Base Bookmark plugin widget for Bootstrap 3 Fluid layout.
    """
    media_css = (
        'bootstrap3/css/dash_plugin_bookmark_bootstrap3.css',
    )
