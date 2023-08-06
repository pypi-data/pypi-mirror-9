# -*- coding: utf-8 -*-
# Copyright (C)2015 DKRZ GmbH

"""Recipe mongodb"""

import os
from mako.template import Template

import zc.buildout
from birdhousebuilder.recipe import conda, supervisor

templ_config = Template(filename=os.path.join(os.path.dirname(__file__), "mongodb.conf"))

class Recipe(object):
    """This recipe is used by zc.buildout.
    It installs mongodb as conda package and inits mongodb database."""

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        b_options = buildout['buildout']
        self.prefix = self.options.get('prefix', conda.prefix())
        self.options['prefix'] = self.prefix
        
        self.conda_channels = b_options.get('conda-channels')

    def install(self):
        installed = []
        installed += list(self.install_mongodb())
        installed += list(self.install_config())
        installed += list(self.install_program())
        return installed

    def install_mongodb(self):
        script = conda.Recipe(
            self.buildout,
            self.name,
            {'pkgs': 'mongodb'})

        conda.makedirs( os.path.join(self.prefix, 'etc') )
        conda.makedirs( os.path.join(self.prefix, 'var', 'lib', 'mongodb') )
        conda.makedirs( os.path.join(self.prefix, 'var', 'log', 'mongodb') )
        
        return script.install()
        
    def install_config(self):
        """
        install mongodb config file
        """
        result = templ_config.render(
            prefix=self.prefix,
            )

        output = os.path.join(self.prefix, 'etc', 'mongodb.conf')
        conda.makedirs(os.path.dirname(output))
        
        try:
            os.remove(output)
        except OSError:
            pass

        with open(output, 'wt') as fp:
            fp.write(result)
        return [output]

    def install_program(self):
        script = supervisor.Recipe(
            self.buildout,
            self.name,
            {'program': 'mongodb',
             'command': '%s/bin/mongod --config %s/etc/mongodb.conf' % (self.prefix, self.prefix),
             'priority': '10',
         'autostart': 'true',
         'autorestart': 'false',
             })
        return script.install()

    def update(self):
        return self.install()

def uninstall(name, options):
    pass

