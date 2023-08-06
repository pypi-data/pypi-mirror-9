# simple-site-manager

This creates configuration files for lighttpd and django fcgi, based on a simple list of sites. 
Templates are used for the output files so they can easily be modified and customised for your own sites.

You can either use a global config file or individual files for each project.

The project is in the early stages, barely tested. More to come. Born from the frustration I felt every time I wanted to delpoy a new python driven site...

## Example site list
```yaml
site1:
  domain_name: example.com
  # optional arguments
  redirect_from_domains: ['www.example.com']
  project_root_dir: /opt/django/site1/,
  django_root_dir: /opt/django/site1/site1/,
  fcgi_path: /opt/django/site1/site1/siteman-fcgi.py,
  uploaded_dir: /opt/static/site1_uploaded/,
  static_dir: /opt/static/site1/,
  www_uploaded_path: /uploaded/,
  www_static_path: /m/,
  virtual_env_dir: /opt/django/site1/env-site1/,
  settings_module: site1.settings
  max_procs: 3
```

### Defaults
The paths in the example above are the defaults if nothing is specified in the config file.
In a future versions you will be able to set your defaults yourself.

Here are some defaults:
```
    root of your project:                        /opt/django/sitename/
    fcgi file path (where manage.py is located): /opt/django/sitename/sitename/
    static files:                                /opt/static/sitename/
    static uploaded files:                       /opt/static/sitename_uploaded/
    settings file:                               /opt/django/sitename/sitename/sitename/settings.py
    settings module:                             sitename.settings
    virtualenv path:                             /opt/django/sitename/env-sitename/
```

# TODO

- More fine tuning of site performance settings.
