// -*- coding: utf-8 -*-
// :Progetto:  SoL -- Authentication form UI
// :Creato:    lun 15 apr 2013 11:35:31 CEST
// :Autore:    Lele Gaifax <lele@metapensiero.it>
// :Licenza:   GNU General Public License version 3 or later
//

/*jsl:declare Ext*/
/*jsl:declare _*/

Ext.define('SoL.window.Login', {
    extend: 'MP.window.Login',

    initComponent: function() {
        var me = this;

        me.callParent(arguments);

        var version = me.getDockedItems('toolbar[dock="bottom"] > label')[0];
        version.setText(
            Ext.String.format('<a href="{0}" target="_blank">{1}</a> &mdash; <a href="{2}" target="_blank">{3}</a>',
                              "https://pypi.python.org/pypi/SoL/#changes",
                              version.text,
                              "/static/manual/index.html",
                              _('About…')), false);
    },

    getFormFields: function() {
        var me = this;
        var fields = this.callParent();

        // Put a container with a logo and a description above the form fields

        fields.unshift({
            xtype: 'container',
            height: 100,
            html: [
                '<a href="/lit" data-qtip="',
                _('Go to the light HTML only interface…').replace(/"/g, '”'),
                '" target="_blank">',
                '  <img src="/static/images/logo.png"',
                '       style="margin-top: 15px; margin-left: 20px; float: left;">',
                '</a>',
                '<div style="margin-top: 25px; text-align: center;">',
                '<b>Scarry On Line</b><br/><br/>',
                _('Carrom tournaments management'),
                '</div>'
            ].join('')
        });

        return fields;
    }
});
