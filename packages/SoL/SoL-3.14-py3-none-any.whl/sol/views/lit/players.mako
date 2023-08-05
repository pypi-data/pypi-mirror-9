## -*- mode: html; coding: utf-8 -*-
## :Progetto:  SoL
## :Creato:    mer 16 lug 2014 12:19:04 CEST
## :Autore:    Lele Gaifax <lele@metapensiero.it>
## :Licenza:   GNU General Public License version 3 or later
##

<%inherit file="base.mako" />

<%def name="title()">
  ${_('Players directory')}
</%def>

## Body

<div class="centered multi-columns">
% for letter, countsbycountry in index:
  <h3>«${letter}»</h3>
  % for count in countsbycountry:
    <p>
      <a href="${request.route_path('lit_players_list', letter=letter, country=count['code'])}">
        % if count['code']:
        <img src="/static/images/flags/${count['code']}.png" />
        % endif
        ${count['country']}: ${count['count']} ${ngettext('player', 'players', count['count'])}
      </a>
    </p>
  % endfor
% endfor
</div>