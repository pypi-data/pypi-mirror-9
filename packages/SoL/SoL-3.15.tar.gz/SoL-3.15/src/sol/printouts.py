# -*- coding: utf-8 -*-
# :Progetto:  SoL
# :Creato:    ven 31 ott 2008 10:32:29 CET
# :Autore:    Lele Gaifax <lele@metapensiero.it>
# :Licenza:   GNU General Public License version 3 or later
#

"""
This module uses ReportLab to produce all the needed printouts.
"""

from copy import copy
from datetime import date, datetime, timedelta
import locale, logging
from babel.numbers import format_decimal

logger = logging.getLogger(__name__)

BASE_FONT_NAME = 'DejaVuSans'

from reportlab import rl_settings
rl_settings.canvas_basefontname = BASE_FONT_NAME

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont, TTFError

try:
    for variant in ('', '-Bold', '-Oblique', '-BoldOblique'):
        pdfmetrics.registerFont(TTFont(BASE_FONT_NAME + variant,
                                       BASE_FONT_NAME + "%s.ttf" % variant))
except TTFError: # pragma: no cover
    from reportlab import rl_config

    logger.error('Could not find the "%s" font, using PDF default fonts', BASE_FONT_NAME)

    BASE_FONT_NAME = 'Times-Roman'
    rl_config.canvas_basefontname = rl_settings.canvas_basefontname = BASE_FONT_NAME
    BOLD_ITALIC_FONT_NAME = 'Times-BoldItalic'
    ITALIC_FONT_NAME = 'Times-Italic'
else:
    BOLD_ITALIC_FONT_NAME = BASE_FONT_NAME + '-BoldOblique'
    ITALIC_FONT_NAME = BASE_FONT_NAME + '-Oblique'

    from reportlab.lib.fonts import addMapping
    addMapping(BASE_FONT_NAME, 0, 0, BASE_FONT_NAME)
    addMapping(BASE_FONT_NAME, 0, 1, BASE_FONT_NAME + '-Oblique')
    addMapping(BASE_FONT_NAME, 1, 0, BASE_FONT_NAME + '-Bold')
    addMapping(BASE_FONT_NAME, 1, 1, BASE_FONT_NAME + '-BoldOblique')

from reportlab.graphics import renderPDF
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.platypus import (BaseDocTemplate, CondPageBreak, Frame, FrameBreak, Image,
                                KeepTogether, NextPageTemplate, PageTemplate, Paragraph,
                                Spacer, TableStyle)
from reportlab.platypus.tables import Table

from sqlalchemy.orm.exc import NoResultFound

import sol
from .i18n import translatable_string as _, gettext, ngettext, translator
from .models import Rating, Championship, Tourney
from .models.errors import OperationAborted


base_style = getSampleStyleSheet()
"The base style used to build the document"

title_style = copy(base_style['Title'])
"The style used for the title of the document"

title_style.fontSize = 28
title_style.leading = title_style.fontSize*1.1

subtitle_style = copy(base_style['Heading1'])
"The style used for the subtitle of the document"

subtitle_style.fontSize = 20
subtitle_style.leading = subtitle_style.fontSize*1.1
subtitle_style.alignment = TA_CENTER
subtitle_style.fontName = ITALIC_FONT_NAME

heading_style = copy(base_style['Heading2'])
"The style used for the heading paragraphs of the document"

heading_style.alignment = TA_CENTER

normal_style = copy(base_style['Normal'])
"The style used for most of the paragraphs of the document"

normal_style.fontSize = 14
normal_style.leading = normal_style.fontSize*1.1

caption_style = copy(base_style['Italic'])
"The style used for the caption of the table's columns"

caption_style.fontSize = 9
caption_style.leading = caption_style.fontSize*1.1

cardtitle_style = copy(base_style['Normal'])
"The style used for the title of the score cards"

cardtitle_style.alignment = TA_CENTER
cardtitle_style.leading = 6

cardsmall_style = copy(base_style['Normal'])
"The style used for most of the text on the score cards"

cardsmall_style.fontSize = 6
cardsmall_style.leading = 7

cardinfo_style = copy(base_style['Italic'])
"The style used for the additional info on the score cards"

cardinfo_style.alignment = TA_CENTER

badgename_style = copy(cardinfo_style)
"The style used for the player name on the badges"

badgename_style.fontName = BOLD_ITALIC_FONT_NAME
badgename_style.fontSize = 12
badgename_style.leading = 13

cardname_style = copy(badgename_style)
"The style used for the player name on the score cards"

cardname_style.fontSize = 9
cardname_style.leading = 10

rank_width = 0.8*cm
"The width of the `rank` columns"

scores_width = 1.3*cm
"The width of the `scores` columns"

prizes_width = 2*cm
"The width of the `prizes` columns"


def reduce_fontsize_to_fit_width(text, maxwidth, *styles):
    """Reduce the font size of the given styles to fit a max width.

    :param text: the string of text
    :param maxwidth: maximum width that can be used
    :param styles: the list of styles that should be adapted
    :returns: a list of (copies of) the styles with the adapted font size
    """

    from reportlab.pdfbase.pdfmetrics import stringWidth

    copies = styles
    mainstyle = styles[0]

    while stringWidth(text, mainstyle.fontName, mainstyle.fontSize) > maxwidth:
        if mainstyle is styles[0]: # pragma: no cover
            copies = [copy(style) for style in styles]
            mainstyle = copies[0]

        for style in copies:
            style.fontSize -= 1
            style.leading = style.fontSize * 1.1

    return copies


def ordinal(num, _ordinals=[None, _('the first'), _('the second'), _('the third'),
                            _('the fourth'), _('the fifth'), _('the sixth'), _('the seventh'),
                            _('the eighth'), _('the nineth'), _('the tenth'),
                            _('the eleventh'), _('the twelfth'), _('the thirdteenth'),
                            _('the fourteenth'), _('the fifteenth'), _('the sixteenth')]):
    return gettext(_ordinals[num]) if 0 < num < len(_ordinals) else str(num)


def ordinalp(num, _ordinals=[None, _('of the first'), _('of the second'), _('of the third'),
                             _('of the fourth'), _('of the fifth'), _('of the sixth'),
                             _('of the seventh'), _('of the eighth'), _('of the nineth'),
                             _('of the tenth'), _('of the eleventh'), _('of the twelfth'),
                             _('of the thirdteenth'), _('of the fourteenth'),
                             _('of the fifteenth'), _('of the sixteenth')]):
    return gettext(_ordinals[num]) if 0 < num < len(_ordinals) else str(num)


