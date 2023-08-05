## -*- mode: html; coding: utf-8 -*-
## :Progetto:  SoL -- Player's matches
## :Creato:    sab 08 nov 2014 09:16:28 CET
## :Autore:    Lele Gaifax <lele@metapensiero.it>
## :Licenza:   GNU General Public License version 3 or later
##

<%inherit file="base.mako" />

<%
from sol.models.utils import njoin
%>

<%def name="title()">
  ${_('Singles matches played by %s') % entity.caption(html=False)}
</%def>

<%def name="club_emblem(url='', href='')">
  <%
     if entity.idclub is not None and entity.club.emblem:
         parent.club_emblem(url="/lit/emblem/%s" % entity.club.emblem,
                            href=entity.club.siteurl,
                            title=entity.club.description)
  %>
</%def>

## Body

<%
opponents = entity.opponents()
%>

% if entity.portrait:
<img class="centered portrait" src="/lit/portrait/${entity.portrait}" />
% endif

<dl>
  <dt>${_('First name')}</dt> <dd>${entity.firstname}</dd>
  <dt>${_('Last name')}</dt> <dd>${entity.lastname}</dd>
  % if not entity.shouldOmitNickName():
  <dt>${_('Nickname')}</dt> <dd>${entity.nickname}</dd>
  % endif
  % if entity.sex:
  <% sex = entity.__class__.__table__.c.sex.info['dictionary'][entity.sex] %>
  <dt>${_('Sex')}</dt> <dd>${_(sex)}</dd>
  % endif
  % if entity.nationality:
  <dt>${_('Country')}</dt>
  <dd>
    <img src="/static/images/flags/${entity.nationality}.png" />
    ${entity.country}
    % if entity.citizenship:
    (${_('citizenship')})
    % endif
  </dd>
  % endif
  % if entity.club and entity.federation and entity.club is entity.federation:
  <dt>${_('Associated and federated with')}</dt>
  <dd>
    <a href="${request.route_path('lit_club', guid=entity.club.guid) | n}">${entity.club.description}</a>
  </dd>
  % else:
  % if entity.club:
  <dt>${_('Associated to')}</dt>
  <dd>
    <a href="${request.route_path('lit_club', guid=entity.club.guid) | n}">${entity.club.description}</a>
  </dd>
  % endif
  % if entity.federation:
  <dt>${_('Federated with')}</dt>
  <dd>
    <a href="${request.route_path('lit_club', guid=entity.federation.guid) | n}">${entity.federation.description}</a>
  </dd>
  % endif
  % endif
  % if opponents:
  <dt>${_('Direct matches')}</dt>
  <%
     wins, losts, ties, singles = entity.matchesSummary()
     done = wins + losts + ties
     msgs = []
     if wins:
         wp = ' (%d%%)' % (100 * wins // done)
         msgs.append((ngettext('%d won', '%d won', wins) % wins) + wp)
     if losts:
         lp = ' (%d%%)' % (100 * losts // done)
         msgs.append((ngettext('%d lost', '%d lost', losts) % losts + lp))
     if ties:
         tp = ' (%d%%)' % (100 * ties // done)
         msgs.append((ngettext('%d tied', '%d tied', ties) % ties) + tp)
  %>
  <dd>${njoin(msgs)}</dd>
  % endif
</dl>

<%def name="opponents_header()">
  <thead>
    <tr>
      <th class="player-header" rowspan="2">${_('Opponent')}</th>
      <th class="event-header" colspan="7">${_('Matches')}</th>
      <th class="event-header" colspan="3">${_('Coins')}</th>
    </tr>
    <tr>
      <th class="sortedby total-header">${_('Number')}</th>
      <th class="event-header winner">${_('Won')}</th>
      <th class="event-header winner">%</th>
      <th class="event-header">${_('Lost')}</th>
      <th class="event-header">%</th>
      <th class="event-header">${_('Tied')}</th>
      <th class="event-header">%</th>
      <th class="event-header">+</th>
      <th class="event-header">-</th>
      <th class="event-header">${_('Diff')}</th>
    </tr>
  </thead>
</%def>

<%def name="opponents_body()">
  <tbody>
    % for i, row in enumerate(opponents, 1):
    ${opponents_row(i, row)}
    % endfor
  </tbody>
</%def>

<%def name="opponents_row(index, row)">
    <tr class="${index%2 and 'odd' or 'even'}-row">
      <td class="player">${'<a href="%s">%s</a>' % (request.route_path('lit_player_opponent', guid=entity.guid, opponent=row[0].guid), escape(row[0].caption(html=False))) | n}</td>
      <% done = row[1] + row[2] + row[3] %>
      <td class="sortedby event">${done}</td>
      <td class="event winner">${row[1]}</td>
      <td class="event winner">${100 * row[1] // done}%</td>
      <td class="event">${row[2]}</td>
      <td class="event">${100 * row[2] // done}%</td>
      <td class="event">${row[3]}</td>
      <td class="event">${100 * row[3] // done}%</td>
      <td class="event">${row[4]}</td>
      <td class="event">${row[5]}</td>
      <td class="event">${row[4] - row[5]}</td>
    </tr>
</%def>

% if opponents:
<table class="ranking">
  <caption>${_('Opponents')}</caption>
  ${opponents_header()}
  ${opponents_body()}
</table>
% endif
