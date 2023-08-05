## -*- mode: html; coding: utf-8 -*-
## :Progetto:  SoL
## :Creato:    mer 09 lug 2014 17:34:22 CEST
## :Autore:    Lele Gaifax <lele@metapensiero.it>
## :Licenza:   GNU General Public License version 3 or later
##

<%inherit file="base.mako" />

<%def name="title()">
  ${entity.caption(html=False)}
</%def>

<%def name="club_emblem(url='', href='')">
  <%
     if entity.emblem:
         parent.club_emblem(url="/lit/emblem/%s" % entity.emblem,
                            href=entity.siteurl,
                            title=entity.description)
  %>
</%def>


<dl>
  % if entity.nationality:
  <dt>${_('Country')}</dt>
  <dd>
    <img src="/static/images/flags/${entity.nationality}.png" />
    ${entity.country}
  </dd>
  % endif
  % if entity.siteurl:
  <dt>${_('Federation web site') if entity.isfederation else _('Club web site')}</dt>
  <dd><a href="${entity.siteurl}">${entity.siteurl}</a></dd>
  % endif
  % if len(entity.championships):
  <dt>${_('Championships')}</dt><dd>${len(entity.championships)}</dd>
  % endif
  % if len(entity.associated_players):
  <dt>${_('Players')}</dt><dd>${len(entity.associated_players)}</dd>
  % endif
  % if entity.isfederation and len(entity.federated_players):
  <dt>${_('Federated players')}</dt><dd>${len(entity.federated_players)}</dd>
  % endif
</dl>

<%
   singles = []
   doubles = []
   teams = []
   for championship in entity.championships:
       pt = []
       for t in championship.tourneys:
           if t.prized:
               pt.append(t)
       nt = len(pt)
       if nt:
           new = (today - pt[-1].date).days < 21
           if championship.playersperteam == 1:
               singles.append((championship, nt, new))
           elif championship.playersperteam == 2:
               doubles.append((championship, nt, new))
           else:
               teams.append((championship, nt, new))
%>
% if singles:
<h4 class="centered">${_('Singles')}</h4>
<div class="centered multi-columns">
  % for championship,nt,new in singles:
  <p class="championship">
    <a href="${request.route_path('lit_championship', guid=championship.guid) | n}">${championship.description}</a>
    (${ngettext('%d tourney', '%d tourneys', nt) % nt})
    % if new:
    <img src="/static/images/new.png" />
    % endif
  </p>
  % endfor
</div>
% endif
% if doubles:
<h4 class="centered">${_('Doubles')}</h4>
<div class="centered multi-columns">
  % for championship,nt,new in doubles:
  <p class="championship">
    <a href="${request.route_path('lit_championship', guid=championship.guid) | n}">${championship.description}</a>
    (${ngettext('%d tourney', '%d tourneys', nt) % nt})
    % if new:
    <img src="/static/images/new.png" />
    % endif
  </p>
  % endfor
</div>
% endif
% if teams:
<h4 class="centered">${_('Teams')}</h4>
<div class="centered multi-columns">
  % for championship,nt,new in teams:
  <p class="championship">
    <a href="${request.route_path('lit_championship', guid=championship.guid) | n}">${championship.description}</a>
    (${ngettext('%d tourney', '%d tourneys', nt) % nt})
    % if new:
    <img src="/static/images/new.png" />
    % endif
  </p>
  % endfor
</div>
% endif
</div>