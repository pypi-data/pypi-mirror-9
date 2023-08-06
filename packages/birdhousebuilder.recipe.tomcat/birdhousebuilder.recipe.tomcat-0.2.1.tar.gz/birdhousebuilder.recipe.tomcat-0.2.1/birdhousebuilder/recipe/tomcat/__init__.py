# -*- coding: utf-8 -*-
# Copyright (C)2015 DKRZ GmbH

"""Recipe tomcat"""

import os
from mako.template import Template

import zc.buildout
from birdhousebuilder.recipe import conda, supervisor

users_config = Template(filename=os.path.join(os.path.dirname(__file__), "tomcat-users.xml"))

class Recipe(object):
    """This recipe is used by zc.buildout.
    It installs apache-tomcat as conda package and setups tomcat configuration"""

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        b_options = buildout['buildout']
        self.prefix = self.options.get('prefix', conda.prefix())
        self.options['prefix'] = self.prefix

    def install(self):
        installed = []
        installed += list(self.install_tomcat())
        installed += list(self.setup_config())
        installed += list(self.setup_service())
        return tuple()

    def install_tomcat(self):
        script = conda.Recipe(
            self.buildout,
            self.name,
            {'pkgs': 'apache-tomcat'})

        return script.install()

    def setup_config(self):
        result = users_config.render(**self.options)

        output = os.path.join(self.prefix, 'opt', 'apache-tomcat', 'conf', 'tomcat-users.xml')
        conda.makedirs(os.path.dirname(output))

        try:
            os.remove(output)
        except OSError:
            pass

        with open(output, 'wt') as fp:
            fp.write(result)
        return [output]
    
    def setup_service(self):
        script = supervisor.Recipe(
            self.buildout,
            self.name,
            {'program': 'tomcat',
             'command': '%s/bin/catalina.sh run' % (self.prefix),
             })
        return script.install()

    def update(self):
        #self.install_tomcat()
        self.setup_config()
        self.setup_service()
        return tuple()

def uninstall(name, options):
    pass