class BasicPrintout(object):
    """Abstract base class used to implement the printouts.

    This class implements the logic used by most printouts, producing a PDF document in the
    `output` filename.

    The document has a front page with an header, a body splitted into `columns` frames and
    a footer. Succeding pages do not have the header frame.
    """

    leftMargin = 1*cm
    "The width of the left margin, by default 1cm"

    rightMargin = 1*cm
    "The width of the right margin, by default 1cm"

    topMargin = 1*cm
    "The width of the top margin, by default 1cm"

    bottomMargin = 1*cm
    "The width of the bottom margin, by default 1cm"

    pagesize = A4
    "The page size, by default A4 in portrait orientation"

    @classmethod
    def getArgumentsFromRequest(klass, session, request):
        """Extract needed arguments for the constructor from the request.

        :param session: the SQLAlchemy session
        :param request: the Pyramid request instance
        :rtype: a sequence of arguments
        """
        # pragma: no cover
        raise NotImplementedError("%s should implement this method!" % klass)

    def __init__(self, output, columns):
        """Initialize the instance.

        :param output: a filename where the PDF will be written
        :param columns: number of columns
        """

        self.output = output
        self.columns = columns
        self.timestamp = datetime.now()

    @property
    def cache_max_age(self):
        "Compute the cache control max age, in seconds."

        return 0

    def createDocument(self):
        """Create the base Platypus document."""

        from pkg_resources import get_distribution
        version = get_distribution('sol').version

        doc = self.doc = BaseDocTemplate(
            self.output, pagesize=self.pagesize, showBoundary=1,
            leftMargin=self.leftMargin, rightMargin=self.rightMargin,
            topMargin=self.topMargin, bottomMargin=self.bottomMargin,
            author='%s %s' % (sol.__package__, version),
            creator="https://bitbucket.org/lele/sol",
            subject=self.__class__.__name__,
            title='%s: %s' % (self.getTitle(), self.getSubTitle()))

        title_height = 3.0*cm
        title_width = doc.width
        if self.lit_url is not None:
            title_width -= title_height
        title_frame = Frame(doc.leftMargin, doc.height + doc.bottomMargin - title_height,
                            title_width, title_height)
        self.title_width = title_width

        fp_frames = [title_frame]
        lp_frames = []

        fwidth = doc.width / self.columns
        fheight = doc.height

        bmargin = doc.bottomMargin
        for f in range(self.columns):
            lmargin = doc.leftMargin + f*fwidth
            fp_frames.append(Frame(lmargin, bmargin, fwidth, fheight-title_height))
            lp_frames.append(Frame(lmargin, bmargin, fwidth, fheight))

        templates = [PageTemplate(frames=fp_frames, id="firstPage",
                                  onPage=self.decoratePage),
                     PageTemplate(frames=lp_frames, id="laterPages",
                                  onPage=self.decoratePage)]
        doc.addPageTemplates(templates)

    def getLeftHeader(self):
        "The top left text."

        raise NotImplementedError("%s should implement this method!"
                                  % self.__class__)

    def getRightHeader(self):
        "The top right text."

        raise NotImplementedError("%s should implement this method!"
                                  % self.__class__)

    def getCenterHeader(self):
        "The top center text."
        # pragma: no cover
        raise NotImplementedError("%s should implement this method!"
                                  % self.__class__)

    def getTitle(self):
        "The title of the document."

        raise NotImplementedError("%s should implement this method!"
                                  % self.__class__)

    def getSubTitle(self):
        "The subtitle of the document."

        raise NotImplementedError("%s should implement this method!"
                                  % self.__class__)

    def getLeftFooter(self):
        "The bottom left text, SoL description and version by default."

        from pkg_resources import get_distribution

        dist = get_distribution('sol')
        description = dist.project_name
        version = dist.version

        return '%s %s %s' % (description, gettext('version'), version)

    def getRightFooter(self):
        "The bottom right text, current time by default."

        # TRANSLATORS: this is a Python strftime() format, see
        # http://docs.python.org/3/library/time.html#time.strftime
        return self.timestamp.strftime(str(gettext('%m-%d-%Y %I:%M %p')))

    def getCenterFooter(self):
        "The bottom center text, current page number by default."

        if self.doc.page > 1:
            return self.getSubTitle() + ', ' + gettext('page %d') % self.doc.page
        else:
            return gettext('page %d') % self.doc.page

    def decoratePage(self, canvas, doc):
        "Add standard decorations to the current page."

        canvas.saveState()
        canvas.setFont(BASE_FONT_NAME, 6)
        w, h = doc.pagesize
        hh = doc.bottomMargin + doc.height + doc.topMargin/2
        hl = doc.leftMargin
        hc = doc.leftMargin + doc.width/2.0
        hr = doc.leftMargin + doc.width
        canvas.drawString(hl, hh, self.getLeftHeader())
        canvas.drawCentredString(hc, hh, self.getCenterHeader())
        canvas.drawRightString(hr, hh, self.getRightHeader())
        fh = doc.bottomMargin/2
        canvas.drawString(hl, fh, self.getLeftFooter())
        canvas.drawCentredString(hc, fh, self.getCenterFooter())
        canvas.drawRightString(hr, fh, self.getRightFooter())

        if doc.page == 1 and self.lit_url is not None:
            qr = QrCodeWidget(self.lit_url)
            bounds = qr.getBounds()
            qrw = bounds[2] - bounds[0]
            qrh = bounds[2] - bounds[1]
            size = 3*cm
            drawing = Drawing(size, size, transform=[size/qrw, 0, 0, size/qrh, 0, 0])
            drawing.add(qr)
            renderPDF.draw(drawing, canvas,
                           w - doc.leftMargin - size,
                           h - doc.topMargin - size)

        canvas.restoreState()

    def execute(self, request):
        """Create and build the document.

        :param request: the Pyramid request instance
        """

        self.lit_url = self.getLitURL(request)
        self.createDocument()
        self.doc.build(list(self.getElements()))

    def getElements(self):
        "Return a list or an iterator of all the elements."

        raise NotImplementedError("%s should implement this method!"
                                  % self.__class__)

    def getLitURL(self, request):
        """Compute the Lit URL for this printout, if any.

        :param request: the Pyramid request instance
        """

        return None


class TourneyPrintout(BasicPrintout):
    "Basic tourney printout, to be further specialized."

    @classmethod
    def getArgumentsFromRequest(klass, session, request):
        t = translator(request)

        id = request.matchdict['id']
        try:
            idtourney = int(id)
        except ValueError:
            try:
                entity = session.query(Tourney).filter_by(guid=id).one()
            except NoResultFound:
                raise OperationAborted(t(_('Bad tourney id: $id',
                                           mapping=dict(id=repr(id)))))
        else:
            entity = session.query(Tourney).get(idtourney)
            if entity is None:
                raise OperationAborted(t(_('Bad tourney id: $id',
                                           mapping=dict(id=str(idtourney)))))

        return [entity]

    def __init__(self, output, tourney, columns):
        super(TourneyPrintout, self).__init__(output, columns)
        self.tourney = tourney

    @property
    def cache_max_age(self):
        "Cache for one year prized tourneys, no cache otherwise."

        if self.tourney.prized:
            return 60*60*24*365
        else:
            return 0

    def getLeftHeader(self):
        "Return championship description."

        return self.tourney.championship.description

    def getRightHeader(self):
        "Return championship's club description."

        return self.tourney.championship.club.description

    def getCenterHeader(self):
        "Return location and date of the event."

        # TRANSLATORS: this is a Python strftime() format, see
        # http://docs.python.org/3/library/time.html#time.strftime
        dateformat = gettext('%m-%d-%Y')

        if self.tourney.location:
            return gettext('%(location)s, %(date)s') % dict(
                location=self.tourney.location ,
                date=self.tourney.date.strftime(dateformat))
        else:
            return self.tourney.date.strftime(dateformat)

    def getTitle(self):
        "Return tourney description."

        return self.tourney.description

    def getElements(self):
        "Yield basic elements for the title frame in the first page."

        title = self.getTitle()
        tstyle, ststyle = reduce_fontsize_to_fit_width(title, self.title_width - 1*cm,
                                                       title_style, subtitle_style)

        yield Paragraph(title, tstyle)
        yield Paragraph(self.getSubTitle(), ststyle)
        yield FrameBreak()
        yield NextPageTemplate('laterPages')


