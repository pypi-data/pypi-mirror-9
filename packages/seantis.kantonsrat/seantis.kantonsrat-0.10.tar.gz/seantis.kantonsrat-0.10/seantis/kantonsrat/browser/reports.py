import os
import codecs

from five import grok

from zope.interface import Interface
from zExceptions import NotFound

from seantis.kantonsrat.reports import get_available_reports
from seantis.kantonsrat.browser.base import BaseView


class Report(BaseView):

    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('kantonsrat-report')

    def render(self):

        report = get_available_reports().get(self.request.get('id'))

        if not report:
            raise NotFound()

        return self.get_response(
            filename=self.translate(report['title']),
            filehandle=report['class']().build(self.context, self.request)
        )

    def get_response(self, filename, filehandle):
        filename = codecs.utf_8_encode('filename="%s.pdf"' % filename)[0]
        self.request.RESPONSE.setHeader('Content-disposition', filename)
        self.request.RESPONSE.setHeader('Content-Type', 'application/pdf')

        response = filehandle.getvalue()
        filehandle.seek(0, os.SEEK_END)

        filesize = filehandle.tell()
        filehandle.close()

        self.request.RESPONSE.setHeader('Content-Length', filesize)

        return response
