## -*- mode: html; coding: utf-8 -*-
## :Progetto:  SoL
## :Creato:    mer 16 lug 2014 13:20:13 CEST
## :Autore:    Lele Gaifax <lele@metapensiero.it>
## :Licenza:   GNU General Public License version 3 or later
##

<%inherit file="base.mako" />

<%def name="title()">
  ${_('Players directory')}
</%def>

<dl>
  <dt>${_('Country')}</dt>
  <dd>
    % if code:
    <img src="/static/images/flags/${code}.png" />
    % endif
    ${country}
  </dd>
  <dt>${_('Letter')}</dt> <dd>«${letter}»</dd>
</dl>

<div class="centered multi-columns">
  % for player in players:
  <p>
    <a href="${request.route_path('lit_player', guid=player.guid)}">${player.caption(False)}</a>
  </p>
  % endfor
</div>