class Participants(TourneyPrintout):
    "List of partecipants of a tourney."

    def __init__(self, output, tourney):
        super(Participants, self).__init__(
            output, tourney, len(tourney.competitors)<35 and 1 or 2)

    def getSubTitle(self):
        num = len(self.tourney.competitors)
        return ngettext('$num Participant', '$num Partecipants', num,
                        mapping=dict(num=num))

    def getElements(self):
        from gettext import translation
        from os.path import join
        from pycountry import LOCALES_DIR, countries
        from pyramid.threadlocal import get_current_request

        request = get_current_request()

        lname = request.locale_name
        try:
            t = translation('iso3166', LOCALES_DIR, languages=[lname]).gettext
        except IOError:
            t = lambda x: x

        yield from super(Participants, self).getElements()

        nsummary = {}
        for c in self.tourney.competitors:
            ncomps = nsummary.setdefault(c.player1Nationality, [])
            description = c.description
            if self.tourney.idrating:
                description += ' (%d)' % c.rate
            ncomps.append(description)

        if not nsummary:
            return

        style = TableStyle([('SIZE', (0,0), (0,-1), normal_style.fontSize),
                            ('LEADING', (0,0), (0,-1), normal_style.leading),
                            ('ALIGN', (0,0), (0,-1), 'RIGHT'),
                            ('VALIGN', (0,0), (-1,-1), 'MIDDLE')])

        nations = list(nsummary.items())
        if len(nations) > 1:
            nations.sort(key=lambda n: -len(n[1]))

            rows = []
            for ccode, comps in nations:
                if ccode:
                    flag = join(self.flags, ccode+'.png')
                    country = t(countries.get(alpha3=ccode).name)
                    caption = ngettext('$country: $num competitor',
                                       '$country: $num competitors',
                                       len(comps),
                                       mapping=dict(country=country,
                                                    num=len(comps)))
                    rows.append((Image(flag), Paragraph(caption, normal_style)))
                else:
                    rows.append(('', Paragraph(gettext('Unspecified country'),
                                               normal_style)))
                rnum = len(rows)-1
                if rnum > 1:
                    style.add('TOPPADDING', (0,rnum), (-1,rnum), 15)
                style.add('FONT', (0,rnum), (-1,rnum), 'Times-Bold')

                rows.extend((i, Paragraph(c, normal_style))
                            for i, c in enumerate(sorted(comps), 1))
        else:
            rows = [(i, Paragraph(c, normal_style))
                    for i, c in enumerate(nations[0][1], 1)]

        desc_width = self.doc.width/self.columns*0.9 - rank_width
        yield Table(rows, (rank_width, desc_width), style=style)


class Ranking(TourneyPrintout):
    "Current ranking of a tourney."

    leftMargin=0.1*cm
    rightMargin=0.1*cm

    @classmethod
    def getArgumentsFromRequest(klass, session, request):
        t = translator(request)
        kw = request.params
        args = super().getArgumentsFromRequest(session, request)
        args.append(getattr(request, '_LOCALE_', 'en'))
        if 'turn' in kw:
            try:
                args.append(int(kw['turn']))
            except ValueError:
                raise OperationAborted(
                    t(_('Invalid turn: $turn',
                        mapping=dict(turn=repr(kw['turn'])))))
        return args

    def __init__(self, output, tourney, locale, turn=None):
        super(Ranking, self).__init__(output, tourney, 1)
        self.locale = locale
        self.turn = turn

    def getLitURL(self, request):
        if (date.today() - self.tourney.date) > timedelta(days=3):
            return None
        elif not request.host.startswith('localhost'):
            return request.route_url('lit_tourney', guid=self.tourney.guid)

    def getSubTitle(self):
        if self.turn is not None:
            return gettext('Ranking after %s round') % ordinal(self.turn)
        else:
            if self.tourney.prized:
                return gettext('Final ranking')
            else:
                rt = self.tourney.rankedturn
                if rt:
                    return gettext('Ranking after %s round') % ordinal(rt)
                else:
                    return gettext('Initial ranking')

    def getFinalElements(self):
        from collections import defaultdict

        finalmatches = [m for m in self.tourney.matches if m.final]
        results = defaultdict(list)
        order = []

        for match in finalmatches:
            caption = gettext('$comp1 vs. $comp2', mapping=dict(
                comp1=match.competitor1, comp2=match.competitor2))
            if caption not in results:
                order.append(caption)
            results[caption].append('%d/%d' % (match.score1, match.score2))

        for i, caption in enumerate(order):
            if i == 0:
                yield Paragraph(ngettext('Result of the final for the 1st/2nd place',
                                         'Results of the final for the 1st/2nd place',
                                         len(results[caption])), heading_style)
            else:
                yield Paragraph(ngettext('Result of the final for the 3rd/4th place',
                                         'Results of the final for the 3rd/4th place',
                                         len(results[caption])), heading_style)
            yield Paragraph(caption, cardname_style)
            yield Paragraph(', '.join(results[caption]), cardinfo_style)
            yield Spacer(0, 0.6*cm)

    def getElements(self):
        yield from super(Ranking, self).getElements()

        def player_caption(player, html, localized):
            caption = player.caption(html=html, localized=localized)
            if player.club:
                caption += "<font size=6> %s</font>" % player.club
            return caption

        if self.tourney.championship.prizes in ('asis', 'fixed', 'fixed40', 'millesimal'):
            def format_prize(p):
                return '%d' % p
        else:
            def format_prize(p):
                return format_decimal(p, '###0.00', self.locale)

        if self.turn is not None:
            ranking = [(i, c.caption(player_caption=player_caption), c.nationality,
                        r.points, r.bucholz, r.netscore, 0)
                       for i, (c, r) in enumerate(self.tourney.computeRanking(self.turn), 1)]
        else:
            ranking = [(i, c.caption(player_caption=player_caption), c.nationality,
                        c.points, c.bucholz, c.netscore, format_prize(c.prize))
                       for i, c in enumerate(self.tourney.ranking, 1)]

            if self.tourney.finals and self.tourney.prized:
                yield from self.getFinalElements()

        if not ranking: # pragma: no cover
            return

        is_intl = len(set(r[2] for r in ranking)) > 1

        if self.tourney.championship.playersperteam > 1:
            caption = gettext('Team')
        else:
            caption = gettext('Player')

        if self.tourney.prized and self.turn is None:
            if self.tourney.championship.prizes == 'asis':
                npointcols = 3
                rows = [('#',
                         '',
                         caption,
                         gettext('Pts'),
                         gettext('Bch'),
                         gettext('Net')) if is_intl
                        else ('#',
                              caption,
                              gettext('Pts'),
                              gettext('Bch'),
                              gettext('Net'))]
                rows.extend((rank,
                             country,
                             Paragraph(description, normal_style),
                             points,
                             bucholz,
                             netscore) if is_intl
                            else (rank,
                                  Paragraph(description, normal_style),
                                  points,
                                  bucholz,
                                  netscore)
                            for (rank, description, country,
                                 points, bucholz, netscore, prize) in ranking)
                desc_width = (self.doc.width - rank_width - scores_width*4 -
                              (scores_width if is_intl else 0))
                widths = (
                    rank_width, scores_width, desc_width,
                    scores_width, scores_width,
                    scores_width
                ) if is_intl else (
                    rank_width, desc_width,
                    scores_width, scores_width,
                    scores_width)
            else:
                npointcols = 4
                rows = [('#',
                         '',
                         caption,
                         gettext('Pts'),
                         gettext('Bch'),
                         gettext('Net'),
                         gettext('Prz')) if is_intl
                        else ('#',
                              caption,
                              gettext('Pts'),
                              gettext('Bch'),
                              gettext('Net'),
                              gettext('Prz'))]
                rows.extend((rank,
                             country,
                             Paragraph(description, normal_style),
                             points,
                             bucholz,
                             netscore,
                             prize) if is_intl
                            else (rank,
                                  Paragraph(description, normal_style),
                                  points,
                                  bucholz,
                                  netscore,
                                  prize)
                            for (rank, description, country,
                                 points, bucholz, netscore, prize) in ranking)
                desc_width = (self.doc.width - rank_width - scores_width*4 - prizes_width -
                              (scores_width if is_intl else 0))
                widths = (
                    rank_width, scores_width, desc_width,
                    scores_width, scores_width,
                    scores_width, prizes_width
                ) if is_intl else (
                    rank_width, desc_width,
                    scores_width, scores_width,
                    scores_width, prizes_width)

            yield Table(rows, widths,
                        style=TableStyle([('ALIGN', (0,0), (0,-1), 'RIGHT'),
                                          ('ALIGN', (-npointcols,0), (-1,-1), 'RIGHT'),
                                          ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                                          ('FONT', (0,0), (-1,0), caption_style.fontName),
                                          ('SIZE', (0,0), (-1,0), caption_style.fontSize),
                                          ('LEADING', (0,0), (-1,0), caption_style.leading),
                                          ('SIZE', (0,1), (0,-1), normal_style.fontSize),
                                          ('LEADING', (0,1), (0,-1), normal_style.leading),
                                          ('SIZE', (-npointcols,1), (-1,-1), normal_style.fontSize),
                                          ('LEADING', (-npointcols,1), (-1,-1), normal_style.leading),
                                          ('LINEBELOW', (0,1), (-1,-1), 0.25, colors.black)]))
        else:
            rows = [('#',
                     '',
                     caption,
                     gettext('Pts'),
                     gettext('Bch'),
                     gettext('Net')) if is_intl
                    else ('#',
                          caption,
                          gettext('Pts'),
                          gettext('Bch'),
                          gettext('Net'))]
            rows.extend([(rank,
                          country,
                          Paragraph(description, normal_style),
                          points,
                          bucholz,
                          netscore) if is_intl
                         else (rank,
                               Paragraph(description, normal_style),
                               points,
                               bucholz,
                               netscore)
                         for (rank, description, country, points,
                              bucholz, netscore, prize) in ranking])
            desc_width = (self.doc.width/self.columns*0.9 - rank_width -
                          scores_width*3 -
                          (scores_width if is_intl else 0))
            yield Table(rows,
                        (rank_width, scores_width, desc_width,
                         scores_width, scores_width, scores_width) if is_intl
                        else (rank_width, desc_width,
                              scores_width, scores_width, scores_width),
                        style=TableStyle([('ALIGN', (0,0), (0,-1), 'RIGHT'),
                                          ('ALIGN', (-3,0), (-1,-1), 'RIGHT'),
                                          ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                                          ('FONT', (0,0), (-1,0), caption_style.fontName),
                                          ('SIZE', (0,0), (-1,0), caption_style.fontSize),
                                          ('LEADING', (0,0), (-1,0), caption_style.leading),
                                          ('SIZE', (0,1), (0,-1), normal_style.fontSize),
                                          ('LEADING', (0,1), (0,-1), normal_style.leading),
                                          ('SIZE', (-3,1), (-1,-1), normal_style.fontSize),
                                          ('LEADING', (-3,1), (-1,-1), normal_style.leading),
                                          ('LINEBELOW', (0,1), (-1,-1), 0.25, colors.black)]))


