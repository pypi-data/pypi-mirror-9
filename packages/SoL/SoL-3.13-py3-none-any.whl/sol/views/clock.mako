<!-- -*- mode: html; coding: utf-8 -*-
-- :Progetto:  SoL
-- :Creato:    gio 06 nov 2008 17:24:19 CET
-- :Autore:    Lele Gaifax <lele@metapensiero.it>
-- :Licenza:   GNU General Public License version 3 or later
-- -->

<html>
  <head>
    <title>${_('SoL Clock')}</title>

    % for group, sheets in stylesheets:
    <!-- ${group} -->
      % for sheet in sheets:
    <link rel="stylesheet" type="text/css" href="${sheet}"></link>
      % endfor

    % endfor
    <!--[if IE]><script type="text/javascript" src="/static/clock/excanvas.js"></script><![endif]-->

    % for group, scripts in javascripts:
    <!-- ${group} -->
      % for script in scripts:
    <script type="text/javascript" src="${script}"></script>
      % endfor

    % endfor

    <!-- Sounds initialization -->
    <script type="text/javascript">
      soundManager.setup({
        url: '/static/clock/', // directory where SM2 .SWFs live
        debugMode: false,
        onready: function() {
          soundManager.createSound('tic','/static/sounds/tic.ogg');
          soundManager.createSound('tac','/static/sounds/tac.ogg');
          soundManager.createSound('start','/static/sounds/start.ogg');
          soundManager.createSound('prealarm','/static/sounds/prealarm.ogg');
          soundManager.createSound('stop','/static/sounds/stop.ogg');
        }
      });
    </script>

    <!-- Prevent accidental close/stop -->
    <script type="text/javascript">
      window.addEventListener("beforeunload", function (e) {
        var clock = document.getElementById('c1').getClock();
        if(clock.startTime) {
          var msg = "${_('Closing the page will stop the clock.')}";

          (e || window.event).returnValue = msg;     //Gecko + IE
          return msg;                                //Webkit, Safari, Chrome etc.
        }
      });
    </script>
  </head>

  <body>
    <div>
      <!-- soundManager appends "hidden" Flash to the first DIV on the page. -->
    </div>

    <h2 class="centered">${_('Playing %s round') % currentturn}</h2>

    <table class="centered">
      <tbody>
        <tr>
          <td rowspan="2">
            <canvas id="c1"
                    class="CoolAlarmClock:swissRail::noSeconds::::${duration}:${prealarm}:${starttime}"
                    confirmrestart="${_('Do you really want to restart the countdown?')}"
                    notifystart="${notifystart}">
            </canvas>
          </td>
          <td class="centered">${_('%d minutes, %d minutes of prealarm')%(duration,prealarm)}</td>
        </tr>
        <tr>
          <td width="50%" id="c1-time-left" class="timeleft centered"></td>
        </tr>
      </tbody>
    </table>
    <div class="centered hint">
      % if starttime:
      <button type="button" onclick="document.getElementById('c1').startCountdown();">
        ${_('Restart the countdown')}
      </button>
      % else:
      <button type="button" onclick="document.getElementById('c1').startCountdown();">
        ${_('(Re)start the countdown immediately')}
      </button>
      ${_('or')}
      <button type="button" onclick="document.getElementById('c1').startDelayedCountdown(15000);">
        ${_('do it in 15 seconds')}
      </button>
      % endif
      &nbsp;
      <button type="button" onclick="window.close();">
        ${_('Close the window to stop')}
      </button>
    </div>
  </body>
</html>
