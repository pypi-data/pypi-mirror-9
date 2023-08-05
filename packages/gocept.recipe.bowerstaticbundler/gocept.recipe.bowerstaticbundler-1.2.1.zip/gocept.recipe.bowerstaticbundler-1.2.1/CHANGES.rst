=======
CHANGES
=======

1.2.1 (2015-01-14)
==================

- Also copy images into the bundle dir, which will be rendered as the fav icon.

- Make generated .bower.json file more readable by adding newlines and indent.

- When copying resources, create a separate directory for each package to
  reduce probability of name clashes.


1.2.0 (2015-01-13)
==================

- Copy all template files into the bundle dir, rather building one huge
  bundle.pt template


1.1.1 (2015-01-12)
==================

- Prevent error on update if `bowerstatic_bundle` directory is missing.


1.1 (2015-01-12)
================

- Symlink additional resources references in CSS files (images, fonts, …) into
  the bundle and point minified CSS to these symlinks.


1.0.2 (2015-01-08)
==================

- Fixed handling of the ``pkg_resources`` working set when collecting
  resources from eggs.

- Make sure recipe does not brake when there are no resources to bundle.


1.0.1 (2014-09-20)
==================

- Repair homepage url in setup.py.


1.0.0 (2014-09-20)
==================

- Initial release.