class NationalRanking(TourneyPrintout):
    "Current ranking of a tourney by nationality."

    @classmethod
    def getArgumentsFromRequest(klass, session, request):
        t = translator(request)
        kw = request.params
        args = super().getArgumentsFromRequest(session, request)
        if 'turn' in kw:
            try:
                args.append(int(kw['turn']))
            except ValueError:
                raise OperationAborted(
                    t(_('Invalid turn: $turn',
                        mapping=dict(turn=repr(kw['turn'])))))
        return args

    def __init__(self, output, tourney, turn=None):
        super(NationalRanking, self).__init__(output, tourney, 1)
        self.turn = turn

    def getSubTitle(self):
        if self.turn is not None:
            return gettext('Ranking by nationality after %s round') % ordinal(self.turn)
        else:
            if self.tourney.prized:
                return gettext('Final ranking by nationality')
            else:
                rt = self.tourney.rankedturn
                if rt:
                    return gettext('Ranking by nationality after %s round') % ordinal(rt)
                else:
                    return gettext('Initial ranking by nationality')

    def getElements(self):
        from gettext import translation
        from operator import itemgetter
        from os.path import join
        from pycountry import LOCALES_DIR, countries
        from pyramid.threadlocal import get_current_request

        request = get_current_request()

        lname = request.locale_name
        try:
            t = translation('iso3166', LOCALES_DIR, languages=[lname]).gettext
        except IOError:
            t = lambda x: x

        yield from super(NationalRanking, self).getElements()

        if self.turn is not None:
            ranking = [(i, c.description, c.player1Nationality,
                        r.points, r.bucholz, r.netscore, 0)
                       for i, (c, r) in enumerate(self.tourney.computeRanking(self.turn), 1)]
        else:
            ranking = [(i, c.description, c.player1Nationality,
                        c.points, c.bucholz, c.netscore, c.prize)
                       for i, c in enumerate(self.tourney.ranking, 1)]

        if not ranking:
            return

        nsummary = {}
        for r in ranking:
            sum = nsummary.get(r[2], [0, 0, 0, 0, 0])
            sum[0] += r[6]
            sum[1] += r[3]
            sum[2] += r[4]
            sum[3] += r[5]
            sum[4] += 1
            nsummary[r[2]] = sum

        nations = list(nsummary.items())
        nations.sort(key=itemgetter(1))
        nations.reverse()

        if self.tourney.championship.playersperteam > 1:
            caption = gettext('Team')
        else:
            caption = gettext('Player')

        if self.tourney.prized:
            style = TableStyle([('ALIGN', (0,1), (0,-1), 'RIGHT'),
                                ('ALIGN', (-4,0), (-1,-1), 'RIGHT'),
                                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                                ('FONT', (0,0), (-1,0), caption_style.fontName),
                                ('SIZE', (0,0), (-1,0), caption_style.fontSize),
                                ('LEADING', (0,0), (-1,0), caption_style.leading),
                                ('SIZE', (0,1), (-1,-1), normal_style.fontSize),
                                ('LEADING', (0,1), (-1,-1), normal_style.leading),
                                ('LINEBELOW', (0,1), (-1,-1), 0.25, colors.black)])
            rows = [('#',
                     caption,
                     gettext('Pts'),
                     gettext('Bch'),
                     gettext('Net'),
                     gettext('Prz'))]
            for n in nations:
                if n[0]:
                    flag = join(self.flags, n[0]+'.png')
                    country = t(countries.get(alpha3=n[0]).name)
                    caption = ngettext('$country: $num competitor',
                                       '$country: $num competitors',
                                       n[1][4],
                                       mapping=dict(country=country,
                                                    num=n[1][4]))
                    rows.append((Image(flag), Paragraph(caption, normal_style),
                                 n[1][1], n[1][2], n[1][3], n[1][0]))
                else:
                    rows.append(('', Paragraph(gettext('Unspecified country'), normal_style),
                                 n[1][1], n[1][2], n[1][3], n[1][0]))
                rnum = len(rows)-1
                if rnum > 1:
                    style.add('LINEABOVE', (0, rnum), (-1, rnum), 1, colors.black)
                    style.add('TOPPADDING', (0,rnum), (-1,rnum), 15)
                style.add('FONT', (0,rnum), (-1,rnum), 'Times-Bold')
                rows.extend([(rank,
                              Paragraph(description, normal_style),
                              points,
                              bucholz,
                              netscore,
                              prize)
                             for (rank, description, nationality, points,
                                  bucholz, netscore, prize) in ranking
                             if nationality==n[0]])
            desc_width = (self.doc.width/self.columns*0.9 - rank_width
                          - scores_width*4 - prizes_width)
            yield Table(rows, (rank_width, desc_width,
                               scores_width, scores_width,
                               scores_width, prizes_width),
                        style=style)
        else:
            style = TableStyle([('ALIGN', (0,1), (0,-1), 'RIGHT'),
                                ('ALIGN', (-3,0), (-1,-1), 'RIGHT'),
                                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                                ('FONT', (0,0), (-1,0), caption_style.fontName),
                                ('SIZE', (0,0), (-1,0), caption_style.fontSize),
                                ('LEADING', (0,0), (-1,0), caption_style.leading),
                                ('SIZE', (0,1), (-1,-1), normal_style.fontSize),
                                ('LEADING', (0,1), (-1,-1), normal_style.leading),
                                ('LINEBELOW', (0,1), (-1,-1), 0.25, colors.black)])
            rows = [('#',
                     caption,
                     gettext('Pts'),
                     gettext('Bch'),
                     gettext('Net'))]

            for n in nations:
                if n[0]:
                    flag = join(self.flags, n[0]+'.png')
                    country = t(countries.get(alpha3=n[0]).name)
                    caption = ngettext('$country: $num competitor',
                                       '$country: $num competitors',
                                       n[1][4],
                                       mapping=dict(country=country,
                                                    num=n[1][4]))
                    rows.append((Image(flag), Paragraph(caption, normal_style),
                                 n[1][1], n[1][2], n[1][3]))
                else:
                    rows.append(('', Paragraph(gettext('Unspecified country'), normal_style),
                                 n[1][1], n[1][2], n[1][3]))
                rnum = len(rows)-1
                if rnum > 1:
                    style.add('LINEABOVE', (0, rnum), (-1, rnum), 1, colors.black)
                style.add('FONT', (0,rnum), (-1,rnum), 'Times-Bold')
                rows.extend([(rank,
                              Paragraph(description, normal_style),
                              points,
                              bucholz,
                              netscore)
                             for (rank, description, nationality, points,
                                  bucholz, netscore, prize) in ranking
                             if nationality==n[0]])

            desc_width = self.doc.width/self.columns*0.9 - rank_width - scores_width*3
            yield Table(rows, (rank_width, desc_width,
                               scores_width, scores_width, scores_width),
                        style=style)


