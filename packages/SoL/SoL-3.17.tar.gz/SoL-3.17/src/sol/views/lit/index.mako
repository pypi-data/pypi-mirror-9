## -*- mode: html; coding: utf-8 -*-
## :Progetto:  SoL
## :Creato:    mer 17 dic 2008 02:16:28 CET
## :Autore:    Lele Gaifax <lele@metapensiero.it>
## :Licenza:   GNU General Public License version 3 or later
##

<%inherit file="base.mako" />

<%
from operator import attrgetter
%>

<%def name="title()">
  ${_('SoL Lit')}
</%def>

## Body

<dl>
  <dt>${_('Clubs')}</dt>
  <dd>
    ${nclubs}
    (${ngettext('%d country', '%d countries', nccountries) % nccountries})
  </dd>
  <dt>${_('Federations')}</dt> <dd>${nfederations}</dd>
  <dt>${_('Championships')}</dt> <dd>${nchampionships}</dd>
  <dt>${_('Tourneys')}</dt>
  <dd>${ntourneys} (<a href="${request.route_path('lit_latest', _query=dict(n=20))|n}">${_('latest 20')}</a>)</dd>
  <dt>${_('Players')}</dt>
  <dd>
    <a href="${request.route_path('lit_players')}">${nplayers}</a>
    (<a href="${request.route_path('svg_playersdist') | n}">${ngettext('%d country', '%d countries', npcountries) % npcountries}</a>)
  </dd>
  <dt>${_('Ratings')}</dt> <dd>${nratings}</dd>
</dl>

<div class="centered multi-columns">
% for index, (country, code) in enumerate(sorted(clubsbycountry)):
  <h3>
    % if code:
    <img src="/static/images/flags/${code}.png" />
    % endif
    ${country}
  </h3>
  % for club in sorted(clubsbycountry[(country, code)], key=attrgetter('description')):
  <p class="${'federation' if club.isfederation else 'club'}">
    <a href="${request.route_path('lit_club', guid=club.guid) | n}">${club.description}</a>
    <% nc = len(club.championships) %>
    (${ngettext('%d championship', '%d championships', nc) % nc})
  </p>
  % endfor
  </ul>
% endfor
</div>
