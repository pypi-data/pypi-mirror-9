from five import grok

from seantis.plonetools.browser import BaseView as SharedBaseView
from seantis.plonetools.browser import BaseForm as SharedBaseForm

from seantis.translators.interfaces import ISeantisTranslatorsSpecific


class BaseView(SharedBaseView):

    grok.baseclass()
    grok.layer(ISeantisTranslatorsSpecific)

    domain = 'seantis.translators'


class BaseForm(SharedBaseForm):

    grok.baseclass()
    grok.layer(ISeantisTranslatorsSpecific)

    domain = 'seantis.translators'
