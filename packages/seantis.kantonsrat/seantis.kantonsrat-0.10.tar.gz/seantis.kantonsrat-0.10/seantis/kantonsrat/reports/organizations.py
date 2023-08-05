from datetime import datetime, date
import tempfile

from plone import api
from seantis.kantonsrat import _
from seantis.kantonsrat import settings

from pdfdocument.document import MarkupParagraph
from reportlab.lib.units import cm
from seantis.kantonsrat.reports.base import Report


class MembershipInfo(object):
    """ Holds and renders the infos related to a membership. """

    __slots__ = ('name', 'role', 'address_parts', 'party', 'elected')

    def __init__(self, name, role, address_parts, party):
        self.name = name
        self.role = role
        self.address_parts = address_parts
        self.party = party

    def get_text(self):
        parts = list()
        if self.name:
            parts.append(self.name)
        if self.address_parts:
            parts.extend(self.address_parts)
        if self.role:
            parts.append(self.role)

        return ', '.join(parts)


class MembershipNotes(object):
    """ Holds the infos related to the second table containing the notes
    about the memberships in the first table. """

    __slots__ = ('notes', 'reference')

    def __init__(self, notes, reference):
        self.notes = notes
        self.reference = reference


class OrganizationsReport(Report):
    """ Report to show the memberships of organizations found in the
    current context. Pretty much geared towards the CD of the Canton of Zug
    at this point. Parameters would have to be added to make this report
    look different in new deployments.

    """

    @property
    def without_table_of_content(self):
        return 'without-table-of-content' in self.request

    @property
    def with_this_organization(self):
        return self.request.get('with-this-organization')

    def adjust_style(self):
        """ Changes the existing style of the report as defined by
        the pdfdocument module.

        """
        self.pdf.style.heading1.fontName = '{}-Bold'.format(
            self.pdf.style.fontName
        )

        self.pdf.style.heading1.fontSize = 15
        self.pdf.style.heading1.spaceAfter = 1.2 * cm
        self.pdf.style.heading2.fontSize = 12
        self.pdf.style.heading2.spaceAfter = 0.6 * cm
        self.pdf.style.normal.fontSize = 9
        self.pdf.style.right.fontSize = 9
        self.pdf.style.normal.rightIndent = 0.2 * cm
        self.pdf.style.right.rightIndent = 0.2 * cm

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
        svg = settings.get('svg_logo')

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
        print_date = self.translate(_(u'Print date: ${date}', mapping={
            'date': self.get_date_text(self.report_date)
        }))

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

    def get_date_text(self, date):
        """ Returns a readable represantation of date. """
        return api.portal.get_localized_time(
            datetime=datetime.combine(
                date, datetime.min.time()
            )
        )

    def populate(self):
        """ Builds the structure of the report before it gets rendered. """
        self.title = self.context.title
        self.report_date = date.today()

        self.adjust_style()

        # First page contains the title and table of contents
        if not self.without_table_of_content:
            self.pdf.h1(self.title)
            self.pdf.table_of_contents()
            self.pdf.pagebreak()

        # Every other page contains the organisation and its members.
        # After each organization a page break is inserted.

        # The members are drawn in two tables. The first table contains the
        # members and the second table optionally includes notes about them
        # and shows which member from the first table replaced a previous
        # member.

        # 1: reference between table 1 and 2 (optional)
        # 2: member info or note
        # 3: party info (optional)
        table_columns = [1.2*cm, 13.3*cm, 2*cm]

        for organization in self.get_organizations(self.report_date):

            # the references are independent in each organization
            self.reset_references()

            self.pdf.h2(organization.title, toc_level=0)
            self.pdf.p(organization.description)
            self.pdf.spacer()

            tables = self.get_membership_tables(organization, self.report_date)

            for table_data in tables:
                if table_data:
                    self.pdf.table(
                        self.wrap_rows_in_paragraphs(table_data),
                        table_columns
                    )
                    self.pdf.spacer()

            if organization.start:
                self.pdf.p(self.translate(_(u'Election on ${date}', mapping={
                    'date': self.get_date_text(organization.start)
                })))

            self.pdf.pagebreak()

    def wrap_rows_in_paragraphs(self, table):
        """ Wraps the table contents in paragraphs to allow for correct
        word wrapping.

        """
        for row in table:
            row[0] = MarkupParagraph(row[0], self.pdf.style.right)
            row[1] = MarkupParagraph(row[1], self.pdf.style.normal)
            row[2] = MarkupParagraph(row[2], self.pdf.style.normal)

        return table

    def get_reference(self):
        """ Increments and returns a reference. References are just
        a growing number of stars:

        *)
        **)
        ***)

        """
        self.reference_count += 1
        return u'{})'.format(self.reference_count)

    def reset_references(self):
        self.reference_count = 0

    def get_person_party(self, person):
        """ Returns the party of the given person. """
        parties = person.parties
        return parties and parties[0] or ''

    def get_membership_info(self, membership):
        """ Returns a MembershipInfo instance for the given membership. """
        person = membership.person.to_object
        name = ' '.join((person.lastname, person.firstname))
        address_parts = [
            p.strip() for p in person.address.split('\n') if p.strip()
        ]
        party = self.get_person_party(person)

        return MembershipInfo(name, membership.role, address_parts, party)

    def get_membership_notes(self, membership):
        """ Returns a MembershipNote instance for the given membership. """

        if not membership.replacement_for and not membership.note:
            return None

        notes = []

        if membership.replacement_for:
            replaced_membership = membership.replacement_for.to_object
            info = self.get_membership_info(replaced_membership)
            info.elected = membership.start
            notes.append(info)

        if membership.note:
            notes.append(membership.note)

        return MembershipNotes(notes, self.get_reference())

    def get_membership_tables(self, organization, report_date):
        """ Returns the row/column data for both tables used in an
        organization. The first table is the memberships table, the second
        the notes table.

        """
        brains = organization.memberships('present', report_date)
        memberships = (o.getObject() for o in brains)

        memberships_table = []
        notes_table = []

        for ix, membership in enumerate(memberships):
            info = self.get_membership_info(membership)
            notes = self.get_membership_notes(membership)

            # the first row of the membership table is printed in bold
            if ix == 0:
                text = u'<b>{}</b>'.format(info.get_text())
            else:
                text = info.get_text()

            memberships_table.append([
                notes and notes.reference, text, info.party
            ])

            for ix, note in enumerate(notes and notes.notes or []):
                if isinstance(note, MembershipInfo):
                    if note.elected:
                        text = _(
                            u'Replacement for ${name}, elected on ${date}',
                            mapping={
                                'name': note.get_text(),
                                'date': self.get_date_text(note.elected)
                            }
                        )

                    else:
                        text = _(u'Replacement for ${name}', mapping={
                            'name': note.get_text()
                        })

                    text = self.translate(text)
                    party = note.party
                else:
                    text = note
                    party = ''

                notes_table.append([
                    ix == 0 and notes.reference or '', text, party
                ])

        return memberships_table, notes_table

    def get_organizations(self, report_date):
        catalog = api.portal.get_tool('portal_catalog')

        query = dict(
            path={'query': '/'.join(self.context.getPhysicalPath())},
            portal_type='seantis.kantonsrat.organization',
            sort_on='sortable_title'
        )

        if self.with_this_organization:
            query['UID'] = self.with_this_organization

        organizations = []

        for brain in catalog(**query):
            if report_date < (brain.start or date.min):
                continue

            if report_date > (brain.end or date.max):
                continue

            organizations.append(brain.getObject())

        return sorted(organizations, key=lambda o: o.title)
