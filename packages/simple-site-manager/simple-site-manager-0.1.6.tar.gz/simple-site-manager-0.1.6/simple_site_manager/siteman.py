#!/usr/bin/env python
# The MIT License (MIT)
# Copyright (c) 2015 Dmitri Fedortchenko
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.


import os
import argparse
import re
import sys
import yaml
from jinja2 import Environment, PackageLoader
env = Environment(loader=PackageLoader('simple_site_manager', "templates"))

DEFAULTS = {
    "project_root_dir": "/opt/django/%(project_name)s/",
    "django_root_dir": "%(project_root_dir)s%(project_name)s/",
    "fcgi_path": "%(django_root_dir)ssiteman-fcgi.py",
    "uploaded_dir": "/opt/static/%(project_name)s_uploaded/",
    "static_dir": "/opt/static/%(project_name)s/",
    "www_uploaded_path": "/uploaded/",
    "www_static_path": "/m/",
    "max_procs": "3",
    "virtual_env_dir": "%(project_root_dir)senv-%(project_name)s/",
    "settings_module": "settings",
    'redirect_from_domains': []
}

class Server(object):
    def __init__(self, config_file, dry_run=False):
        self.dry_run = dry_run
        self.sites = []
        for site in sites_for_settings(config_file):
            self.sites.append(site)

    def write_fcgi_file(self, site):
        conf = site.generate_fcgi_file()
        if not self.dry_run:
            with open(site.fcgi_path, 'w') as f:
                f.write(conf)
            os.chmod(site.fcgi_path, 0755)
        return site.fcgi_path

    def write_ligttpd_config(self, site):
        config_path = "/etc/lighttpd/"
        file_path = os.path.join(config_path, u"conf-available/siteman-%s.conf" % site.project_name)
        symlink_path = os.path.join(config_path, u"conf-enabled/siteman-%s.conf" % site.project_name)

        conf = site.generate_lighttpd_config()
        if not self.dry_run:
            with open(file_path, 'w') as f:
                f.write(conf)
            if os.path.exists(symlink_path):
                os.unlink(symlink_path)
            os.symlink(file_path, symlink_path)
        return ', '.join((file_path, symlink_path))


    def write(self):
        for site in self.sites:
            print ("Writing files for %s" % site)
            if self.dry_run:
                print("**DRY RUN**")
            print("Wrote %s" % self.write_ligttpd_config(site))
            print("Wrote %s" % self.write_fcgi_file(site))

def sites_for_settings(config_file):
    config_data = yaml.load(config_file)
    for site_name, site_data in config_data.items():
        yield Site(site_name, **site_data)

class Site(object):
    def _path_fix(self, path):
        matches = re.match(r"^/?(.*)/?$", path)
        return u"/%s/" % matches.group(1)

    def _or_default(self, kwargs, key):
        return kwargs.get(key, str(DEFAULTS[key]) % vars(self))

    def __repr__(self):
        return self.project_name

    def __init__(self, name, **kwargs):

        self.project_name = name
        self.domain_name = kwargs['domain_name']
        self.project_root_dir = self._or_default(kwargs, 'project_root_dir')

        self.django_root_dir = self._or_default(kwargs, 'django_root_dir')

        self.uploaded_dir = self._or_default(kwargs, 'uploaded_dir')

        self.static_dir = self._or_default(kwargs, 'static_dir')

        self.www_uploaded_path = self._or_default(kwargs, "www_uploaded_path")
        self.www_static_path = self._or_default(kwargs, 'www_static_path')

        self.fcgi_path = self._or_default(kwargs, "fcgi_path")
        self.max_procs = self._or_default(kwargs, 'max_procs')

        self.virtual_env_dir = self._or_default(kwargs, 'virtual_env_dir')
        self.settings_module = self._or_default(kwargs, 'settings_module')
        if 'settings_module' not in kwargs:
            self.settings_module = u"%s.%s" % (self.project_name, self.settings_module)

        self.redirect_from_domains = kwargs.get('redirect_from_domains', [])

    def generate_fcgi_file(self):
        template = env.get_template('fcgi.py.jinja2')
        return template.render(**vars(self))

    def generate_lighttpd_config(self):
        template = env.get_template('lighttpd.conf.jinja2')
        return template.render(**vars(self))

def main_func():
    parser = argparse.ArgumentParser(description='Create lighttpd configuration files and fcgi.py files.')

    parser.add_argument('--print', "-p", action='store_true',
                        required=False,
                        help='print all file data to console')
    parser.add_argument('--dry_run', action='store_true',
                        required=False,
                        help='just print file actions')
    parser.add_argument('config_file',
                        type=argparse.FileType('r'),
                        nargs=1,
                        default=sys.stdin,
                        #required=True,
                        help='site list file')

    args = vars(parser.parse_args())
    config_file = args['config_file'][0]
    dry_run = args.get('dry_run', False)
    server = Server(config_file, dry_run=dry_run)
    if not args['print']:
        server.write()
    else:
        for site in server.sites:
            print("------------------------------------------------")
            print("fcgi.py")
            print("------------------------------------------------")
            print(site.generate_fcgi_file())
            print("------------------------------------------------")
            print("lighttpd.conf")
            print("------------------------------------------------")
            print(site.generate_lighttpd_config())

if __name__ == "__main__":
    main_func()
