import os 
from yafowil.base import factory


resourcedir = os.path.join(os.path.dirname(__file__), 'resources')
js = [{
    'group': 'yafowil.widget.datetime.datepicker',
    'resource': 'jquery.ui.datepicker.min.js',
    'order': 20,
}, {
    'group': 'yafowil.widget.datetime.timepicker',
    'resource': 'jquery.ui.timepicker.js',
    'order': 20,
}, {
    'group': 'yafowil.widget.datetime.common',
    'resource': 'widget.js',
    'order': 21,
}]
default_css = [{
    'group': 'yafowil.widget.datetime.datepicker',
    'resource': 'jquery.ui.datepicker.css',
    'order': 20,
}, {
    'group': 'yafowil.widget.datetime.timepicker',
    'resource': 'jquery.ui.timepicker.css',
    'order': 20,
}, {
    'group': 'yafowil.widget.datetime.common',
    'resource': 'widget.css',
    'order': 21,
}]
bootstrap_css = [{
    'group': 'yafowil.widget.datetime.datepicker',
    'resource': 'jquery.ui.datepicker.bootstrap.css',
    'order': 20,
}, {
    'group': 'yafowil.widget.datetime.timepicker',
    'resource': 'jquery.ui.timepicker.bootstrap.css',
    'order': 20,
}, {
    'group': 'yafowil.widget.datetime.common',
    'resource': 'widget-bootstrap.css',
    'order': 21,
}]


def register():
    import widget
    factory.register_theme('default', 'yafowil.widget.datetime',
                           resourcedir, js=js, css=default_css)
    factory.register_theme('bootstrap', 'yafowil.widget.datetime',
                           resourcedir, js=js, css=bootstrap_css)