# -*- coding: utf-8 -*-

################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################


import hurry
import inspect
import humanize
import datetime
import fs.opener
import fs.errors
from zope.component import getUtility
from plone.app.registry.browser import controlpanel
from Products.Five.browser import BrowserView

from xmldirector.plonecore.i18n import MessageFactory as _
from xmldirector.plonecore.interfaces import IWebdavSettings
from xmldirector.plonecore.interfaces import IWebdavHandle


class DBSettingsEditForm(controlpanel.RegistryEditForm):

    schema = IWebdavSettings
    label = _(u'XML Director core settings')
    description = _(u'')

    def updateFields(self):
        super(DBSettingsEditForm, self).updateFields()

    def updateWidgets(self):
        super(DBSettingsEditForm, self).updateWidgets()


class DBSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = DBSettingsEditForm

    def connection_test(self):

        service = getUtility(IWebdavHandle)
        errors = []

        try:
            service.webdav_handle()
        except fs.errors.PermissionDeniedError as e:
            errors.append(
                u'Permission denied error - improper credentials? ({})'.format(e))
            return errors
        except fs.errors.ResourceNotFoundError as e:
            errors.append(
                u'Resource not found - local webdav path correct? ({})'.format(e))
            return errors
        except fs.errors.RemoteConnectionError as e:
            errors.append(u'WebDAV URL incorrect! ({})'.format(str(e)))
            return errors

        return errors


class ValidatorRegistry(BrowserView):

    @property
    def registry(self):
        from zope.component import getUtility
        from xmldirector.plonecore.interfaces import IValidatorRegistry
        return getUtility(IValidatorRegistry)

    def get_entries(self):
        return self.registry.entries()

    def validator_content(self):
        """ Return the schema content of the given schema """

        family = self.request['family']
        name = self.request['name']
        key = '{}::{}'.format(family, name)
        d = self.registry.registry.get(key)
        with fs.opener.opener.open(d['path'], 'rb') as fp:
            return dict(text=fp.read(), ace_type='xml')

    def human_readable_datetime(self, dt):
        """ Convert with `dt` datetime string into a human readable
            representation using humanize module.
        """
        diff = datetime.datetime.utcnow() - dt
        return humanize.naturaltime(diff)

    def human_readable_filesize(self, num_bytes):
        """ Return num_bytes as human readable representation """
        return hurry.filesize.size(num_bytes, hurry.filesize.alternative)


class TransformerRegistry(BrowserView):

    @property
    def registry(self):
        from zope.component import getUtility
        from xmldirector.plonecore.interfaces import ITransformerRegistry
        return getUtility(ITransformerRegistry)

    def transformer_content(self):
        """ Return the transformer content of the given transformer"""

        family = self.request['family']
        name = self.request['name']
        key = '{}::{}'.format(family, name)
        d = self.registry.registry.get(key)

        if d['type'] in ('XSLT1', 'XSLT2', 'XSLT3'):
            with fs.opener.opener.open(d['path'], 'rb') as fp:
                return dict(text=fp.read(), ace_type='xml', transformer_type=d['type'])
        elif d['type'] == 'python':
            return dict(text=inspect.getsource(d['transform']), ace_type='python', transformer_type=d['type'])
        else:
            raise ValueError(
                'Unsupported transformer type "{}"'.format(d['type']))

    def get_entries(self):
        return self.registry.entries()

    def human_readable_datetime(self, dt):
        """ Convert with `dt` datetime string into a human readable
            representation using humanize module.
        """
        diff = datetime.datetime.utcnow() - dt
        return humanize.naturaltime(diff)

    def human_readable_filesize(self, num_bytes):
        """ Return num_bytes as human readable representation """
        return hurry.filesize.size(num_bytes, hurry.filesize.alternative)
