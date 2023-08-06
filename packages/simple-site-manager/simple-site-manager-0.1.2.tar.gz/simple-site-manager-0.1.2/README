# simple-site-manager

This creates configuration files for lighttpd and django fcgi, based on a simple list of sites. 
Templates are used for the output files so they can easily be modified and customised for your own sites.

## Example site list
```yaml
site1:
  domain_name: example.com
  # optional arguments
  project_root_dir: /opt/django/site1/,
  django_root_dir: /opt/django/site1/site1/,
  fcgi_path: /opt/django/site1/site1/fcgi.py,
  uploaded_dir: /opt/static/uploaded_site1/,
  static_dir: /opt/static/site1/,
  www_uploaded_path: /uploaded/,
  www_static_path: /m/,
  virtual_env_dir: /opt/virtualenvs/env-site1/,
  settings_module: settings
  max_procs: 3
```

# TODO

- More fine tuning of site performance settings.
