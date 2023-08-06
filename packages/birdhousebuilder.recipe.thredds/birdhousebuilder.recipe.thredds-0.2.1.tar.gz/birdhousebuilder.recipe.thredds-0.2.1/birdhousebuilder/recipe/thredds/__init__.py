# -*- coding: utf-8 -*-
# Copyright (C)2015 DKRZ GmbH

"""Recipe thredds"""

import os
from mako.template import Template

import zc.buildout
from birdhousebuilder.recipe import conda, tomcat

web_config = Template(filename=os.path.join(os.path.dirname(__file__), "web.xml"))
wms_config = Template(filename=os.path.join(os.path.dirname(__file__), "wmsConfig.xml"))
thredds_config = Template(filename=os.path.join(os.path.dirname(__file__), "threddsConfig.xml"))
catalog_config = Template(filename=os.path.join(os.path.dirname(__file__), "catalog.xml"))

class Recipe(object):
    """This recipe is used by zc.buildout.
    It installs thredds with conda and setups thredds configuration."""

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        b_options = buildout['buildout']
        self.prefix = self.options.get('prefix', conda.prefix())
        self.options['prefix'] = self.prefix
        self.options['data_root'] = options.get(
            'data_root', os.path.join(self.prefix, 'var', 'lib', 'pywps', 'outputs'))

    def install(self):
        installed = []
        installed += list(self.install_thredds())
        installed += list(self.install_thredds_config())
        installed += list(self.install_catalog_config())
        installed += list(self.install_wms_config())
        installed += list(self.install_web_config())
        return tuple()

    def install_thredds(self):
        script = conda.Recipe(
            self.buildout,
            self.name,
            {'pkgs': 'thredds'})

        return script.install()

    def install_thredds_config(self):
        result = thredds_config.render(**self.options)

        output = os.path.join(self.prefix, 'opt', 'apache-tomcat', 'content', 'thredds', 'threddsConfig.xml')
        conda.makedirs(os.path.dirname(output))

        try:
            os.remove(output)
        except OSError:
            pass

        with open(output, 'wt') as fp:
            fp.write(result)
        return [output]

    def install_catalog_config(self):
        result = catalog_config.render(**self.options)

        output = os.path.join(self.prefix, 'opt', 'apache-tomcat', 'content', 'thredds', 'catalog.xml')
        conda.makedirs(os.path.dirname(output))

        try:
            os.remove(output)
        except OSError:
            pass

        with open(output, 'wt') as fp:
            fp.write(result)
        return [output]

    def install_wms_config(self):
        result = wms_config.render(**self.options)

        output = os.path.join(self.prefix, 'opt', 'apache-tomcat', 'content', 'thredds', 'wmsConfig.xml')
        conda.makedirs(os.path.dirname(output))

        try:
            os.remove(output)
        except OSError:
            pass

        with open(output, 'wt') as fp:
            fp.write(result)
        return [output]

    def install_web_config(self):
        result = web_config.render(**self.options)

        output = os.path.join(self.prefix, 'opt', 'apache-tomcat', 'conf', 'web.xml')
        conda.makedirs(os.path.dirname(output))

        try:
            os.remove(output)
        except OSError:
            pass

        with open(output, 'wt') as fp:
            fp.write(result)
        return [output]


    def update(self):
        #self.install_thredds()
        self.install_thredds_config()
        self.install_catalog_config()
        self.install_wms_config()
        self.install_web_config()
        return tuple()

def uninstall(name, options):
    pass

