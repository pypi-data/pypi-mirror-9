# -*- coding: utf-8 -*-
from collective.themesitesetup.interfaces import DEFAULT_ENABLED_PROFILE_NAME
from io import BytesIO
from plone import api
from plone.autoform import directives
from plone.autoform.form import AutoExtensibleForm
from plone.supermodel import model
from plone.z3cform.layout import FormWrapper
from z3c.form import button
from z3c.form import form
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from zope import schema
from zope.interface import provider
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
import Acquisition
import re
import tarfile


# noinspection PyUnusedLocal,PyPep8Naming
@provider(IContextSourceBinder)
def genericSetupStepsSource(context):
    portal_setup = api.portal.get_tool('portal_setup')
    export_steps = portal_setup.listExportSteps()
    return SimpleVocabulary(map(SimpleTerm, map(str, export_steps)))


class IExportForm(model.Schema):

    directory = schema.BytesLine(
        title=u'Directory name',
        description=u'Give name for the theme sub-directory, where '
                    u'the generated export should be saved to. '
                    u'If the directory already exists, '
                    u'its content may get overridden.',
        default=DEFAULT_ENABLED_PROFILE_NAME
    )

    directives.widget(steps=CheckBoxFieldWidget)
    steps = schema.List(
        title=u'Exported steps',
        description=u'Select the steps, which should be included in '
                    u'the export.',
        value_type=schema.Choice(
            title=u'Step name',
            source=genericSetupStepsSource
        ),
        default=['content']
    )


# noinspection PyPep8Naming
class ExportForm(AutoExtensibleForm, form.Form):
    schema = IExportForm
    ignoreContext = True

    label = u'Export site setup into theme'
    description = (u'Export the current site setup '
                   u'and save as editable files into this '
                   u'theme (or resource) directory.')

    def __init__(self, context, request, directory=None):
        self.directory = directory
        super(ExportForm, self).__init__(context, request)

    # noinspection PyUnusedLocal
    @button.buttonAndHandler(u'Export')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        directoryName = (data.get('directory') or '').strip()
        exportSteps = filter(bool, map(str.strip, data.get('steps') or []))

        if not directoryName or not exportSteps:
            return

        # Create export
        portal_setup = api.portal.get_tool('portal_setup')
        # noinspection PyProtectedMember
        tarball = portal_setup._doRunExportSteps(exportSteps)['tarball']

        # Open the exported tarball
        fb = BytesIO(tarball)
        tar = tarfile.open(fileobj=fb, mode='r:gz')

        # Create base directory
        if not self.directory.isDirectory(directoryName):
            self.directory.makeDirectory(directoryName)
        baseDirectory = self.directory[directoryName]

        # Export tarball contents into the base directory
        for info in tar:
            if info.type == tarfile.DIRTYPE:
                baseDirectory.makeDirectory(info.name)
            else:
                path = info.path

                # Fix dotted names filted by source dictory API
                path = re.sub('/\.([^/]+)', '/\\1.dotfile', path)

                baseDirectory.writeFile(path, tar.extractfile(info))

        # Close the tarfile
        tar.close()

        # Report success
        self.status = u'Done.'


class ExportFormView(FormWrapper):
    form = ExportForm

    def __init__(self, context, request):
        # z3c.forms cannot be rendered with resource directory as context
        super(ExportFormView, self).__init__(api.portal.get(), request)

        # noinspection PyUnresolvedReferences
        self.form_instance = self.form(Acquisition.aq_inner(self.context),
                                       self.request, context)
        self.form_instance.__name__ = self.__name__

        # Disable green border
        self.request.set('disable_border', True)
