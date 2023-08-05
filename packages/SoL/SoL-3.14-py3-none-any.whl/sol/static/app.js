/* coding: utf-8 -*- */

/*jsl:declare Ext*/

Ext.Loader.setPath({
    MP: '/desktop/js'
});

Ext.application({
    name: 'SoL',
    appFolder: '/static/app',
    controllers: [
        'Login'
    ],

    launch: function() {
        Ext.BLANK_IMAGE_URL = '/static/images/s.gif';
        Ext.create('SoL.window.Login', {}).show();
    }
});
