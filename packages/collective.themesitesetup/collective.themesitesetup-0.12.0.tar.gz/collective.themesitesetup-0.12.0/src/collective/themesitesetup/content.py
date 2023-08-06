# -*- coding: utf-8 -*-
from ConfigParser import ConfigParser
from Products.CMFCore.exportimport.content import StructureFolderWalkingAdapter
from Products.CMFCore.exportimport.content import encode_if_needed
from Products.GenericSetup.content import FolderishExporterImporter
from Products.GenericSetup.interfaces import IContentFactoryName
from Products.GenericSetup.interfaces import IFilesystemExporter
from Products.GenericSetup.interfaces import IINIAware
from Products.GenericSetup.utils import _getDottedName
from collective.themesitesetup.interfaces import IGenericSetupExportableContainer  # noqa
from csv import writer
from io import BytesIO
import Acquisition


class ManagedFolderishExporterImporter(FolderishExporterImporter):

    def listExportableItems(self):
        exportable = super(ManagedFolderishExporterImporter, self).listExportableItems()  # noqa
        exportable = [x for x in exportable if x[2] is not None]
        return exportable

    def export(self, export_context, subdir, root=False):
        super(ManagedFolderishExporterImporter, self).export(export_context, subdir, root)  # noqa
        export_context.writeDataFile('.preserve', text='*',
                                     content_type='text/plain', subdir=subdir)


# noinspection PyPep8Naming
class ManagedSiteRootExporterImporter(StructureFolderWalkingAdapter):
    """Enhanced structure folder walking adapter for site root:

    - supports exporting selected non-CMF-containers
    - adds .preserve -file to never delete e.g. Members-folder

    """
    def listExportableItems(self):
        ids = self.context.contentIds()
        exportable = self.context.objectItems()
        exportable = [(id_, obj) for id_, obj in exportable
                      if (id_ in ids
                          or IGenericSetupExportableContainer.providedBy(obj))]
        exportable = [x + (IFilesystemExporter(x[1], None),)
                      for x in exportable]
        exportable = [x for x in exportable if x[2] is not None]
        return exportable

    def export(self, export_context, subdir, root=False):
        context = self.context

        if not root:
            subdir = '%s/%s' % (subdir, context.getId())

        stream = BytesIO()
        csv_writer = writer(stream)

        exportable = self.listExportableItems()

        for object_id, obj, adapter in exportable:
            if hasattr(Acquisition.aq_base(obj), 'getPortalTypeName'):
                csv_writer.writerow((object_id, obj.getPortalTypeName()))
            else:
                factory_namer = IContentFactoryName(obj, None)
                if factory_namer is None:
                    factory_name = _getDottedName(obj.__class__)
                else:
                    factory_name = factory_namer()
                csv_writer.writerow((object_id, factory_name))

        export_context.writeDataFile('.objects',
                                     text=stream.getvalue(),
                                     content_type='text/comma-separated-values',  # noqa
                                     subdir=subdir,
                                     )

        prop_adapter = IINIAware(context, None)

        parser = ConfigParser()
        if prop_adapter is not None:
            parser.readfp(BytesIO(prop_adapter.as_ini()))

        title = context.Title()
        description = context.Description()
        title_str = encode_if_needed(title, 'utf-8')
        description_str = encode_if_needed(description, 'utf-8')
        parser.set('DEFAULT', 'Title', title_str)
        parser.set('DEFAULT', 'Description', description_str)

        stream = BytesIO()
        parser.write(stream)

        export_context.writeDataFile('.properties',
                                     text=stream.getvalue(),
                                     content_type='text/plain',
                                     subdir=subdir,
                                     )

        for object_id, obj, adapter in exportable:
            if adapter is not None:
                adapter.export(export_context, subdir)

        export_context.writeDataFile('.preserve', text='*',
                                     content_type='text/plain', subdir=subdir)
