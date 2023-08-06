## -*- mode: html; coding: utf-8 -*-
## :Progetto:  SoL
## :Creato:    sab 13 dic 2008 16:34:14 CET
## :Autore:    Lele Gaifax <lele@metapensiero.it>
## :Licenza:   GNU General Public License version 3 or later
##

<%inherit file="base.mako" />

<%
import locale
from sol.models.utils import njoin
if entity.playersperteam==1:
    subject = _('Player')
else:
    subject = _('Team')
%>

<%def name="title()">
  ${entity.description}
</%def>

<%def name="club_emblem(url='', href='')">
  <%
     if entity.club.emblem:
         parent.club_emblem(url="/lit/emblem/%s" % entity.club.emblem,
                            href=entity.club.siteurl,
                            title=entity.club.description)
  %>
</%def>

<%def name="table_header(dates)">
  <thead>
    <tr>
      <td class="rank-header">#</td>
      <td class="player-header">${subject}</td>
      % for date,guid in dates:
      <td class="event-header">
        <a href="${request.route_path('lit_tourney', guid=guid) | n}">
          ${date.strftime(_('%m-%d-%y'))}
        </a>
      </td>
      % endfor
      <td class="sortedby total-header">${_('Total')}</td>
    </tr>
  </thead>
</%def>

<%def name="table_body(ranking)">
  <tbody>
    % for i, row in enumerate(ranking, 1):
    ${table_row(i, row)}
    % endfor
  </tbody>
</%def>

<%def name="table_row(rank, row)">
    <tr class="${rank%2 and 'odd' or 'even'}-row">
      <td class="rank">${rank}</td>
      <td class="player">${njoin(row[0], stringify=lambda p: '<a href="%s">%s</a>' % (request.route_path('lit_player', guid=p.guid), escape(p.caption(html=False)))) | n}</td>
      % for s in row[2]:
      <%
         if row[4] and s in row[4]:
             eventclass = 'skipped-event'
             row[4].remove(s)
         else:
             eventclass = 'event'
      %>
      <td class="${eventclass}">${s and locale.format('%.2f', s) or ''}</td>
      % endfor
      <td class="sortedby total">${locale.format('%.2f', row[1])}</td>
    </tr>
</%def>

## Body

<dl>
  <dt>${_('Club')}</dt>
  <dd><a href="${request.route_path('lit_club', guid=entity.club.guid) | n}">${entity.club.description}</a></dd>
  <dt>${_('Players per team')}</dt> <dd>${entity.playersperteam}</dd>
  <% pmethod = entity.__class__.__table__.c.prizes.info['dictionary'][entity.prizes] %>
  <dt>${_('Prize-giving method')}</dt> <dd>${_(pmethod)}</dd>
  % if entity.skipworstprizes:
  <dt>${_('Skip worst prizes')}</dt> <dd>${entity.skipworstprizes}</dd>
  % endif
  % if entity.previous:
  <dt>${_('Previous championship')}</dt>
  <dd>
    <a href="${request.route_path('lit_championship', guid=entity.previous.guid) | n}">
      ${entity.previous.description}
    </a>
  </dd>
  % endif
  % if entity.next:
  <dt>${_('Next championship')}</dt>
  <dd>
    <a href="${request.route_path('lit_championship', guid=entity.next.guid) | n}">${entity.next.description}</a>
  </dd>
  % endif
</dl>

<% dates, ranking = entity.ranking() %>
<table class="ranking">
  <caption>${_('Championship ranking')} (<a href="${request.route_path('pdf_championshipranking', id=entity.guid) | n}">pdf</a>) </caption>
  ${table_header(dates)}
  ${table_body(ranking)}
</table>
