# -*- coding: utf-8 -*-
from __future__ import print_function

from web_framework import registry
from web_framework import site_config

site_config.add('siteconfig/modules/{name}-siteconfig.json')

MODULES = registry.Registry()

@MODULES("{name}")
def featured_jobs(module, front_type, front_name, **kwargs):
    print("WE MADE IT!")