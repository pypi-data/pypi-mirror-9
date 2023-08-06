## -*- mode: html; coding: utf-8 -*-
## :Progetto:  SoL
## :Creato:    dom 13 lug 2014 10:08:55 CEST
## :Autore:    Lele Gaifax <lele@metapensiero.it>
## :Licenza:   GNU General Public License version 3 or later
##

<%inherit file="base.mako" />

<%
from sol.models.utils import njoin
%>

<%def name="title()">
  ${ngettext('Latest %d tournament', 'Latest %d tournaments', n) % n}
</%def>

<%def name="table_header()">
  <thead>
    <tr>
      <td class="rank-header">#</td>
      <td class="tourney-header">${_('Tournament')}</td>
      <td class="date-header">${_('Date')}</td>
      <td class="event-header">${_('Location')}</td>
      <td class="championship-header">${_('Club')}</td>
      <td class="championship-header">${_('Championship')}</td>
      <td class="player-header">${_('Winner')}</td>
    </tr>
  </thead>
</%def>

<%def name="table_body()">
  <tbody>
    % for i, row in enumerate(tourneys, 1):
    ${table_row(i, row)}
    % endfor
  </tbody>
</%def>

<%def name="table_row(rank, row)">
    <tr class="${rank%2 and 'odd' or 'even'}-row">
      <td class="rank">${rank}</td>
      <td class="tourney"><a href="${request.route_path('lit_tourney', guid=row.guid) | n}">${row.description}</a></td>
      <td class="date sortedby">${row.date.strftime(_('%m-%d-%y'))}</td>
      <td>${row.location}</td>
      <td class="championship"><a href="${request.route_path('lit_club', guid=row.championship.club.guid) | n}">${row.championship.club.description}</a></td>
      <td class="championship"><a href="${request.route_path('lit_championship', guid=row.championship.guid) | n}">${row.championship.description}</a></td>
      <%
      ranking = row.ranking
      if ranking:
          winner = ranking[0]
          players = [getattr(winner, 'player%d'%i) for i in range(1,5) if getattr(winner, 'player%d'%i) is not None]
      else:
          players = []
      %>
      <td class="player winner">${njoin(players, stringify=lambda p: '<a href="%s">%s</a>' % (request.route_path('lit_player', guid=p.guid), escape(p.caption(html=False)))) | n}</td>
    </tr>
</%def>

<table class="ranking">
  ${table_header()}
  ${table_body()}
</table>
