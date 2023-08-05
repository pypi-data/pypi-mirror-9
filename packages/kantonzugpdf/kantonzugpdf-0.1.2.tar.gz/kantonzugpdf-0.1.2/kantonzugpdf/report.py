import pkg_resources
import tempfile

from copy import deepcopy
from datetime import date
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


class Template(ReportingDocTemplate):
    """ Extends the ReportingDocTemplate with Table of Contents printing.
    Might be nice in the official pdfdocument lib as well, but reportlab's
    3.0 release broke table of contents and pdfdocument shouldn't rely on 2.7.

    """

    def afterFlowable(self, flowable):

        ReportingDocTemplate.afterFlowable(self, flowable)

        if hasattr(flowable, 'toc_level'):
            self.notify('TOCEntry', (
                flowable.toc_level, flowable.getPlainText(), self.page,
                flowable.bookmark
            ))


class PDF(PDFDocument):

    def __init__(self, *args, **kwargs):
        self.doc = Template(*args, **kwargs)
        self.doc.PDFDocument = self
        self.story = []
        self.toc_numbering = {}

        self.font_name = kwargs.get('font_name', 'Helvetica')
        self.font_size = kwargs.get('font_size', 10)

        self.margin_left = 3.5*cm
        self.margin_top = 5.2*cm
        self.margin_bottom = 4*cm
        self.margin_right = 1.5*cm

    def generate_style(self, font_name=None, font_size=None):
        super(PDF, self).generate_style(font_name, font_size)
        self.style.heading4 = deepcopy(self.style.heading3)
        self.style.heading5 = deepcopy(self.style.heading3)
        self.style.heading6 = deepcopy(self.style.heading3)

    def table_of_contents(self):
        self.toc = TableOfContents()

        self.toc.levelStyles[0].leftIndent = 0
        self.toc.levelStyles[0].rightIndent = 0.25*cm
        self.toc.levelStyles[0].fontName = self.font_name
        self.toc.levelStyles[0].fontName = '{}-Bold'.format(
            self.font_name
        )
        self.toc.levelStyles[0].spaceBefore = 0.2*cm
        for idx in range(1, 7):
            toc_style = deepcopy(self.toc.levelStyles[0])
            toc_style.name = 'Level {}'.format(idx)
            toc_style.fontName = self.font_name
            toc_style.spaceBefore = 0
            self.toc.levelStyles.append(toc_style)

        self.toc.dotsMinLevel = 7
        self.toc.tableStyle = TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0.2*cm)
        ])
        self.story.append(self.toc)

    def add_toc_heading(self, text, style=None, toc_level=0, num_level=0):
        has_toc = toc_level is not None and hasattr(self, 'toc')

        if self.toc_numbering is not None and num_level is not None:
            # increment current level
            if num_level not in self.toc_numbering:
                self.toc_numbering[num_level] = 0
            self.toc_numbering[num_level] += 1

            # reset higher levels
            for idx in range(num_level+1,
                             max(self.toc_numbering.keys())+1):
                self.toc_numbering[idx] = 0

            # create and append prefix
            prefix = '.'.join([
                str(self.toc_numbering.get(idx)) or u''
                for idx in range(num_level+1)
            ])
            text = u'{} {}'.format(prefix, text)

        if has_toc:
            bookmark = new_uuid().hex
            text = u'{}<a name="{}"/>'.format(text, bookmark)

        self.story.append(MarkupParagraph(text, style))

        if has_toc:
            self.story[-1].toc_level = toc_level
            self.story[-1].bookmark = bookmark

    def h(self, text):
        self.story.append(MarkupParagraph(text, self.style.heading))

    def h1(self, text, toc_level=0):
        self.add_toc_heading(text, self.style.heading1, toc_level, 0)

    def h2(self, text, toc_level=1):
        self.add_toc_heading(text, self.style.heading2, toc_level, 1)

    def h3(self, text, toc_level=2):
        self.add_toc_heading(text, self.style.heading3, toc_level, 2)

    def h4(self, text, toc_level=3):
        self.add_toc_heading(text, self.style.heading4, toc_level, 3)

    def h5(self, text, toc_level=4):
        self.add_toc_heading(text, self.style.heading5, toc_level, 4)

    def h6(self, text, toc_level=5):
        self.add_toc_heading(text, self.style.heading6, toc_level, 5)

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

    def populate(self):
        raise NotImplementedError

    def build(self, context=None, request=None):
        self.context = context
        self.request = request
        self.populate()
        self.pdf.generate()
        self.file.seek(0)
        return self.file