class Results(TourneyPrintout):
    "Results of the last turn."

    @classmethod
    def getArgumentsFromRequest(klass, session, request):
        t = translator(request)
        kw = request.params
        args = super().getArgumentsFromRequest(session, request)
        if 'turn' in kw:
            if kw['turn'] == 'all':
                args.append(None)
            else:
                try:
                    args.append(int(kw['turn']))
                except ValueError:
                    raise OperationAborted(
                        t(_('Invalid turn: $turn',
                            mapping=dict(turn=repr(kw['turn'])))))
        else:
            args.append(args[0].rankedturn)

        return args

    def __init__(self, output, tourney, turn):
        super(Results, self).__init__(output, tourney, 1)
        self.turn = turn

    def getLitURL(self, request):
        if (date.today() - self.tourney.date) > timedelta(days=3):
            return None
        elif not request.host.startswith('localhost') and self.turn:
            return request.route_url('lit_tourney', guid=self.tourney.guid,
                                     _query=dict(turn=self.turn))

    def getSubTitle(self):
        if self.turn:
            if [m.final for m in self.tourney.matches if m.turn == self.turn][0]:
                return gettext('Results %s final round') % ordinalp(self.turn)
            else:
                return gettext('Results %s round') % ordinalp(self.turn)
        else:
            return gettext('All results')

    def getElements(self):
        yield from super(Results, self).getElements()

        turn = self.turn

        results = [(m.turn, m.board, m.description, m.score1, m.score2, m.final)
                   for m in self.tourney.matches
                   if not turn or m.turn == turn]
        if not results:
            return

        results.sort()

        if turn:
            yield from self.getSingleTurnElements(results)
        else:
            yield from self.getAllTurnElements(results)

    def getSingleTurnElements(self, results):
        from reportlab.pdfbase.pdfmetrics import stringWidth

        slash_w = stringWidth('/', normal_style.fontName, normal_style.fontSize)

        rows = [(gettext('#'), gettext('Match'), '', gettext('Result'), '')]

        rows.extend([(board,
                      Paragraph(description, normal_style),
                      str(score1), '/', str(score2))
                     for (turn, board, description, score1, score2, final) in results])

        desc_width = self.doc.width/self.columns*0.9 - rank_width - scores_width*2 - slash_w
        yield Table(rows, (rank_width, desc_width, scores_width, slash_w, scores_width),
                    style=TableStyle([('ALIGN', (0,1), (0,-1), 'RIGHT'),
                                      ('ALIGN', (-3,0), (-3,-1), 'RIGHT'),
                                      ('ALIGN', (-2,0), (-2,-1), 'CENTER'),
                                      ('ALIGN', (-1,0), (-1,-1), 'RIGHT'),
                                      ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                                      ('FONT', (0,0), (-1,0), caption_style.fontName),
                                      ('SIZE', (0,0), (-1,0), caption_style.fontSize),
                                      ('LEADING', (0,0), (-1,0), caption_style.leading),
                                      ('SIZE', (0,1), (-1,-1), normal_style.fontSize),
                                      ('LEADING', (0,1), (-1,-1), normal_style.leading),
                                      ('LINEBELOW', (0,0), (-1,-1), 0.25, colors.black)]))

    def getAllTurnElements(self, results):
        from itertools import groupby
        from operator import itemgetter

        key = itemgetter(0)
        for turn, res in groupby(results, key):
            yield CondPageBreak(4*cm)
            res = list(res)
            if res[0][5]:
                title = Paragraph(gettext('Results %s final round') % ordinalp(turn),
                                  heading_style)
            else:
                title = Paragraph(gettext('Results %s round') % ordinalp(turn), heading_style)
            yield title
            yield from self.getSingleTurnElements(res)
            yield Spacer(0, 0.4*cm)


class Matches(TourneyPrintout):
    "Next turn matches."

    def __init__(self, output, tourney):
        super(Matches, self).__init__(output, tourney, 1)

    def getSubTitle(self):
        if self.tourney.finalturns:
            return gettext('Matches %s final round') % ordinalp(self.tourney.currentturn)
        else:
            return gettext('Matches %s round') % ordinalp(self.tourney.currentturn)

    def getElements(self):
        yield from super(Matches, self).getElements()

        currentturn = self.tourney.currentturn
        turn = [(m.board, m.description)
                for m in self.tourney.matches
                if m.turn==currentturn]
        if not turn:
            return

        turn.sort()
        rows = [(gettext('#'),
                 gettext('Match'))]
        rows.extend([(board,
                      Paragraph(description, normal_style))
                     for (board, description) in turn])

        desc_width = self.doc.width/self.columns*0.9 - rank_width
        yield Table(rows, (rank_width, desc_width),
                    style=TableStyle([('ALIGN', (0,1), (0,-1), 'RIGHT'),
                                      ('ALIGN', (-2,1), (-1,-1), 'RIGHT'),
                                      ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                                      ('FONT', (0,0), (-1,0), caption_style.fontName),
                                      ('SIZE', (0,0), (-1,0), caption_style.fontSize),
                                      ('LEADING', (0,0), (-1,0), caption_style.leading),
                                      ('SIZE', (0,1), (-1,-1), normal_style.fontSize),
                                      ('LEADING', (0,1), (-1,-1), normal_style.leading),
                                      ('LINEBELOW', (0,0), (-1,-1), 0.25, colors.black)]))


