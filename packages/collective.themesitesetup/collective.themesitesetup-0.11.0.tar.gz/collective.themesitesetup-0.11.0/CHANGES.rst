Changelog
=========

0.11.0 (2015-04-04)
-------------------

- Add site setup import view to allow testing manual upgrading of site setups
  [datakurre]
- Add option to disable setup steps import via plugin configuration variable in
  theme manifest (either with 'enabled = false' or 'disabled = true')
  [datakurre]

0.10.0 (2015-04-03)
-------------------

- Add GS content export support to include non-CMF-containers
  marked with
  ``collective.themesitesetup.interfaces.IGenericSetupExportableContainer``
  [datakurre]

- Add GS content export/import to support non-CMF-containers, PythonScripts
  and PageTemplates.
  [datakurre]

0.9.0 (2015-04-01)
------------------

- First release.
