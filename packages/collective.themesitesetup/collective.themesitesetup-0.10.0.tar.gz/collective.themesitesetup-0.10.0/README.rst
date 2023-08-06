collective.themesitesetup
=========================

.. image:: https://secure.travis-ci.org/datakurre/collective.themesitesetup.png
   :target: https://travis-ci.org/datakurre/collective.themesitesetup

**collective.themesitesetup** is a plugin for `plone.app.theming`_. With this
plugin it's possible to embed automatically imported generic setup profiles
into a zipped theme package: one to be imported when theme is activated from
the theming control panel, and the other one to be imported when theme is
deactivated (as so called *uninstall profile*).

.. _plone.app.theming: https://pypi.python.org/pypi/plone.app.theming

**Note:** Due to regression in *plone.app.theming*, this package will work only
when a fixing pull for it is accepted and new version released (1__, 2__, 3__):

__ https://github.com/plone/plone.app.theming/pull/38
__ https://github.com/plone/plone.app.theming/pull/39
__ https://github.com/plone/plone.app.theming/pull/40

Once this plugin is included into your Plone site (e.g. including it into the
buildout eggs list and running the buildout), the plugin is enabled for the
theme by adding the following line into its ``manifest.cfg``:

.. code:: ini

   [theme:genericsetup]

By default the plugin looks the profile imported during activation from a theme
sub-directory called ``install`` and the profile imported during deactivation
from a sub-directory called ``uninstall``. The default lookup directories can
be customized in ``manifest.cfg``:

.. code:: ini

   [theme:genericsetup]
   install = my-install
   uninstall = my-uninstall

The importable profile can be edited TTW through the theme editor:

.. image:: https://raw.githubusercontent.com/collective/collective.themesitesetup/master/docs/images/edit-site-setup.png
   :width: 768px
   :align: center

**Note:** Because the theme editor hides all *dotfiles*, files starting with a
dot must be renamed to end with ``.dotfile`` (and to not start with a dot).

This plugin also provides a helper form for exporting the current site setup
into a through-the-web created (editable) theme. The helper form can be reached
by adding ``@@export-site-setup`` after the theme resource directory URL,
e.g. ``http://localhost:8080/Plone/++theme++my-theme/@@export-site-setup``:

.. image:: https://raw.githubusercontent.com/collective/collective.themesitesetup/master/docs/images/export-site-setup.png
   :width: 768px
   :align: center
