## -*- mode: html; coding: utf-8 -*-
## :Progetto:  SoL
## :Creato:    gio 10 lug 2014 10:44:12 CEST
## :Autore:    Lele Gaifax <lele@metapensiero.it>
## :Licenza:   GNU General Public License version 3 or later
##

<%inherit file="base.mako" />

<%def name="title()">
  ${entity.description}
</%def>

<% ranking = entity.ranking %>

<dl>
  <% level = entity.__class__.__table__.c.level.info['dictionary'][entity.level] %>
  <dt>${_('Level')}</dt> <dd>${_(level)}</dd>
  <dt>${_('Tau')}</dt> <dd>${entity.tau}</dd>
  <dt>${_('Default rate')}</dt> <dd>${entity.default_rate}</dd>
  <dt>${_('Default deviation')}</dt> <dd>${entity.default_deviation}</dd>
  <dt>${_('Default volatility')}</dt> <dd>${entity.default_volatility}</dd>
  <dt>${_('Rate range')}</dt> <dd>${entity.lower_rate}—${entity.higher_rate}</dd>
  <% outcomes = entity.__class__.__table__.c.outcomes.info['dictionary'][entity.outcomes] %>
  <dt>${_('Match outcomes')}</dt> <dd>${_(outcomes)}</dd>
  <dt>${_('Tourneys')}</dt> <dd>${ntourneys}</dd>
  <dt>${_('Players')}</dt> <dd>${len(ranking)}</dd>
</dl>

<%def name="ranking_header()">
  <thead>
    <tr>
      <td class="rank-header">#</td>
      <td class="player-header">${_('Player')}</td>
      <td class="sortedby total-header">${_('Rate')}</td>
      <td class="event-header">${_('Deviation')}</td>
      <td class="event-header">${_('Volatility')}</td>
      <td class="event-header">${_('Tourneys')}</td>
    </tr>
  </thead>
</%def>

<%def name="ranking_body(ranking)">
  <tbody>
    % for i, (player, rate, deviation, volatility, nrates) in enumerate(ranking, 1):
    ${ranking_row(i, player, rate, deviation, volatility, nrates)}
    % endfor
  </tbody>
</%def>

<%def name="ranking_row(rank, player, rate, deviation, volatility, nrates)">
    <tr class="${rank%2 and 'odd' or 'even'}-row">
      <td class="rank">${rank}</td>
      <td class="player">
        <a href="${request.route_path('svg_ratingchart', id=entity.guid, _query=dict(player=player.guid)) | n}" title="${_('Show rates chart')}">${player.caption(html=False)}</a>
      </td>
      <td class="sortedby total">${rate}</td>
      <td class="event">${deviation}</td>
      <td class="event">${volatility}</td>
      <td class="event">${nrates}</td>
    </tr>
</%def>

<table class="ranking">
  <caption>
  ${_('Ranking')} (<a href="${request.route_path('pdf_ratingranking', id=entity.guid) | n}">pdf</a>)
  </caption>
  ${ranking_header()}
  ${ranking_body(ranking)}
</table>
