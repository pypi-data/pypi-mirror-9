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
  uploaded_dir: /opt/static/uploaded_site1/,
  static_dir: /opt/static/site1/,
  www_uploaded_path: /uploaded/,
  www_static_path: /m/,
  virtual_env_dir: /opt/virtualenvs/env-site1/,
  settings_module: settings
  max_procs: 3
```

### Defaults
The paths in the example above are the defaults if nothing is specified in the config file.
In a future versions you will be able to set your defaults yourself.

# TODO

- More fine tuning of site performance settings.
