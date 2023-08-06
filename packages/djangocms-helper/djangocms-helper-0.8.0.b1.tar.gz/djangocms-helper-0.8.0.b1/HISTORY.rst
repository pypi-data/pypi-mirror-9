.. :changelog:

History
-------

0.8.0 (unreleased)
++++++++++++++++++

* Add --native option to use native test command instead of djangocms-helper one
* Use django-discover-runner on Django 1.5 if present
* Better handling of runner options
* Add support for empty/dry-run arguments to makemigrations
* Add USE_CMS flag to settings when using django CMS configuration

0.7.0 (2015-01-22)
++++++++++++++++++

* Fix an error which prevents the runner to discover the settings
* django CMS is no more a dependency, install it manually to enable django CMS support

0.6.0 (2015-01-10)
++++++++++++++++++

* Add a runner to make cms_helper file itself a runner for djangocms-helper
* Fix issues with mptt / treebeard and Django 1.7
* Fix some makemigrations / --migrate issues
* Make djangocms-helper less django CMS dependent

0.5.0 (2015-01-01)
++++++++++++++++++

* Fixing bugs when using extra settings
* Add messages framework to default environment
* Add CSRF middleware / context_processor to default settings
* Add base helper class for test cases
* Complete Django 1.7 support
* Smarter detection of migration operations in Django 1.6-
* Add option to create migrations for external applications

0.4.0 (2014-09-18)
++++++++++++++++++

* Add support for command line test runner options;
* Add check command on Django 1.7+;
* Add cms check command (which triggers cms inclusion);
* Add squashmigration command Django 1.7+;
* Add support for makemigrations merge on Django 1.7+;
* Add helpers for custom user models;

0.3.1 (2014-08-25)
++++++++++++++++++

* Add staticfiles application;
* Add djangocms_admin_style if cms is enabled;

0.3.0 (2014-08-14)
++++++++++++++++++

* Add support for django nose test runner;
* Add default CMS template;

0.2.0 (2014-08-12)
++++++++++++++++++

* Add option to customize sample project settings;
* Add option to exclude djanigo CMS from test project configurations;
* Add support for Django 1.7;

0.1.0 (2014-08-09)
++++++++++++++++++

* First public release.