class ScoreCards(TourneyPrintout):
    "Score cards, where match results are written by the competitors."

    @classmethod
    def getArgumentsFromRequest(klass, session, request):
        if request.matchdict['id'] != 'blank':
            return super().getArgumentsFromRequest(session, request)
        else:
            return [None]

    def __init__(self, output, tourney, columns=2):
        super(ScoreCards, self).__init__(output, tourney, columns)

    @property
    def cache_max_age(self):
        "Cache for one year blank score cards, no cache otherwise."

        if self.tourney is None:
            return 60*60*24*365
        else:
            return 0

    def createDocument(self):
        from pkg_resources import get_distribution

        if self.tourney is not None:
            if not self.tourney.prized:
                title = gettext('Score cards for %s round') % ordinal(self.tourney.currentturn)
            else:
                title = gettext('Finals score cards')
        else:
            title = gettext('Score cards')

        dist = get_distribution('sol')
        description = dist.project_name
        version = dist.version

        doc = self.doc = BaseDocTemplate(
            self.output, pagesize=A4, showBoundary=0,
            leftMargin=0.5*cm, rightMargin=0.5*cm,
            topMargin=0.5*cm, bottomMargin=0.5*cm,
            author='%s %s' % (description, version),
            creator="https://bitbucket.org/lele/sol",
            subject=self.__class__.__name__,
            title=title)

        lp_frames = []

        fwidth = doc.width / self.columns
        fheight = doc.height

        bmargin = doc.bottomMargin
        for f in range(self.columns):
            lmargin = doc.leftMargin + f*fwidth
            lp_frames.append(Frame(lmargin, bmargin, fwidth, fheight))

        templates = [PageTemplate(frames=lp_frames, onPage=self.decoratePage)]
        doc.addPageTemplates(templates)

    def decoratePage(self, canvas, doc):
        "Add crop-marks to the page."

        line = canvas.line
        for iy in range(0, 4):
            y = doc.bottomMargin + iy * (doc.height/3)
            for ix in range(0, 3):
                x = doc.leftMargin + ix * (doc.width/2)
                line(x-5, y, x+5, y)
                line(x, y-5, x, y+5)

    def getElements(self):
        if self.tourney is not None:
            currentturn = self.tourney.currentturn
            boards = [(m.board, m.competitor1.description, m.competitor2.description,
                       m.final)
                      for m in self.tourney.matches
                      if m.turn==currentturn and m.idcompetitor2]
        else:
            # Six blank score cards
            boards = [(i, '', '') for i in range(1, 7)]

        if not boards:
            return
        boards.sort()

        data = [[gettext('Points'),
                 '',
                 gettext('Score'),
                 gettext('Coins'),
                 gettext('Queen'),
                 '',
                 '',
                 gettext('Coins'),
                 gettext('Score'),
                 '',
                 gettext('Points')]]

        for i in range(9):
            data.append(['', '', '', '', '', i+1, '', '', '', '', ''])

        sw = self.doc.width/self.columns*0.95 / 23
        ssw = sw/2
        qw = sw*2
        nw = sw*3
        table_widths = (nw, ssw, nw, nw, qw, ssw, qw, nw, nw, ssw, nw)
        table_style = TableStyle([('GRID', (0,1), (0,9), 1.0, colors.black),
                                  ('GRID', (-1,1), (-1,9), 1.0, colors.black),
                                  ('GRID', (2,1), (-3,9), 0.5, colors.black),
                                  ('ALIGN', (0,0), (-1,0), 'CENTER'),
                                  ('SIZE', (0,0), (-1,0), 8),
                                  ('ALIGN', (5,1), (5,-1), 'CENTER'),
                                  ('BACKGROUND', (5,1), (5,-2), colors.lightgrey),
                                  ('SIZE', (5,1), (5,-1), 8),
                                  ('SPAN', (4,0), (6,0)),
                                  ('ALIGN', (0,10), (-1,10), 'CENTER'),
                                  ('SIZE', (0,10), (-1,10), 8),
                                  ('BOX', (0,11), (0,11), 2.0, colors.black),
                                  ('BOX', (-1,11), (-1,11), 2.0, colors.black),
                                  ('ALIGN', (0,12), (-1,12), 'CENTER'),
                                  ('SIZE', (0,12), (-1,12), 8),
                                  ('BOX', (0,13), (0,13), 0.5, colors.black),
                                  ('BOX', (-1,13), (-1,13), 0.5, colors.black),
                                  ('SPAN', (1,10), (4,12)),
                                  ('SPAN', (6,10), (-2,12)),
                                  ('VALIGN', (0,10), (-1,13), 'MIDDLE'),
                                  ('SPAN', (1,-1), (-2,-1))
                                  ])

        if self.tourney is not None:
            now = datetime.now()
            start = now + timedelta(minutes=9, seconds=45)
            start += timedelta(minutes=5-start.minute%5)
            end = start + timedelta(minutes=self.tourney.duration)
            # TRANSLATORS: this is strftime() format, see
            # http://docs.python.org/3/library/time.html#time.strftime
            time_format = gettext('%I:%M %p')
            estimated_start = start.strftime(time_format)
            estimated_end = end.strftime(time_format)

            if not self.tourney.prized:
                boardno_format = '%s<br/><font size=6>%s</font>' % (
                    gettext('Round %(turn)d — Board %(board)d'),
                    gettext('estimated start %(start)s — end %(end)s'))

        for i, board in enumerate(boards):
            boardno = ['']
            if self.tourney is not None:
                if self.tourney.prized or board[3]:
                    if board[1] == self.tourney.ranking[0].description:
                        caption = gettext('1st/2nd place final')
                    else:
                        caption = gettext('3rd/4th place final')
                    if self.tourney.finalkind == 'bestof3':
                        finalmatches = [m for m in self.tourney.matches if m.final]
                        nfinalturns = len(set(m.turn for m in finalmatches))
                        caption += ' (%d/3)' % nfinalturns
                    boardno.append(Paragraph(caption, cardtitle_style))
                else:
                    boardno.append(Paragraph(boardno_format % dict(turn=currentturn,
                                                                   board=board[0],
                                                                   start=estimated_start,
                                                                   end=estimated_end),
                                             cardtitle_style))
            else:
                boardno.append('')
            boardno.extend(['']*9)
            names = [[gettext('Total'),
                      Paragraph(board[1], cardname_style),
                      '', '', '', '',
                      Paragraph(board[2], cardname_style),
                      '', '', '',
                      gettext('Total')],
                     ['']*11,
                     [gettext('Break')]+['']*9+[gettext('Break')],
                     boardno]
            table = Table(data+names, table_widths, style=table_style)
            if i == 0 or (i+1) % 3:
                yield KeepTogether([table, Spacer(0, 0.6*cm)])
            else:
                yield table
                yield FrameBreak()


