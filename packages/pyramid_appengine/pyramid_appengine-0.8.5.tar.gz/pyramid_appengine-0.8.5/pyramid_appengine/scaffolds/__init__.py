"""
scaffold
"""
from pyramid.scaffolds.template import Template
import os


class PyramidAppEngineStarterTemplate(Template):
    _template_dir = "starter"
    summary = "Pyramid scaffold for appengine"

    # taken from pyramid/scaffolds.PyramidTemplate
    def pre(self, command, output_dir, vars):
        vars['random_string'] = os.urandom(20).encode('hex')
        package_logger = vars['package']
        if package_logger == 'root':
            # Rename the app logger in the rare case a project is named 'root'
            package_logger = 'app'
        vars['package_logger'] = package_logger
        return Template.pre(self, command, output_dir, vars)

    def post(self, command, output_dir, vars):
        self.out('Welcome to pyramid_appengine.  Go HACK!!!')
        return Template.post(self, command, output_dir, vars)

    def out(self, msg): # pragma: no cover (replaceable testing hook)
        print msg
