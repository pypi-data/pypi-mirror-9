# -*- coding: utf8 -*-
from __future__ import print_function

import os
import sys
import json

import six
import click

default_siteconfig = {
    "version": 2,
    "siteModules": {}
}

template_js = """
define(["jquery", "underscore"], function($, _) {
    "use strict";
    alert("I am working!");
});
"""

template_modules = """
# -*- coding: utf-8 -*-
from __future__ import print_function

from web_framework import registry
from web_framework import site_config

site_config.add('siteconfig/modules/{name}-siteconfig.json')

MODULES = registry.Registry()

@MODULES("{name}")
def featured_jobs(module, front_type, front_name, **kwargs):
    print("WE MADE IT!")
"""

@click.command()
@click.option('--dir', default=os.getcwd(), prompt='Enter directory to create web-standard-app module',
              help='Directory where the web-standard-app module should be created')
@click.option('--name', prompt='Enter module name',
              help='The name of the web-standard-app module name')
@click.option('--js/--no-js', default=True,
              prompt='Do you want to add a basic javascript template?',
              help='These options will determine if a templated javascript file ought to be created')
@click.option('--css/--no-css', default=True,
              prompt='Do you want to add a basic css template?',
              help='These options will determine if a templated css file ought to be created')
@click.option('--config-version', default=2, prompt='Config version',
              help="This option sets the version for siteconfig.json")
@click.option('--template', default='primary', prompt='Template type', help='The type of template')
@click.option('--manifest/--no-manifest', default=False,
              prompt='Do you want to append the MANIFEST.in file?',
              help='This option appends a MANIFEST.in file with the assets for the module')
@click.option('--force', is_flag=True, default=False,
              help='This option will force the script to overwrite a currently existing module setup if the directory already exists')
def mkwsa(dir, name, js, css, config_version, template, manifest, force):
    """ Command line template for creating a basic web-standard-apps module """
    module_dir = os.path.join(dir, name)
    parent_dir = os.path.abspath(os.path.join(module_dir, os.pardir))

    static_dir = os.path.join(module_dir, "static")
    css_dir = os.path.join(static_dir, "css")
    css_modules = "modules"
    css_modules_dir = os.path.join(css_dir, "modules")
    js_dir = os.path.join(static_dir, "js")
    js_modules = "modules"
    js_modules_dir = os.path.join(js_dir, "modules")

    site_config_dir = os.path.join(js_dir, "siteconfig")
    site_config_module_dir = os.path.join(site_config_dir, "modules")
    site_config_file = os.path.join(site_config_module_dir, "{}-siteconfig.json".format(name))

    template_dir = os.path.join(module_dir, "templates")
    template_module_dir = os.path.join(template_dir, "modules")
    template_module_name_dir = os.path.join(template_module_dir, name)
    template_module_file = os.path.join(template_module_name_dir, "{}-{}".format(name, template))

    click.echo("Creating module named {} in {} ...".format(name, dir))

    if os.path.isdir(module_dir):
        if not force:
            click.echo("Directory already exists, use --force option to overwrite module setup settings")
            sys.exit()
    else:
        # create base module folder
        os.mkdir(module_dir)

    # setup python package
    click.echo("Creating __init__.py file ...")
    with open(os.path.join(module_dir, "__init__.py"), 'wb') as fp:
        output = "# -*- coding: utf-8 -*-"
        content = six.u(output)
        fp.write(content)

    click.echo("Creating modules.py file in {} ...".format(module_dir))
    data = six.u(template_modules.format(name=name))
    with open(os.path.join(module_dir, "modules.py"), 'wb') as fp_new:
        fp_new.write(data)

    # setup template folder structure and default template
    create_dir(template_dir)
    create_dir(template_module_dir)
    create_dir(template_module_name_dir)

    click.echo("Creating {}.html file in {} ...".format(template_module_file, template_module_name_dir))
    with open("{}.html".format(template_module_file), 'wb') as fp:
        output = '<div class="{}-container"></div>'.format(name)
        content = six.u(output)
        fp.write(content)

    # setup static folder structure and config files
    create_dir(static_dir)
    create_dir(css_dir)
    create_dir(js_dir)

    create_dir(site_config_dir)
    create_dir(site_config_module_dir)

    default_siteconfig['version'] = config_version
    default_siteconfig['siteModules'][name] = {}

    # create js modules directory and templated js file
    if js:
        create_dir(js_modules_dir)
        click.echo("Creating {}.js file in {} ...".format(name, js_modules_dir))
        data = six.u(template_js)
        with open(os.path.join(js_modules_dir, "{}.js".format(name)), 'wb') as fp_new:
            fp_new.write(data)
        default_siteconfig['siteModules'][name]['path'] = "{}/{}".format(js_modules, name)

    # create css modules directory and templated css file
    if css:
        create_dir(css_modules_dir)
        click.echo("Creating {}.css file in {} ...".format(name, css_modules_dir))
        with open(os.path.join(css_modules_dir, "{}.css".format(name)), 'wb') as fp:
            output = '.{}-container {}'.format(name, "{}")
            content = six.u(output)
            fp.write(content)
        default_siteconfig['siteModules'][name]['css'] = "{}/{}".format(css_modules, name)

    click.echo("Creating {}-siteconfig.json file in {} ..." \
               .format(name, site_config_module_dir))
    create_json(site_config_file, default_siteconfig)

    if manifest:
        append_manifest(parent_dir, module_dir, name)

    click.echo("---------------------------------\n")
    click.echo("Successfully installed {} module!".format(name))
    click.echo("Next steps:")
    click.echo("\t1.) Add {} to INSTALLED_APPS in uscp-web/uscp-web/settings/base.py".format(name))
    click.echo("\t2.) Create module in PRESTO")
    click.echo("\t3.) Add module to layout of choice")

def append_manifest(parent_dir, module_dir, name):
    manifest_file = os.path.join(parent_dir, "MANIFEST.in")
    templates = "\nrecursive-include {}/templates *\n".format(name)
    static = "recursive-include {}/static *".format(name)
    if os.path.isfile(manifest_file):
        with open(manifest_file, "a") as fp:
            fp.write(templates)
            fp.write(static)
        click.echo("Appended MANIFEST.in file in {}".format(parent_dir))
    else:
        click.echo("Could not find MANIFEST.in file ... ignoring")

def create_dir(directory):
    """ Create directory or display message if directory already exists

    :param director: The directory """
    if os.path.isdir(directory):
        click.echo("Found {}, skipping folder creation".format(directory))
    else:
        click.echo("Creating {} ...".format(directory))
        os.mkdir(directory)

def create_json(fname, data):
    """ Create JSON file

    :param fname: Name of the file to be saved
    :param data: Array or dictionary to be converted to JSON
    """
    with open(fname, 'w') as outfile:
        json.dump(data, outfile, indent=2, separators=(',', ': '))

    return True

if __name__ == '__main__':
    create_module()