class Badges(object):
    "Personal badges."

    emblems = '.'
    height = 5.4*cm
    width = 8.5*cm
    bottom_margin = 1*cm
    left_margin = 2*cm

    @classmethod
    def getArgumentsFromRequest(klass, session, request):
        t = translator(request)

        id = request.matchdict['id']
        try:
            idtourney = int(id)
        except ValueError:
            try:
                entity = session.query(Tourney).filter_by(guid=id).one()
            except NoResultFound:
                raise OperationAborted(t(_('Bad tourney id: $id',
                                           mapping=dict(id=repr(id)))))
        else:
            entity = session.query(Tourney).get(idtourney)
            if entity is None:
                raise OperationAborted(t(_('Bad tourney id: $id',
                                           mapping=dict(id=str(idtourney)))))

        return [entity]

    def __init__(self, output, tourney):
        self.output = output
        self.tourney = tourney

    @property
    def cache_max_age(self):
        "Cache for one year prized tourneys, no cache otherwise."

        if self.tourney.prized:
            return 60*60*24*365
        else:
            return 0

    def getPlayers(self):
        if self.tourney.prized:
            competitors = self.tourney.ranking
        else:
            competitors = self.tourney.competitors
        for r, c in enumerate(competitors):
            for p in (c.player1, c.player2, c.player3, c.player4):
                if p:
                    yield c, p, r+1

    def execute(self, request):
        from pkg_resources import get_distribution

        dist = get_distribution('sol')
        description = dist.project_name
        version = dist.version

        c = self.canvas = canvas.Canvas(self.output)
        c.setAuthor('%s %s' % (description, version))
        c.setSubject(self.__class__.__name__)
        c.setTitle(gettext('Badges'))

        players = self.getPlayers()
        while self.drawOnePage(players):
            c.showPage()

        c.save()

    def drawOnePage(self, players):
        try:
            c, p, r = next(players)
        except StopIteration:
            return False
        first = True

        line = self.canvas.line
        for i in range(0, 6):
            y = self.bottom_margin + i * self.height
            line(5, y, 20, y)
            line(A4[0] - 5, y, A4[0] - 20, y)

        for i in range(0, 3):
            x = self.left_margin + i * self.width
            line(x, 5, x, 20)
            line(x, A4[1] - 5, x, A4[1] - 20)

        self.canvas.translate(self.left_margin, self.bottom_margin)
        for i in range(5):
            if not first:
                try:
                    c, p, r = next(players)
                except StopIteration:
                    return False
            else:
                first = False

            self.drawLeftSide(c, p, r)
            self.canvas.saveState()
            self.canvas.translate(self.width, 0)
            if self.tourney.prized:
                self.drawRightSide(c, p, r)
            else:
                try:
                    c, p, r = next(players)
                except StopIteration:
                    self.canvas.restoreState()
                    return False
                self.drawLeftSide(c, p, r)
            self.canvas.restoreState()
            self.canvas.translate(0, self.height)
        return True

    def drawLeftSide(self, competitor, player, rank=None):
        from os.path import exists, join

        c = self.canvas
        max_text_width = self.width
        center = self.width/2

        if self.tourney.championship.club.emblem:
            image = join(self.emblems, self.tourney.championship.club.emblem)
            if exists(image):
                image_width = self.width/5 * 2
                c.drawImage(image, 0, 0, image_width, self.height,
                            preserveAspectRatio=True)
                max_text_width -= image_width
                center = image_width + max_text_width/2

        style = reduce_fontsize_to_fit_width(self.tourney.description,
                                             max_text_width, cardtitle_style)[0]
        c.setFont(style.fontName, style.fontSize, style.leading)
        c.drawCentredString(center, self.height-1*cm, self.tourney.description)

        style = cardinfo_style
        c.setFont(style.fontName, style.fontSize, style.leading)
        c.drawCentredString(center, self.height-1.6*cm,
                            self.tourney.date.strftime(gettext('%m-%d-%Y')))

        style = reduce_fontsize_to_fit_width(self.tourney.championship.description,
                                             max_text_width, cardinfo_style)[0]
        c.setFont(style.fontName, style.fontSize, style.leading)
        c.drawCentredString(center, self.height-2.2*cm,
                            self.tourney.championship.description)

        if rank and self.tourney.prized:
            style = subtitle_style
            c.setFont(style.fontName, style.fontSize, style.leading)
            c.drawCentredString(center, self.height-3*cm, str(rank))

        caption = player.caption(html=False)
        style = reduce_fontsize_to_fit_width(caption, max_text_width, badgename_style)[0]
        c.setFont(style.fontName, style.fontSize, style.leading)
        c.drawCentredString(center, self.height-3.7*cm, caption)

        style = cardname_style
        c.setFont(style.fontName, style.fontSize, style.leading)

        rating = self.tourney.rating
        if rating is not None:
            rate = rating.getPlayerRating(player).rate
            c.drawCentredString(center, self.height-4.1*cm, str(rate))

        if competitor.player1Nationality:
            from gettext import translation
            from pycountry import LOCALES_DIR, countries
            from pyramid.threadlocal import get_current_request

            request = get_current_request()

            lname = request.locale_name
            try:
                t = translation('iso3166', LOCALES_DIR, languages=[lname]).gettext
            except IOError:
                t = lambda x: x

            country = t(countries.get(alpha3=competitor.player1Nationality).name)
            flag = join(self.flags, competitor.player1Nationality+'.png')
            if exists(flag):
                c.drawRightString(center-0.1*cm, self.height-4.9*cm, country)
                c.drawImage(flag, center+0.1*cm, self.height-5.0*cm)
            else:
                c.drawCentredString(center, self.height-4.8*cm, country)

    def drawRightSide(self, competitor, player, rank=None):
        c = self.canvas

        def e(s, l):
            if c.stringWidth(s) > l:
                l -= c.stringWidth('…')
                while c.stringWidth(s) > l:
                    s = s[:-1]
                s += '…'
            return s

        c.setFont(cardsmall_style.fontName, cardsmall_style.fontSize, cardsmall_style.leading)

        c.drawCentredString(1.8*cm, self.height-1*cm, gettext('You met…'))
        c.drawString(0.3*cm, self.height-1.25*cm, gettext('Opponent'))

        # TRANSLATORS: this is the "score of this player" in the badge
        your = gettext('your')
        c.drawRightString(3.1*cm, self.height-1.25*cm, your)

        # TRANSLATORS: this is the "opponent score" in the badge
        his = gettext('his')
        c.drawRightString(3.4*cm, self.height-1.25*cm, his)

        pmatches = [m for m in self.tourney.matches
                    if m.idcompetitor1 == competitor.idcompetitor
                    or m.idcompetitor2 == competitor.idcompetitor]
        for i, m in enumerate(pmatches):
            if m.idcompetitor1 == competitor.idcompetitor:
                other = m.competitor2
                myscore = m.score1
                otherscore = m.score2
            elif m.idcompetitor2==competitor.idcompetitor:
                other = m.competitor1
                myscore = m.score2
                otherscore = m.score1
            else:
                continue
            h = self.height-1.6*cm-i*0.3*cm
            c.drawString(0.3*cm, h,
                         other and e(other.caption(html=False), 2.4*cm)
                         or gettext('Phantom'))
            c.drawRightString(3.1*cm, h, str(myscore))
            c.drawRightString(3.4*cm, h, str(otherscore))

        c.drawCentredString(6.0*cm, self.height-1*cm,
                            gettext('Final ranking'))
        c.drawString(3.8*cm, self.height-1.25*cm,
                     gettext('Competitor'))
        if self.tourney.championship.prizes == 'asis':
            # TRANSLATORS: this is the points in the badge
            pts = gettext('pts')
            c.drawRightString(7.6*cm, self.height-1.25*cm, pts)
            # TRANSLATORS: this is the bucholz in the badge
            bch = gettext('bch')
            c.drawRightString(8.0*cm, self.height-1.25*cm, bch)
            # TRANSLATORS: this is the net score in the badge
            net = gettext('net')
            c.drawRightString(8.4*cm, self.height-1.25*cm, net)

            for i, ctor in enumerate(self.tourney.ranking):
                if i > 15:
                    break
                h = self.height-1.6*cm-i*0.22*cm
                c.drawRightString(3.8*cm, h, str(i+1))
                c.drawString(3.9*cm, h, e(ctor.caption(html=False), 3.3*cm))
                c.drawRightString(7.6*cm, h, str(ctor.points))
                c.drawRightString(8.0*cm, h, str(ctor.bucholz))
                c.drawRightString(8.4*cm, h, str(ctor.netscore))
        else:
            # TRANSLATORS: this is the points in the badge
            pts = gettext('pts')
            c.drawRightString(6.9*cm, self.height-1.25*cm, pts)
            # TRANSLATORS: this is the bucholz in the badge
            bch = gettext('bch')
            c.drawRightString(7.3*cm, self.height-1.25*cm, bch)
            # TRANSLATORS: this is the net score in the badge
            net = gettext('net')
            c.drawRightString(7.75*cm, self.height-1.25*cm, net)
            # TRANSLATORS: this is the prize in the badge
            prz = gettext('prz')
            c.drawRightString(8.5*cm, self.height-1.25*cm, prz)

            for i, ctor in enumerate(self.tourney.ranking):
                if i > 15:
                    break
                h = self.height-1.6*cm-i*0.22*cm
                c.drawRightString(3.8*cm, h, str(i+1))
                c.drawString(3.9*cm, h, e(ctor.caption(html=False), 2.6*cm))
                c.drawRightString(6.9*cm, h, str(ctor.points))
                c.drawRightString(7.3*cm, h, str(ctor.bucholz))
                c.drawRightString(7.75*cm, h, str(ctor.netscore))
                c.drawRightString(8.5*cm, h, str(ctor.prize))


