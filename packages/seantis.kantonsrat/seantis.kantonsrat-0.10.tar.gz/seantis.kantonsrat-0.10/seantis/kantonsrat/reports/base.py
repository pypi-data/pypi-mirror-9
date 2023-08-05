from io import BytesIO
from uuid import uuid4 as new_uuid
from pdfdocument.document import (
    PDFDocument,
    ReportingDocTemplate,
    PageTemplate,
    NextPageTemplate,
    dummy_stationery,
    Frame,
    cm,
    MarkupParagraph
)
from reportlab.platypus.tables import TableStyle
from reportlab.platypus.tableofcontents import TableOfContents
from seantis.plonetools import tools

""" seantis.kantonsrat uses pdfdocument which is built on reportlab to
do it's pdf reporting. Unfortunately, pdfdocument lacks quite a bit in
functionality so we need to build on it.

Since we have ocqms.reports internally which does more than pdfdocument
we have to eventually open source that because it is easier to use than
pdfdocument and more powerful the same time.

Unfortunately it depends too heavily on pyramid for now and it was faster
to build on pdfdocument than to create a new library, write docs and test,
just to use it here.

xxx => do me in the future

"""


class Template(ReportingDocTemplate):
    """ Extends the ReportingDocTemplate with Table of Contents printing.
    Might be nice in the official pdfdocument lib as well, but reportlab's
    3.0 release broke table of contents and pdfdocument shouldn't rely on 2.7.

    """

    def afterFlowable(self, flowable):

        ReportingDocTemplate.afterFlowable(self, flowable)

        if hasattr(flowable, 'toc_level'):
            text = '<b>{}</b>'.format(
                flowable.getPlainText()
            )
            self.notify('TOCEntry', (
                flowable.toc_level, text, self.page, flowable.bookmark
            ))


class PDF(PDFDocument):

    def __init__(self, *args, **kwargs):
        self.doc = Template(*args, **kwargs)
        self.doc.PDFDocument = self
        self.story = []

        self.font_name = kwargs.get('font_name', 'Helvetica')
        self.font_size = kwargs.get('font_size', 10)

        self.margin_left = 3.5*cm
        self.margin_top = 5.2*cm
        self.margin_bottom = 4*cm
        self.margin_right = 1.5*cm

    def table_of_contents(self):
        self.toc = TableOfContents()
        self.toc.levelStyles[0].leftIndent = 0
        self.toc.levelStyles[0].rightIndent = 0.25*cm
        self.toc.levelStyles[0].fontName = self.font_name
        self.toc.tableStyle = TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0.2*cm)
        ])
        self.story.append(self.toc)

    def add_toc_heading(self, heading, text, style=None, toc_level=0):
        has_toc = toc_level is not None and hasattr(self, 'toc')

        if has_toc:
            bookmark = new_uuid().hex
            text = u'{}<a name="{}"/>'.format(text, bookmark)

        self.story.append(MarkupParagraph(text, style))

        if has_toc:
            self.story[-1].toc_level = toc_level
            self.story[-1].bookmark = bookmark

    def h1(self, text, toc_level=0):
        self.add_toc_heading('h1', text, self.style.heading1, toc_level)

    def h2(self, text, toc_level=1):
        self.add_toc_heading('h2', text, self.style.heading2, toc_level)

    def h3(self, text, toc_level=2):
        self.add_toc_heading('h3', text, self.style.heading3, toc_level)

    def init_report(self, page_fn=dummy_stationery, page_fn_later=None):
        frame_kwargs = {
            'showBoundary': self.show_boundaries,
            'leftPadding': 0,
            'rightPadding': 0,
            'topPadding': 0,
            'bottomPadding': 0,
        }

        self.page_width, self.page_height = self.doc.pagesize

        # x and y start at the lower left corner
        full_frame = Frame(
            x1=self.margin_left,
            y1=self.margin_bottom,
            width=self.page_width - self.margin_left - self.margin_right,
            height=self.page_height - self.margin_top - self.margin_bottom,
            **frame_kwargs
        )

        self.doc.addPageTemplates([
            PageTemplate(
                id='First',
                frames=[full_frame],
                onPage=page_fn),
            PageTemplate(
                id='Later',
                frames=[full_frame],
                onPage=page_fn_later or page_fn),
        ])
        self.story.append(NextPageTemplate('Later'))
        self.generate_style(font_size=8)


class Report(object):
    """ Base Report object to use in new reports. Implement 'populate'
    to add the elements that need to be printed.

    """

    def __init__(self):
        self.file = BytesIO()
        self.pdf = PDF(self.file)
        self.pdf.init_report(
            page_fn=self.first_page, page_fn_later=self.later_page
        )

    def first_page(self, canvas, doc):
        pass

    def later_page(self, canvas, doc):
        pass

    def translate(self, text):
        return tools.translator(self.request, 'seantis.kantonsrat')(text)

    def populate(self):
        raise NotImplementedError

    def build(self, context, request):
        self.context = context
        self.request = request
        self.populate()
        self.pdf.generate()
        self.file.seek(0)
        return self.file
