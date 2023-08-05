__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = 'Copyright (c) 2013 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = ('Bootstrap3FluidLayout',)

from dash.base import (
    BaseDashboardLayout, BaseDashboardPlaceholder, layout_registry
    )

# *******************************************************************
# ******************** Bootstrap 3 Fluid layout *********************
# *******************************************************************

class Bootstrap3FluidMainPlaceholder(BaseDashboardPlaceholder):
    """
    Main placeholder.
    """
    uid = 'main'
    cols = 11
    rows = 9
    cell_width = 70
    cell_height = 40
    cell_margin_top = 8
    cell_margin_right = 8
    cell_margin_bottom = 8
    cell_margin_left = 8
    edit_template_name = 'bootstrap3/fluid_base_placeholder_edit.html'


class Bootstrap3FluidLayout(BaseDashboardLayout):
    """
    Bootstrap 3 Fluid layout.
    """
    uid = 'bootstrap3_fluid'
    name = 'Bootstrap 3 Fluid'
    view_template_name = 'bootstrap3/fluid_view_layout.html'
    edit_template_name = 'bootstrap3/fluid_edit_layout.html'
    plugin_widgets_template_name_ajax = 'bootstrap3/plugin_widgets_ajax.html'
    form_snippet_template_name = 'bootstrap3/snippets/generic_form_snippet.html'
    placeholders = [Bootstrap3FluidMainPlaceholder,]
    cell_units = 'px'
    media_css = (
        'bootstrap3/css/bootstrap.css',
        'bootstrap3/css/dash_layout_bootstap3_fluid.css',
        #'css/dash_solid_borders.css',
    )
    media_js = (
        'bootstrap3/js/bootstrap.js',
        'bootstrap3/js/dash_layout_bootstap3_fluid.js',
    )

    def get_view_template_name(self, request=None, origin=None):
        """
        Override the master view template for public dashboard app.
        """
        if 'dash.public_dashboard' == origin:
            return 'bootstrap3/fuild_public_dashboard_view_layout.html'
        else:
            return super(Bootstrap3FluidLayout, self).get_view_template_name(
                request = request,
                origin = origin
                )


layout_registry.register(Bootstrap3FluidLayout)
