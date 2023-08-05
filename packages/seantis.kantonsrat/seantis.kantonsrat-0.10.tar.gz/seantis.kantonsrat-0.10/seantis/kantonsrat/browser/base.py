from five import grok

from seantis.plonetools.browser import BaseView as SharedBaseView
from seantis.plonetools.browser import BaseForm as SharedBaseForm

from seantis.kantonsrat.interfaces import ISeantisKantonsratSpecific


class BaseView(SharedBaseView):

    grok.baseclass()
    grok.layer(ISeantisKantonsratSpecific)

    domain = 'seantis.kantonsrat'


class BaseForm(SharedBaseForm):

    grok.baseclass()
    grok.layer(ISeantisKantonsratSpecific)

    domain = 'seantis.kantonsrat'
