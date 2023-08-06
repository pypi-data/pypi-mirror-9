/*
 CoolClock by Simon Baird
 Version 2.1.4-13-g6d9c3bf (11-Dec-2012)

 See http://randomibis.com/coolclock and https://github.com/simonbaird/CoolClock

 Copyright (c) 2010-2013, Simon Baird.
 All rights reserved.

 Redistribution and use in source and binary forms, with or without
 modification, are permitted provided that the following conditions are met:
 - Redistributions of source code must retain the above copyright notice,
 this list of conditions and the following disclaimer.
 - Redistributions in binary form must reproduce the above copyright notice,
 this list of conditions and the following disclaimer in the documentation
 and/or other materials provided with the distribution.
 - Neither the name Simon Baird nor the names of other contributors may be
 used to endorse or promote products derived from this software without
 specific prior written permission.

 THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 ARE DISCLAIMED. IN NO EVENT SHALL SIMON BAIRD BE LIABLE FOR ANY DIRECT,
 INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
 THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

//jsl:declare CoolAlarmClock
//jsl:declare clearTimeout
//jsl:declare setTimeout
//jsl:declare soundManager
//jsl:declare jQuery

// Constructor for CoolAlarmClock objects
window.CoolAlarmClock = function(options) {
    return this.init(options);
};

// Config contains some defaults, and clock skins
CoolAlarmClock.config = {
    tickDelay: 200,
    defaultRadius: 85,
    renderRadius: 100,
    defaultSkin: "chunkySwiss",
    defaultFont: "15px sans-serif",
    // Should be in skin probably...
    // (TODO: allow skinning of digital display)
    showSecs: true,
    showAmPm: true,

    skins: {
        // There are more skins in moreskins.js
        // Try making your own skin by copy/pasting one of these and tweaking it
        swissRail: {
            outerBorder: { lineWidth: 2, radius:95, color: "black", alpha: 1 },
            smallIndicator: { lineWidth: 2, startAt: 88, endAt: 92, color: "black", alpha: 1 },
            largeIndicator: { lineWidth: 4, startAt: 79, endAt: 92, color: "black", alpha: 1 },
            hourHand: { lineWidth: 8, startAt: -15, endAt: 50, color: "black", alpha: 1 },
            minuteHand: { lineWidth: 7, startAt: -15, endAt: 75, color: "black", alpha: 1 },
            secondHand: { lineWidth: 1, startAt: -20, endAt: 85, color: "red", alpha: 1 },
            secondDecoration: { lineWidth: 1, startAt: 70, radius: 4, fillColor: "red", color: "red", alpha: 1 },
            startDecoration: { lineWidth: 1, startAt: 80, radius: 4, fillColor: "green", color: "red", alpha: 1 },
            preAlarmDecoration: { lineWidth: 1, startAt: 80, radius: 4, fillColor: "orange", color: "red", alpha: 1 },
            alarmDecoration: { lineWidth: 1, startAt: 80, radius: 4, fillColor: "red", color: "red", alpha: 1 }
        },
        chunkySwiss: {
            outerBorder: { lineWidth: 4, radius:97, color: "black", alpha: 1 },
            smallIndicator: { lineWidth: 4, startAt: 89, endAt: 93, color: "black", alpha: 1 },
            largeIndicator: { lineWidth: 8, startAt: 80, endAt: 93, color: "black", alpha: 1 },
            hourHand: { lineWidth: 12, startAt: -15, endAt: 60, color: "black", alpha: 1 },
            minuteHand: { lineWidth: 10, startAt: -15, endAt: 85, color: "black", alpha: 1 },
            secondHand: { lineWidth: 4, startAt: -20, endAt: 85, color: "red", alpha: 1 },
            secondDecoration: { lineWidth: 2, startAt: 70, radius: 8, fillColor: "red", color: "red", alpha: 1 },
            startDecoration: { lineWidth: 1, startAt: 80, radius: 4, fillColor: "green", color: "red", alpha: 1 },
            preAlarmDecoration: { lineWidth: 1, startAt: 80, radius: 4, fillColor: "orange", color: "red", alpha: 1 },
            alarmDecoration: { lineWidth: 1, startAt: 80, radius: 4, fillColor: "red", color: "red", alpha: 1 }
        },
        chunkySwissOnBlack: {
            outerBorder: { lineWidth: 4, radius:97, color: "white", alpha: 1 },
            smallIndicator: { lineWidth: 4, startAt: 89, endAt: 93, color: "white", alpha: 1 },
            largeIndicator: { lineWidth: 8, startAt: 80, endAt: 93, color: "white", alpha: 1 },
            hourHand: { lineWidth: 12, startAt: -15, endAt: 60, color: "white", alpha: 1 },
            minuteHand: { lineWidth: 10, startAt: -15, endAt: 85, color: "white", alpha: 1 },
            secondHand: { lineWidth: 4, startAt: -20, endAt: 85, color: "red", alpha: 1 },
            secondDecoration: { lineWidth: 2, startAt: 70, radius: 8, fillColor: "red", color: "red", alpha: 1 },
            startDecoration: { lineWidth: 1, startAt: 80, radius: 4, fillColor: "green", color: "red", alpha: 1 },
            preAlarmDecoration: { lineWidth: 1, startAt: 80, radius: 4, fillColor: "orange", color: "red", alpha: 1 },
            alarmDecoration: { lineWidth: 1, startAt: 80, radius: 4, fillColor: "red", color: "red", alpha: 1 }
        }
    },

    // Test for IE so we can nurse excanvas in a couple of places
    isIE: !!document.all,

    // Will store (a reference to) each clock here, indexed by the id of the canvas element
    clockTracker: {},

    // For giving a unique id to coolclock canvases with no id
    noIdCount: 0
};

// Define the CoolAlarmClock object's methods
CoolAlarmClock.prototype = {

    // Initialise using the parameters parsed from the colon delimited class
    init: function(options) {
        // Parse and store the options
        this.canvasId       = options.canvasId;
        this.skinId         = options.skinId || CoolAlarmClock.config.defaultSkin;
        this.font           = options.font || CoolAlarmClock.config.defaultFont;
        this.displayRadius  = options.displayRadius || CoolAlarmClock.config.defaultRadius;
        this.renderRadius   = options.renderRadius || CoolAlarmClock.config.renderRadius;
        this.showSecondHand = typeof options.showSecondHand == "boolean" ? options.showSecondHand : true;
        this.gmtOffset      = (options.gmtOffset != null && options.gmtOffset != '') ? parseFloat(options.gmtOffset) : null;
        this.showDigital    = typeof options.showDigital == "boolean" ? options.showDigital : false;
        this.logClock       = typeof options.logClock == "boolean" ? options.logClock : false;
        this.logClockRev    = typeof options.logClock == "boolean" ? options.logClockRev : false;
        this.confirmRestart = options.confirmRestart;
        this.notifyStart    = options.notifyStart;

        this.tickDelay      = CoolAlarmClock.config.tickDelay;
        // Get the canvas element
        this.canvas = document.getElementById(this.canvasId);

        // Make the canvas the requested size. It's always square.
        this.canvas.setAttribute("width",this.displayRadius*2);
        this.canvas.setAttribute("height",this.displayRadius*2);
        this.canvas.style.width = this.displayRadius*2 + "px";
        this.canvas.style.height = this.displayRadius*2 + "px";

        // Determine by what factor to relate skin values to canvas positions.
        // renderRadius is the max skin positional value before leaving the
        // canvas. displayRadius is half the width and height of the canvas in
        // pixels. If they are equal, there is a 1:1 relation of skin position
        // values to canvas pixels. Setting both to 200 allows 100px of space
        // around clock skins to add your own things: this is due to current
        // skins maxing out at a positional value of 100.
        this.scale = this.displayRadius / this.renderRadius;

        // Initialise canvas context
        this.ctx = this.canvas.getContext("2d");
        this.ctx.scale(this.scale,this.scale);

        // Keep track of this object
        CoolAlarmClock.config.clockTracker[this.canvasId] = this;

        // should we be running the clock?
        this.active = true;
        this.tickTimeout = null;

        this.timeleft = document.getElementById(options.canvasId+'-time-left');
        this.duration = options.duration;
        this.prealarm = options.prealarm;

        if(options.startTime)
            this.setAlarm(options.startTime);

        // Start the clock going
        this.tick();

        return this;
    },

    // Draw a circle at point x,y with params as defined in skin
    fullCircleAt: function(x,y,skin) {
        this.ctx.save();
        this.ctx.globalAlpha = skin.alpha;
        this.ctx.lineWidth = skin.lineWidth;

        if (!CoolAlarmClock.config.isIE) {
            this.ctx.beginPath();
        }

        if (CoolAlarmClock.config.isIE) {
            // excanvas doesn't scale line width so we will do it here
            this.ctx.lineWidth = this.ctx.lineWidth * this.scale;
        }

        this.ctx.arc(x, y, skin.radius, 0, 2*Math.PI, false);

        if (CoolAlarmClock.config.isIE) {
            // excanvas doesn't close the circle so let's fill in the tiny gap
            this.ctx.arc(x, y, skin.radius, -0.1, 0.1, false);
        }

        if (skin.fillColor) {
            this.ctx.fillStyle = skin.fillColor;
            this.ctx.fill();
        }
        if (skin.color) {
            this.ctx.strokeStyle = skin.color;
            this.ctx.stroke();
        }
        this.ctx.restore();
    },

    // Draw some text centered vertically and horizontally
    drawTextAt: function(theText,x,y,skin) {
        if (!skin) skin = this.getSkin();
        this.ctx.save();
        this.ctx.font = skin.font || this.font;
        var tSize = this.ctx.measureText(theText);
        // TextMetrics rarely returns a height property: use baseline instead.
        if (!tSize.height) {
            tSize.height = 0;
            this.ctx.textBaseline = 'middle';
        }
        this.ctx.fillText(theText, x - tSize.width/2, y - tSize.height/2);
        this.ctx.restore();
    },

    lpad2: function(num) {
        return (num < 10 ? '0' : '') + num;
    },

    tickAngle: function(second) {
        // Log algorithm by David Bradshaw
        var tweak = 3; // If it's lower the one second mark looks wrong (?)
        if (this.logClock) {
            return second == 0 ? 0 : (Math.log(second*tweak) / Math.log(60*tweak));
        }
        else if (this.logClockRev) {
            // Flip the seconds then flip the angle (trickiness)
            second = (60 - second) % 60;
            return 1.0 - (second == 0 ? 0 : (Math.log(second*tweak) / Math.log(60*tweak)));
        }
        else {
            return second/60.0;
        }
    },

    timeText: function(hour,min,sec) {
        var c = CoolAlarmClock.config;
        return '' +
            (c.showAmPm ? ((hour%12)==0 ? 12 : (hour%12)) : hour) + ':' +
            this.lpad2(min) +
            (c.showSecs ? ':' + this.lpad2(sec) : '') +
            (c.showAmPm ? (hour < 12 ? ' am' : ' pm') : '')
        ;
    },

    // Draw a radial line by rotating then drawing a straight line
    // Ha ha, I think I've accidentally used Taus, (see http://tauday.com/)
    radialLineAtAngle: function(angleFraction,skin) {
        this.ctx.save();
        this.ctx.translate(this.renderRadius,this.renderRadius);
        this.ctx.rotate(Math.PI * (2.0 * angleFraction - 0.5));
        this.ctx.globalAlpha = skin.alpha;
        this.ctx.strokeStyle = skin.color;
        this.ctx.lineWidth = skin.lineWidth;

        if (CoolAlarmClock.config.isIE)
            // excanvas doesn't scale line width so we will do it here
            this.ctx.lineWidth = this.ctx.lineWidth * this.scale;

        if (skin.radius) {
            this.fullCircleAt(skin.startAt,0,skin);
        }
        else {
            this.ctx.beginPath();
            this.ctx.moveTo(skin.startAt,0);
            this.ctx.lineTo(skin.endAt,0);
            this.ctx.stroke();
        }
        this.ctx.restore();
    },

    render: function(hour,min,sec) {
        // Get the skin
        var skin = this.getSkin();

        // Clear
        this.ctx.clearRect(0,0,this.renderRadius*2,this.renderRadius*2);

        // Draw the outer edge of the clock
        if (skin.outerBorder)
            this.fullCircleAt(this.renderRadius,this.renderRadius,skin.outerBorder);

        // Draw the tick marks. Every 5th one is a big one
        for (var i=0;i<60;i++) {
            (i%5)  && skin.smallIndicator && this.radialLineAtAngle(this.tickAngle(i),skin.smallIndicator);
            !(i%5) && skin.largeIndicator && this.radialLineAtAngle(this.tickAngle(i),skin.largeIndicator);
        }

        // Write the time
        if (this.showDigital) {
            this.drawTextAt(
                this.timeText(hour,min,sec),
                this.renderRadius,
                this.renderRadius+this.renderRadius/2
            );
        }

        var hourA = (hour%12)*5 + min/12.0,
            minA = min + sec/60.0,
            secA = sec;

        // Draw the hands
        if (skin.hourHand)
            this.radialLineAtAngle(this.tickAngle(hourA),skin.hourHand);

        if (skin.minuteHand)
            this.radialLineAtAngle(this.tickAngle(minA),skin.minuteHand);

        if (this.showSecondHand && skin.secondHand)
            this.radialLineAtAngle(this.tickAngle(secA),skin.secondHand);

        // Hands decoration - not in IE
        if  (!CoolAlarmClock.config.isIE) {
            if (skin.hourDecoration)
                this.radialLineAtAngle(this.tickAngle(hourA), skin.hourDecoration);

            if (skin.minDecoration)
                this.radialLineAtAngle(this.tickAngle(minA), skin.minDecoration);

            if (this.showSecondHand && skin.secondDecoration)
                this.radialLineAtAngle(this.tickAngle(secA),skin.secondDecoration);
        }

        if(this.alarmTime) {
            this.showAlarm(skin);
        }

        if (this.extraRender) {
            this.extraRender(hour,min,sec);
        }
    },

    // Check the time and display the clock
    refreshDisplay: function() {
        var now = new Date();
        if (this.gmtOffset != null) {
            // Use GMT + gmtOffset
            var offsetNow = new Date(now.valueOf() + (this.gmtOffset * 1000 * 60 * 60));
            this.render(offsetNow.getUTCHours(),offsetNow.getUTCMinutes(),offsetNow.getUTCSeconds());
        }
        else {
            // Use local time
            this.render(now.getHours(),now.getMinutes(),now.getSeconds());
        }
        if(this.alarmTime) {
            this.checkAlarm(now);
        }
    },

    // Set timeout to trigger a tick in the future
    nextTick: function() {
        this.tickTimeout = setTimeout("CoolAlarmClock.config.clockTracker['"+this.canvasId+"'].tick()",this.tickDelay);
    },

    // Check the canvas element hasn't been removed
    stillHere: function() {
        return document.getElementById(this.canvasId) != null;
    },

    // Stop this clock
    stop: function() {
        this.active = false;
        clearTimeout(this.tickTimeout);
    },

    // Start this clock
    start: function() {
        if (!this.active) {
            this.active = true;
            this.tick();
        }
    },

    // Main tick handler. Refresh the clock then setup the next tick
    tick: function() {
        if (this.stillHere() && this.active) {
            this.refreshDisplay();
            this.nextTick();
        }
    },

    getSkin: function() {
        var skin = CoolAlarmClock.config.skins[this.skinId];
        if (!skin) skin = CoolAlarmClock.config.skins[CoolAlarmClock.config.defaultSkin];
        return skin;
    },

    setDelayedStart: function(delay) {
        if(!delay) {
            this.setAlarm();
            soundManager.play('start');
        } else {
            if(delay % 2000) {
                soundManager.play('tic');
            } else {
                soundManager.play('tac');
            }
            this.timeleft.innerHTML = '-' + (delay/1000) + '"';
            delay -= 1000;
            if(this.delayedStart<=0) {
                this.setAlarm();
                soundManager.play('start');
            }
            setTimeout("CoolAlarmClock.config.clockTracker['"+this.canvasId+"'].setDelayedStart(" + delay + ")", 1000);
        }
    },

    setAlarm: function(now) {
        if(!now) {
            now = new Date();
            if(this.notifyStart) {
                var xhr = new XMLHttpRequest();
                xhr.open("POST", this.notifyStart + '&start=' + now.getTime(), true);
                xhr.send();
            }
        }
        var alarm = new Date(now.getTime() + this.duration*60*1000);
        var prealarm = new Date(now.getTime() + (this.duration - this.prealarm)*60*1000);
        var lastminute = new Date(alarm.getTime() - 60000);
        this.startTime = now;
        this.alarmTime = alarm;
        this.preAlarmTime = prealarm;
        this.lastMinute = lastminute;
        this.timeleft.innerHTML = this.duration + "'<br/>00\"";
        this.showAlarm(CoolAlarmClock.config.skins[this.skinId]);
    },

    showAlarm: function(skin) {
        var secs = this.startTime.getSeconds() / 60;
        var smin = this.startTime.getMinutes() + secs;
        var pmin = this.preAlarmTime.getMinutes() + secs;
        var amin = this.alarmTime.getMinutes() + secs;
        this.radialLineAtAngle((smin/60), skin.startDecoration);
        this.radialLineAtAngle((pmin/60), skin.preAlarmDecoration);
        this.radialLineAtAngle((amin/60), skin.alarmDecoration);
    },

    checkAlarm: function(t) {
        if(this.alarmTime) {
            var left = ((this.alarmTime - t)/1000) / 60;
            if(left > 0) {
                var leftmins = parseInt(left);
                var leftsecs = parseInt((left-leftmins)*60);
                if(leftmins>0) {
                    this.timeleft.innerHTML = leftmins + "'<br/>" + leftsecs + '"';
                } else {
                    this.timeleft.innerHTML = leftsecs + '"';
                }
            } else {
                this.timeleft.innerHTML = 'STOP';
            }
            if(t>this.preAlarmTime) {
                if(!this.showSecondHand) {
                    this.showSecondHand = true;
                    soundManager.play('prealarm');
                } else {
                    if(t>this.lastMinute) {
                        var sec = t.getSeconds();
                        if(sec != this.lastTickedSecond) {
                            if(sec % 2) {
                                soundManager.play('tic');
                            } else {
                                soundManager.play('tac');
                            }
                            this.lastTickedSecond = sec;
                        }
                    }
                    if(t>this.alarmTime) {
                        this.startTime = null;
                        this.alarmTime = null;
                        this.showSecondHand = false;
                        this.lastTickedSecond = null;
                        soundManager.play('stop');
                    }
                }
            }
        }
    }
};

// Find all canvas elements that have the CoolAlarmClock class and turns them into clocks
CoolAlarmClock.findAndCreateClocks = function() {
    // (Let's not use a jQuery selector here so it's easier to use frameworks other than jQuery)
    var canvases = document.getElementsByTagName("canvas");
    for (var i=0;i<canvases.length;i++) {
        // Pull out the fields from the class. Example "CoolAlarmClock:chunkySwissOnBlack:1000"
        var fields = canvases[i].className.split(" ")[0].split(":");
        if (fields[0] == "CoolAlarmClock") {
            if (!canvases[i].id) {
                // If there's no id on this canvas element then give it one
                canvases[i].id = '_coolclock_auto_id_' + CoolAlarmClock.config.noIdCount++;
            }
            var restartmsg = canvases[i].attributes.getNamedItem('confirmrestart');
            if(restartmsg)
                restartmsg = restartmsg.value;
            var notifystart = canvases[i].attributes.getNamedItem('notifystart');
            if(notifystart)
                notifystart = notifystart.value;

            // Create a clock object for this element
            var cac = new CoolAlarmClock({
                canvasId:       canvases[i].id,
                skinId:         fields[1],
                displayRadius:  fields[2]!='' ? parseInt(fields[2]) : window.innerHeight/2.5,
                showSecondHand: fields[3]!='noSeconds',
                gmtOffset:      fields[4],
                showDigital:    fields[5]=='showDigital',
                logClock:       fields[6]=='logClock',
                logClockRev:    fields[6]=='logClockRev',
                duration:       fields[7]!=='' ? parseInt(fields[7]) : 45,
                prealarm:       fields[8]!=='' ? parseInt(fields[8]) : 5,
                startTime:      fields[9] ? new Date(parseInt(fields[9], 10)) : null,
                confirmRestart: restartmsg,
                notifyStart:    notifystart
            });

            canvases[i].startCountdown = canvases[i].ondblclick = function() {
                if(cac.startTime && cac.confirmRestart) {
                    if(!window.confirm(cac.confirmRestart))
                        return;
                }
                cac.setAlarm();
                soundManager.play('start');
            };

            canvases[i].startDelayedCountdown = function(delay) {
                if(!cac.startTime) cac.setDelayedStart(delay);
            };

            canvases[i].getClock = function() {
                return cac;
            };
        }
    }
};

// If you don't have jQuery then you need a body onload like this: <body onload="CoolAlarmClock.findAndCreateClocks()">
// If you do have jQuery and it's loaded already then we can do it right now
if (window.jQuery) {
    jQuery(document).ready(CoolAlarmClock.findAndCreateClocks);
} else {
    var oldonload = window.onload;
    if (typeof window.onload != 'function')
        window.onload = CoolAlarmClock.findAndCreateClocks;
    else
        window.onload = function() {
            oldonload();
            CoolAlarmClock.findAndCreateClocks();
        };
}
