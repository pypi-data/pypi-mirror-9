## -*- mode: html; coding: utf-8 -*-
## :Progetto:  SoL
## :Creato:    sab 13 dic 2008 16:33:31 CET
## :Autore:    Lele Gaifax <lele@metapensiero.it>
## :Licenza:   GNU General Public License version 3 or later
##

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">

<%!
   from datetime import datetime
%>

<html xmlns="http://www.w3.org/1999/xhtml">
  ${self.head()}

  <body>
    <div class="header">
      ${self.header()}
    </div>

    ${self.body()}

    <div class="footer">
      ${self.footer()}
    </div>
  </body>
</html>

<%def name="head()">
  <head profile="http://www.w3.org/2005/10/profile">
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <base href="/lit/" />
    <title>${self.title()}</title>
    <link rel="icon" type="image/png" href="/static/favicon.png" />
    <link rel="stylesheet" type="text/css" href="/static/css/lit.css" />
  </head>
</%def>

<%def name="header()">
    ${self.logo()}
    <h1 class="title centered">${self.title()}</h1>
    ${self.club_emblem()}
</%def>

<%def name="logo(url='/static/images/logo.png', href='../lit')">
    <div id="sol_logo">
      <a href="${href}">
        <img class="logo" src="${url}" title="${_('Summary')}"/>
      </a>
    </div>
</%def>

<%def name="club_emblem(url='', href='', title='', target='_blank')">
    % if url:
    <div id="club_emblem">
      <a href="${href or ''}" target="${target}">
        <img id="emblem" src="${url}" title="${title}" />
      </a>
    </div>
    % endif
</%def>

<%def name="footer()">
  <hr />
  <span id="producer">
    <a href="https://bitbucket.org/lele/sol">
      ${_('Scarry On Line')} ${_('version')} ${version}
    </a>
  </span>
  <span id="generated">
    ${datetime.now().strftime(_('%m-%d-%Y %I:%M %p'))}
  </span>
</%def>
