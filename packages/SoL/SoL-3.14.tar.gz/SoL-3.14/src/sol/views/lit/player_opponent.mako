## -*- mode: html; coding: utf-8 -*-
## :Progetto:  SoL
## :Creato:    gio 06 nov 2014 19:12:19 CET
## :Autore:    Lele Gaifax <lele@metapensiero.it>
## :Licenza:   GNU General Public License version 3 or later
##

<%inherit file="base.mako" />

<%def name="header()">
    ${self.logo()}
    <h1 class="title centered">
      <a href="${request.route_path('lit_player', guid=entity.guid)}">
        ${entity.caption(html=False)}
      </a>
      ${_('vs')}
      <a href="${request.route_path('lit_player', guid=opponent.guid)}">
        ${opponent.caption(html=False)}
      </a>
    </h1>
</%def>

<%def name="title()">
  ${_('Matches between %s and %s') % (entity.caption(html=False), opponent.caption(html=False))}
</%def>

<%
matches = entity.opponentMatches(opponent)
nmatches = len(matches)
ewon = sum(1 for m in matches
           if (m.competitor1.player1 is entity and m.score1 > m.score2)
           or (m.competitor2.player1 is entity and m.score1 < m.score2))
owon = sum(1 for m in matches
           if (m.competitor1.player1 is opponent and m.score1 > m.score2)
           or (m.competitor2.player1 is opponent and m.score1 < m.score2))
tied = sum(1 for m in matches if m.score1 == m.score2)
%>

<dl>
  <dt>${_('Matches')}</dt> <dd>${nmatches}</dd>
  % if nmatches:
  <dt>${_('Won by %s') % entity.caption(html=False)}</dt>
  <dd>${ewon} ${'(%d%%)' % (100 * ewon // nmatches)}</dd>
  <dt>${_('Won by %s') % opponent.caption(html=False)}</dt>
  <dd>${owon} ${'(%d%%)' % (100 * owon // nmatches)}</dd>
  <dt>${_('Tied')}</dt>
  <dd>${tied} ${'(%d%%)' % (100 * tied // nmatches)}</dd>
  % endif
</dl>

<%def name="matches_header()">
  <thead>
    <tr>
      <th class="rank-header" rowspan="2">#</th>
      <th class="tourney-header" rowspan="2">${_('Tourney')}</th>
      <th class="championship-header" rowspan="2">${_('Championship')}</th>
      <th class="date-header" rowspan="2">${_('Date')}</th>
      <th class="event-header" rowspan="2">${_('Round')}</th>
      <th class="event-header" colspan="2">${_('Scores')}</th>
    </tr>
    <tr>
      <th class="event-header">${entity.caption(html=False)}</th>
      <th class="event-header">${opponent.caption(html=False)}</th>
    </tr>
  </thead>
</%def>

<%def name="matches_body()">
  <tbody>
    <% prevs = None %>
    % for i, row in enumerate(matches, 1):
    ${matches_row(i, row, row.tourney.championship is prevs)}
    <% prevs = row.tourney.championship %>
    % endfor
  </tbody>
</%def>

<%def name="matches_row(index, row, samechampionship)">
    <tr class="${index%2 and 'odd' or 'even'}-row">
      <td class="index">${index}</td>
      <td class="tourney">
        <a href="${request.route_path('lit_tourney', guid=row.tourney.guid, _query=dict(turn=row.turn))}">
          ${row.tourney.description}
        </a>
      </td>
      <td class="championship">
        <a href="${request.route_path('lit_championship', guid=row.tourney.championship.guid) | n}" title="${samechampionship and _('Idem') or row.tourney.championship.club.description}">
          ${samechampionship and '...' or row.tourney.championship.description}
        </a>
      </td>
      <td class="date">${row.tourney.date.strftime(_('%m-%d-%Y'))}</td>
      <td class="event">${row.turn}</td>
      % if row.competitor1.player1 is entity:
      <td class="event${' winner' if row.score1>row.score2 else ''}">${row.score1}</td>
      <td class="event${' winner' if row.score1<row.score2 else ''}">${row.score2}</td>
      % else:
      <td class="event${' winner' if row.score1<row.score2 else ''}">${row.score2}</td>
      <td class="event${' winner' if row.score1>row.score2 else ''}">${row.score1}</td>
      % endif
    </tr>
</%def>

<table class="ranking">
  <caption>
  ${_('Matches results')} (<a href="${request.route_path('svg_player_opponent', guid=entity.guid, opponent=opponent.guid) | n}">${_('chart')}</a>)
  </caption>
  ${matches_header()}
  ${matches_body()}
</table>
