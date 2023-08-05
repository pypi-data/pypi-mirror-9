Disable / enable versioning sections
------------------------------------

It can be helpful to disable versioning during content construction to avoid
storing incomplete versions in the content item's revision history.

For example::

    [transmogrifier]
    pipeline =
        schemasource
        disable_versioning
        constructor
        enable_versioning
        schemaupdater

    [disable_versioning]
    blueprint = plone.app.transmogrifier.versioning.disable

    [constructor]
    blueprint = collective.transmogrifier.sections.constructor

    [enable_versioning]
    blueprint = plone.app.transmogrifier.versioning.enable

