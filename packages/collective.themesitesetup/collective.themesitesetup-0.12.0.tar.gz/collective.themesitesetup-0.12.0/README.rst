collective.themesitesetup
=========================

.. image:: https://secure.travis-ci.org/datakurre/collective.themesitesetup.png
   :target: https://travis-ci.org/datakurre/collective.themesitesetup

**collective.themesitesetup** is a `plone.app.theming`_-plugin for
embedding GenericSetup_-steps into zipped theme packages.

**collective.themesitesetup** can automatically import one embedded set of
generic setup steps during theme activation and another one (so called
*uninstall profile*) when theme is deactivated. Yet, also additionals ets
can be embedded and imported manually.

See it activating theme site setup at: https://youtu.be/3vkrc7JFUU0

.. _plone.app.theming: https://pypi.python.org/pypi/plone.app.theming
.. _GenericSetup: https://pypi.python.org/pypi/Products.GenericSetup

**Note:** Due to regression in the plugin support in `plone.app.theming`_, the
automatic import of setup steps require a currently (as of 2015-04-04)
unreleased version with one of the fixing pull requests merged (1__, 2__,
3__).

__ https://github.com/plone/plone.app.theming/pull/38
__ https://github.com/plone/plone.app.theming/pull/39
__ https://github.com/plone/plone.app.theming/pull/40


Installation
------------

Simply include this package into your Plone site buildout by following
`the official instructions`_. This add-on doesn't require other activation,
but, of course, requires `plone.app.theming`_ to be activated.

.. _the official instructions: http://docs.plone.org/manage/installing/installing_addons.html


Configuration
-------------

This plugin is enabled for any theme by simply adding the following line into
theme's ``manifest.cfg``:

.. code:: ini

   [theme:genericsetup]

By default, this looks for the setup steps to be imported during activation
from theme's ``install``-subdirectory and the steps to be imported during
deactivation from theme's ``uninstall``-subdirectory. If such directory does
not exist, this plugin simply does not import any steps.

The default lookup directories can be customized by overriding the defaults
with custom values in theme's ``manifest.cfg``:

.. code:: ini

   [theme:genericsetup]
   install = my-install
   uninstall = my-uninstall

This plugin can also be disabled at any time simply by adding the line
``disabled = true`` into plugin's configuration in theme's ``manifest.cfg``:

.. code:: ini

   [theme:genericsetup]
   disabled = true


Exporting the site setup
------------------------

This plugin provides helper forms for exporting the current site setup
into a through-the-web created (writable) theme and importing that site setup
manually from the theme folder.

The export form is registered for the theme resource directory as
``@@export-site-setup`` and the import form as ``@@import-site-setup``.

The export form is useful for creating the initial site setup into the theme
directory. Simply

1. Create a new theme from Theming control panel

2. Go to the export form URL, e.g.
   ``http://localhost:8080/Plone/++theme++my-theme/@@export-site-setup``:

3. Choose the steps you wish to export and click *Export*.

.. image:: https://raw.githubusercontent.com/collective/collective.themesitesetup/master/docs/images/export-site-setup.png
   :width: 768px
   :align: center


Editing the site setup
----------------------

The site setup steps can be edited like any theme file through the
theme editor:

.. image:: https://raw.githubusercontent.com/collective/collective.themesitesetup/master/docs/images/edit-site-setup.png
   :width: 768px
   :align: center

**Tip:** You can Use `six feet up`_'s great `Generic Setup reference card`__ as
cheat cheet for editing the site setup files.

.. _six feet up: http://www.sixfeetup.com
__ http://www.sixfeetup.com/plone-cms/quick-reference-cards/generic_setup.pdf/view

**Note:** Because the theme editor hides all *dotfiles*, files starting with a
dot must be renamed to end with ``.dotfile`` (and to not start with a dot).


Importing the setup
-------------------

By default, this plugin is configured import setup steps from a directory
``install`` whenever the theme is activated, and steps from a directory
``uninstall``, when the theme is deactivated. Both, install and uninstall
step directory can be changed in the plugin configuration.

In addition, it's possible to import the embedded steps manually using
the import setup form. Simply

1. Go to the import form URL for your theme, e.g.
   ``http://localhost:8080/Plone/++theme++my-theme/@@import-site-setup``:

2. Choose the steps you wish to import and click *Import*.


Better site structure export and import
---------------------------------------

This package includes optional enhancements for the default Plone site
structure export and import.

The enhancements include:

- support for News Item contents
- support for Zope Page Templates
- support for Python Scripts
- support for exporting tagged hidden folders (like ``portal_skins/custom``)

The enhancements can be activated by including a special component
configuration file in your Plone buildout's instance parts with:

.. code:: ini

   [instance]
   ...
   zcml = collective.themesitesetup-extras

ZMI-only content, which is hidden in Plone (folders like ``portal_skins``) can
be included in the export by tagging the folders in ZMI interface tab with a
special marker interface::

    ``collective.themesitesetup.interfaces.IGenericSetupExportableContainer``


PageTemplates and PythonScripts can only be exported when they are located in a
ZMI-only container with this marker interface. So, if you'd like to export
contents in ``portal_skins/custom``, you should add one marker for
``portal_skins`` and the other for ``custom``.

This is only required when exporting ZMI-only content. Importing ZMI-only
content works according to normal structure import rules without these marker
interfaces.