class ReportZug(Report):
    """ Base Report for Kanton Zug. Implement 'populate' to add the elements
    that need to be printed.

    """

    def adjust_style(self):
        """ Changes the existing style of the report as defined by
        the pdfdocument module.

        """
        self.pdf.style.fontSize = 10

        self.pdf.style.normal.fontSize = 10
        self.pdf.style.normal.rightIndent = 0.2 * cm

        self.pdf.style.right.fontSize = 10
        self.pdf.style.right.rightIndent = 0.2 * cm

        self.pdf.style.heading1.fontName = '{}-Bold'.format(
            self.pdf.style.fontName
        )
        self.pdf.style.heading1.fontSize = 10
        self.pdf.style.heading1.spaceAfter = 0 * cm

        self.pdf.style.heading2 = deepcopy(self.pdf.style.heading1)
        self.pdf.style.heading3 = deepcopy(self.pdf.style.heading1)
        self.pdf.style.heading4 = deepcopy(self.pdf.style.heading1)
        self.pdf.style.heading5 = deepcopy(self.pdf.style.heading1)
        self.pdf.style.heading6 = deepcopy(self.pdf.style.heading1)

        self.pdf.style.heading = deepcopy(self.pdf.style.heading1)
        self.pdf.style.heading.fontSize = 16
        self.pdf.style.heading.spaceAfter = 1.2 * cm

    def first_page(self, canvas, doc):
        self.draw_logo(canvas)

    def later_page(self, canvas, doc):
        self.draw_document_footer(canvas, doc)

    def draw_logo(self, canvas):
        """ Draws the svg logo found in the controlpanel settings to the
        upper left corner. The dimensions are currently hard coded, if anyone
        else but the Canton of Zug really uses this module, make those
        dimensions avaiable through the controlpanel as well.

        """
        svg = self.get_logo()
        if not svg:
            return

        canvas.saveState()

        dimensions = {
            'xpos': 1.7*cm,
            'ypos': self.pdf.page_height - 1.7*cm,
            'xsize': 4.6*cm,
            'ysize': 0.96*cm
        }

        # self.pdf.draw_svg doesn't do strings, only file paths
        with tempfile.NamedTemporaryFile() as temp:
            temp.file.seek(0)
            temp.file.write(svg)
            temp.file.flush()

            self.pdf.draw_svg(canvas, temp.name, **dimensions)

        canvas.restoreState()

    def draw_document_footer(self, canvas, doc):
        """ Draws the document footer, including report title, date and
        page number.

        """
        canvas.saveState()

        # report title and print date
        print_date = self.get_print_date_text()
        footer_info = '<br />'.join((self.title, print_date))
        p = MarkupParagraph(footer_info, self.pdf.style.normal)
        w, h = p.wrap(5*cm, doc.bottomMargin)
        p.drawOn(canvas, self.pdf.margin_left, h)

        # page number
        page_info = '<br />' + str(doc.page_index()[0])
        p = MarkupParagraph(page_info, self.pdf.style.right)
        w, h = p.wrap(1*cm, doc.bottomMargin)
        p.drawOn(canvas, self.pdf.page_width - self.pdf.margin_right - 1*cm, h)

        canvas.restoreState()

    def get_print_date_text(self):
        """ Returns a readable representation of the current date."""
        return 'Print date: %s' % date.today().isoformat()

    def get_logo(self):
        return pkg_resources.resource_string('kantonzugpdf',
                                             'resources/logo_zug.svg')