class ChampionshipRanking(BasicPrintout):
    "Championship ranking."

    @classmethod
    def getArgumentsFromRequest(klass, session, request):
        t = translator(request)

        id = request.matchdict['id']
        try:
            idchampionship = int(id)
        except ValueError:
            try:
                entity = session.query(Championship).filter_by(guid=id).one()
            except NoResultFound:
                raise OperationAborted(t(_('Bad championship id: $id',
                                           mapping=dict(id=repr(id)))))
        else:
            entity = session.query(Championship).get(idchampionship)
            if entity is None:
                raise OperationAborted(t(_('Bad championship id: $id',
                                           mapping=dict(id=str(idchampionship)))))

        return [entity]

    def __init__(self, output, arg):
        super(ChampionshipRanking, self).__init__(output, 1)
        self.setup(arg)

    @property
    def cache_max_age(self):
        "Cache for one year closed championships, no cache otherwise."

        if self.championship.closed:
            return 60*60*24*365
        else:
            return 0

    def setup(self, championship):
        self.championship = championship
        self.dates, self.ranking = championship.ranking()
        if len(self.dates) > 5:
            self.pagesize = landscape(A4)

    def getLeftHeader(self):
        return self.getSubTitle()

    def getRightHeader(self):
        return self.championship.club.description

    def getCenterHeader(self):
        if self.championship.skipworstprizes:
            swp = self.championship.skipworstprizes
            return ngettext('Ignoring %d worst result',
                            'Ignoring %d worst results',
                            swp) % swp
        else:
            return ""

    def getTitle(self):
        return self.championship.description

    def getSubTitle(self):
        howmany = len(self.dates)
        if howmany == 0:
            return gettext('No prized tourneys in the championship')
        else:
            return ngettext('%d tourney', '%d tourneys',
                            howmany) % howmany

    def getElements(self):
        from sol.models.utils import njoin

        title = self.getTitle()
        maxwidth = self.doc.width - 1*cm
        tstyle, ststyle = reduce_fontsize_to_fit_width(title, maxwidth,
                                                       title_style, subtitle_style)

        yield Paragraph(title, tstyle)
        yield Paragraph(self.getSubTitle(), ststyle)
        yield FrameBreak()
        yield NextPageTemplate('laterPages')

        if not self.ranking:
            return

        header = self.createTableHeader()

        style = [('SIZE', (0,0), (-1,-1), caption_style.fontSize),
                 ('LEADING', (0,0), (-1,-1), caption_style.leading),
                 ('FONT', (0,0), (-1,0), caption_style.fontName),
                 ('ALIGN', (0,1), (0,-1), 'RIGHT'),
                 ('ALIGN', (2,1), (-1,-1), 'RIGHT'),
                 ('LINEBELOW', (0,1), (-1,-1), 0.25, colors.black)]
        header.append(gettext('Total'))
        rows = [header]
        for i, c in enumerate(self.ranking):
            row = [i+1]
            row.append(njoin(c[0]))
            for col,s in enumerate(c[2]):
                # If we have the skipped prizes and the current
                # prize is one of those, print it in light gray
                if len(c)>4 and c[4] and s in c[4]:
                    if s:
                        style.append(('TEXTCOLOR',
                                      (col+2, i+1), (col+2, i+1),
                                      colors.lightgrey))
                    c[4].remove(s)
                row.append(s and locale.format('%.2f', s) or '')
            row.append(locale.format('%.2f', c[1]))
            rows.append(row)
        yield Table(rows, style=TableStyle(style))

    def createTableHeader(self):
        header = ['#']
        if self.championship.playersperteam > 1:
            header.append(gettext('Team'))
        else:
            header.append(gettext('Player'))

        for d,g in self.dates:
            # TRANSLATORS: this is a Python strftime() format, see
            # http://docs.python.org/3/library/time.html#time.strftime
            header.append(d.strftime(gettext('%m-%d-%y')))
        return header


class SinglesRanking(ChampionshipRanking):
    "General singles ranking."

    @classmethod
    def getArgumentsFromRequest(klass, session, request):
        return [session]

    def setup(self, sasession):
        (self.championships, self.period,
         self.ranking, self.ntourneys) = Championship.generalRanking(sasession)

    def getRightHeader(self):
        # TRANSLATORS: this is something like "Period 10-nov-12 — 10-dec-12"
        return gettext('Period %s — %s') % (
            self.period[0].strftime(gettext('%m-%d-%y')),
            self.period[1].strftime(gettext('%m-%d-%y')))

    def getCenterHeader(self):
        return gettext('%d tourneys') % self.ntourneys

    def getTitle(self):
        return gettext('General ranking')

    def getSubTitle(self):
        return gettext('Singles')

    def getLeftHeader(self):
        howmany = len(self.championships)
        if howmany == 0:
            return gettext('No prized tourneys in the championships')
        else:
            return ngettext('%d championship', '%d championships',
                            howmany) % howmany

    def createTableHeader(self):
        header = ['#']
        if self.championships[0][0].playersperteam > 1:
            header.append(gettext('Team'))
        else:
            header.append(gettext('Player'))

        for i in range(len(self.championships)):
            header.append('[%d]' % (i+1))
        return header

    def getElements(self):
        yield from super(SinglesRanking, self).getElements()

        if not self.ranking:
            return

        desc = gettext('%(championship)s, %(club)s, ')
        rows = []
        for i, (s, dates) in enumerate(self.championships):
            ntourneys = len(dates)
            cdesc = desc + ngettext('%(ntourneys)s tourney',
                                    '%(ntourneys)s tourneys',
                                    ntourneys)
            rows.append((Paragraph('[%d]' % (i+1), cardsmall_style),
                         Paragraph(cdesc % dict(championship=s.description,
                                                club=s.club.description,
                                                ntourneys=ntourneys),
                                   cardsmall_style)))

        yield Spacer(0, 1*cm)

        desc_width = self.doc.width/self.columns*0.9 - rank_width

        yield Table(rows, (rank_width, desc_width))


class DoublesRanking(SinglesRanking):
    "General doubles ranking."

    def setup(self, sasession):
        from sol.models import Championship
        (self.championships, self.period,
         self.ranking, self.ntourneys) = Championship.generalRanking(sasession, 2)

    def getSubTitle(self):
        return gettext('Doubles')


class WomenRanking(SinglesRanking):
    "General women ranking."

    def setup(self, sasession):
        from sol.models import Championship
        (self.championships, self.period,
         self.ranking, self.ntourneys) = Championship.generalRanking(sasession, 1, True)

    def getSubTitle(self):
        return gettext('Women')


class RatingRanking(BasicPrintout):
    "Glicko2 rating ranking."

    @classmethod
    def getArgumentsFromRequest(klass, session, request):
        t = translator(request)

        id = request.matchdict['id']
        try:
            idrating = int(id)
        except ValueError:
            try:
                entity = session.query(Rating).filter_by(guid=id).one()
            except NoResultFound:
                raise OperationAborted(t(_('Bad rating id: $id',
                                           mapping=dict(id=repr(id)))))
        else:
            entity = session.query(Rating).get(idrating)
            if entity is None:
                raise OperationAborted(t(_('Bad rating id: $id',
                                           mapping=dict(id=str(idrating)))))

        return [entity, getattr(request, '_LOCALE_', 'en')]

    def __init__(self, output, rating, locale):
        super().__init__(output, 1)
        self.rating = rating
        self.ranking = rating.ranking
        self.locale = locale

    @property
    def cache_max_age(self):
        "No cache."

        return 0

    def getSubTitle(self):
        return self.rating.description

    def getLeftHeader(self):
        howmany = len(self.rating.tourneys)
        if howmany == 0:
            return gettext('No tourneys in the rating')
        else:
            return ngettext('%d tourney', '%d tourneys',
                            howmany) % howmany

    def getTitle(self):
        return gettext('Rating ranking')

    def getRightHeader(self):
        ts = self.rating.time_span
        if ts and ts[0]:
            # TRANSLATORS: this is a Python strftime() format, see
            # http://docs.python.org/3/library/time.html#time.strftime
            format = gettext('%m-%d-%Y')
            return gettext('Period from %s to %s') % (ts[0].strftime(format),
                                                      ts[1].strftime(format))
        else:
            return ""

    def getCenterHeader(self):
        return gettext('page %d') % self.doc.page

    def getElements(self):
        yield Paragraph(self.getTitle(), title_style)
        yield Paragraph(self.getSubTitle(), subtitle_style)
        yield FrameBreak()
        yield NextPageTemplate('laterPages')

        rows = [('#',
                 gettext('Player'),
                 gettext('Rate'),
                 gettext('Deviation'),
                 gettext('Volatility'),
                 gettext('Tourneys'))]

        rows.extend((rank,
                     Paragraph(r[0].description, normal_style),
                     r[1], r[2], format_decimal(r[3], '0.00000', self.locale), r[4])
                    for rank, r in enumerate(self.ranking, 1))

        desc_width = self.doc.width - rank_width - scores_width*8
        style = [('SIZE', (0,0), (-1,-1), caption_style.fontSize),
                 ('LEADING', (0,0), (-1,-1), caption_style.leading),
                 ('FONT', (0,0), (-1,0), caption_style.fontName),
                 ('ALIGN', (2,0), (-1,0), 'RIGHT'),
                 ('ALIGN', (0,0), (0,-1), 'RIGHT'),
                 ('ALIGN', (2,1), (-1,-1), 'RIGHT'),
                 ('LINEBELOW', (0,1), (-1,-1), 0.25, colors.black)]

        yield Table(rows, (rank_width, desc_width,
                           scores_width*2, scores_width*2, scores_width*2,
                           scores_width*2),
                    style=style)
