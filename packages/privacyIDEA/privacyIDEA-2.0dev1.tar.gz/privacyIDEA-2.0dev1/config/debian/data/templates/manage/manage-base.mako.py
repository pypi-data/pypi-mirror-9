# -*- coding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 9
_modified_time = 1422216485.066585
_enable_loop = True
_template_filename = u'/usr/lib/python2.7/dist-packages/privacyidea/templates/manage/manage-base.mako'
_template_uri = u'/manage/manage-base.mako'
_source_encoding = 'utf-8'
from webhelpers.html import escape
_exports = []


def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        sorted = context.get('sorted', UNDEFINED)
        c = context.get('c', UNDEFINED)
        self = context.get('self', UNDEFINED)
        _ = context.get('_', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 2
        __M_writer(u'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">\n<html>\n<head>\n<title>')
        # SOURCE LINE 5
        __M_writer(escape(_("privacyIDEA Management")))
        __M_writer(u'</title>\n\n<meta name="author" content="Cornelius K\xf6lbel" >\n<meta name="date" content="2014-08-03T18:39:14+0200" >\n<meta name="copyright" content="LSE Leading Security Experts GmbH">\n<meta name="keywords" content="privacyIDEA manage">\n<meta http-equiv="content-type" content="text/html; charset=UTF-8">\n<meta http-equiv="content-type" content="application/xhtml+xml; charset=UTF-8">\n<meta http-equiv="content-style-type" content="text/css">\n\n<link type="text/css" rel="stylesheet" href="/manage/style.css"/>\n<link type="text/css" rel="stylesheet" href="/manage/custom-style.css"/>\n\n<link type="text/css" rel="stylesheet" href="/css/smoothness/jquery-ui-1.8.21.custom.css" />\n\n<link type="text/css" rel="stylesheet" href="/css/flexigrid/flexigrid.css">\n<link type=\'text/css\' rel=\'stylesheet\' media=\'screen\' href=\'/css/superfish.css\' />\n\n<script type="text/javascript" src="/js/jquery-1.7.2.min.js"></script>\n<script type="text/javascript" src="/js/jquery.cookie.js"></script>\n<script type="text/javascript" src="/js/jquery.tools.min.js"></script>\n<script type="text/javascript" src="/js/jquery-ui-1.8.21.custom.min.js"></script>\n<script type="text/javascript" src="/js/jquery.validate.js"></script>\n<script type="text/javascript" src="/js/jquery.form.js"></script>\n<script type="text/javascript" src="/js/flexigrid.js"></script>\n<script type=\'text/javascript\' src=\'/js/superfish.js\'></script>\n\n<script type="text/javascript" src="/js/privacyidea_utils.js"></script>\n\n<script type="text/javascript" src="/js/aladdin.js"></script>\n<script type="text/javascript" src="/js/oathcsv.js"></script>\n<script type="text/javascript" src="/js/yubikeycsv.js"></script>\n<script type="text/javascript" src="/js/feitian.js"></script>\n<script type="text/javascript" src="/js/dpw.js"></script>\n<script type="text/javascript" src="/js/dat.js"></script>\n<script type="text/javascript" src="/js/vasco.js"></script>\n<script type="text/javascript" src="/js/pskc.js"></script>\n<script type="text/javascript" src="/js/tools.js"></script>\n<script type="text/javascript" src="/js/machines.js"></script>\n<script type="text/javascript" src="/js/manage.js"></script>\n\n</head>\n<body>\n\n<div id="wrap">\n\n<ul id=\'menu\' class=\'sf-menu sf-vertical ui-widget-header ui-widget ui-widget-content ui-corner-all\'>\n    <li><a href=\'#\'>')
        # SOURCE LINE 52
        __M_writer(escape(_("Config")))
        __M_writer(u"</a>\n        <ul>\n            <li><a href='#' id='menu_edit_resolvers'>")
        # SOURCE LINE 54
        __M_writer(escape(_("useridresolvers")))
        __M_writer(u"</a></li>\n            <li><a href='#' id='menu_edit_realms'>")
        # SOURCE LINE 55
        __M_writer(escape(_("realms")))
        __M_writer(u"</a></li>\n            <li><a href='#' id='menu_system_config'>")
        # SOURCE LINE 56
        __M_writer(escape(_("System Config")))
        __M_writer(u"</a></li>\n            <li><a href='#' id='menu_token_config'>")
        # SOURCE LINE 57
        __M_writer(escape(_("Token Config")))
        __M_writer(u"</a></li>\n            <li><a href='#' id='menu_policies'>")
        # SOURCE LINE 58
        __M_writer(escape(_("Policies")))
        __M_writer(u"</a></li>\n        </ul>\n    </li>\n    <li><a href='#'>")
        # SOURCE LINE 61
        __M_writer(escape(_("Tools")))
        __M_writer(u"</a>\n\t\t  <ul>\n            <li><a href='#' id='menu_tools_getserial'>")
        # SOURCE LINE 63
        __M_writer(escape(_("Get Serial by OTP")))
        __M_writer(u"</a></li>\n            <li><a href='#' id='menu_tools_copytokenpin'>")
        # SOURCE LINE 64
        __M_writer(escape(_("Copy Token PIN")))
        __M_writer(u"</a></li>\n            <li><a href='#' id='menu_tools_checkpolicy'>")
        # SOURCE LINE 65
        __M_writer(escape(_("Check Policy")))
        __M_writer(u'</a></li>\n            <li><a href="#">')
        # SOURCE LINE 66
        __M_writer(escape(_("Export")))
        __M_writer(u"</a>\n            \t<ul>\n            \t<li><a href='#' id='menu_tools_exporttoken'>")
        # SOURCE LINE 68
        __M_writer(escape(_("Token information")))
        __M_writer(u"</a></li>\n            \t<li><a href='#' id='menu_tools_exportaudit'>")
        # SOURCE LINE 69
        __M_writer(escape(_("Audit information")))
        __M_writer(u"</a></li>\n            \t</ul>\n            </li>\n            <li><a href='#' id='menu_tools_init'>")
        # SOURCE LINE 72
        __M_writer(escape(_("Create default realm with local users")))
        __M_writer(u"</a></li>\n        </ul>\n    </li>\n    <li><a href='#'>")
        # SOURCE LINE 75
        __M_writer(escape(_("Import Token File")))
        __M_writer(u"</a>\n\t\t  <ul>\n            <li><a href='#' id='menu_load_aladdin_xml_tokenfile'>")
        # SOURCE LINE 77
        __M_writer(escape(_("SafeNet/ Aladdin XML")))
        __M_writer(u"</a></li>\n            <li><a href='#' id='menu_load_oath_csv_tokenfile'>")
        # SOURCE LINE 78
        __M_writer(escape(_("OATH csv")))
        __M_writer(u"</a></li>\n            <li><a href='#' id='menu_load_yubikey_csv_tokenfile'>")
        # SOURCE LINE 79
        __M_writer(escape(_("Yubikey csv")))
        __M_writer(u'</a></li>\n\n')
        # SOURCE LINE 81
        for id in c.importers:
            # SOURCE LINE 82
            __M_writer(u"\t\t<li><a href='#' id='menu_load_")
            __M_writer(escape(id))
            __M_writer(u"'>")
            __M_writer(escape(c.importers[id]))
            __M_writer(u'</a></li>\n')
        # SOURCE LINE 84
        __M_writer(u'\t\t</ul>\n    </li>\n    <li><a href=\'#\' id="menu_help">')
        # SOURCE LINE 86
        __M_writer(escape(_("Help")))
        __M_writer(u"</a>\n        <ul>\n        <li><a href='")
        # SOURCE LINE 88
        __M_writer(escape(c.help_url))
        __M_writer(u'\' target="_blank" id="menu_help_online">')
        __M_writer(escape(_("Online Help")))
        __M_writer(u'</a></li>\n        <li><a href=\'#\' id="menu_help_about">')
        # SOURCE LINE 89
        __M_writer(escape(_("About")))
        __M_writer(u"</a></li>\n        </ul>\n    </li>\n    <li>\n      <a href='#'>")
        # SOURCE LINE 93
        __M_writer(escape(c.admin))
        __M_writer(u'</a>\n    \t<ul>\n    \t<li><a href="/">')
        # SOURCE LINE 95
        __M_writer(escape(_("Selfservice")))
        __M_writer(u'</a></li>\n    \t<li><a href="')
        # SOURCE LINE 96
        __M_writer(escape(c.logout_url))
        __M_writer(u'">')
        __M_writer(escape(_("Logout")))
        __M_writer(u'</a></li>\n    \t</ul>\n    </li>\n</ul>\n\n<div class="javascript_error" id="javascript_error">\n\t')
        # SOURCE LINE 102
        __M_writer(escape(_("You need to enable Javascript to use the privacyIDEA Management Web UI.")))
        __M_writer(u'\n</div>\n\n\n<div class="simple_overlay" id="do_waiting">\n\t<img src="/images/ajax-loader.gif" border="0" alt=""> ')
        # SOURCE LINE 107
        __M_writer(escape(_("Communicating with privacyIDEA server...")))
        __M_writer(u'\n</div>\n\n<div id="left_and_right">\n<div id="sidebar">\n\n')
        # SOURCE LINE 113
        __M_writer(escape(self.sidebar()))
        __M_writer(u'\n\n</div> <!-- sidebar -->\n\n')
        # SOURCE LINE 117
        __M_writer(escape(self.body()))
        __M_writer(u'\n\n</div>\n<div id="footer">\n')
        # SOURCE LINE 121
        __M_writer(escape(c.version))
        __M_writer(u' | ')
        __M_writer(escape(c.licenseinfo))
        __M_writer(u'\n</div>\n\n<div id="alert_box">\n    <span id="alert_box_text"> </span>\n</div>\n\n<span id="include_footer"> </span>\n\n<div id="all_dialogs" style="display:none; height:0px;">\n<!-- ############ DIALOGS ######################### -->\n<div id=dialog_about>\n<div id=about_tabs>\n<ul>\n  <li><a href="#about1">Trivia</a>\n  <li><a href="#about2">')
        # SOURCE LINE 136
        __M_writer(escape(_("Contact")))
        __M_writer(u'</a>\n  <li><a href="#about3">')
        # SOURCE LINE 137
        __M_writer(escape(_("License")))
        __M_writer(u'</a>\n</ul>\n<div id=about1>\n<p>\n')
        # SOURCE LINE 141
        __M_writer(escape(_("""privacyIDEA is a modular authentication system. Originally for OTP  
authentication devices. But other >>devices<< like challenge response 
and SSH keys are coming up.""")))
        # SOURCE LINE 143
        __M_writer(u'</p>\n<h2>')
        # SOURCE LINE 144
        __M_writer(escape(_("Openness and Transparency")))
        __M_writer(u'</h2>\n<p>\n')
        # SOURCE LINE 146
        __M_writer(escape(_("""privacyIDEA tries to be open in many ways. We try to provide best transparency:
We host our code on github, so that you can monitor the development. 
The issue tracker at github is used, so that you can see, which topic is hot, 
what is coming up in the future and actually add your own requests! 
New features are planned in the github wiki. We are using travis-ci.org 
to run our tests. You can see which tests pass and also which test fail!
Yes, code breaks and tests fail.""")))
        # SOURCE LINE 152
        __M_writer(u'\n</p><p>\n')
        # SOURCE LINE 154
        __M_writer(escape(_("""privacyIDEA is not ruled by a single company
(although at the moment only one company is involved).
Thus when using privacyIDEA or getting involved you are not at the mercy of
 one single, revenue driven decision maker.""")))
        # SOURCE LINE 157
        __M_writer(u'\n</p>\n<p>\n<a href="https://www.privacyidea.org/about/about-the-name-privacyidea/"\n    target="_about">')
        # SOURCE LINE 161
        __M_writer(escape(_("Read more about the name privacyIDEA")))
        __M_writer(u'</a>\n</p>\n<p class=unimportant>\n')
        # SOURCE LINE 164
        __M_writer(escape(_("""privacyIDEA is a fork of LinOTP""")))
        __M_writer(u'<br>\n')
        # SOURCE LINE 165
        __M_writer(escape(_("""(c) 2010-2014 LSE Leading Security Experts GmbH""")))
        __M_writer(u'\n</p>\n</div>\n<div id=about2>\n<a href="http://www.privacyidea.org" target="_webpage">http://www.privacyidea.org</a>\n</div>\n<div id=about3>\n<p>\n')
        # SOURCE LINE 173
        __M_writer(escape(_("""The complete code is licensed under AGPLv3.""")))
        __M_writer(u'\n</p>\n</div>\n</div>  <!-- about-tabs -->\n</div>  <!-- about-dialog -->\n<script>\n$(\'#about_tabs\').tabs();\nfunction translate_about_dialog() {\n        $("#dialog_about" ).dialog( "option", "title", \'')
        # SOURCE LINE 181
        __M_writer(escape(_("About privacyIDEA")))
        __M_writer(u"' );\n        $('#button_about_dialog_close .ui-button-text').html('")
        # SOURCE LINE 182
        __M_writer(escape(_("close")))
        __M_writer(u'\');\n}\n</script>\n<!-- ############ system settings ################# -->\n<div id=dialog_system_settings>\n<form class="cmxform" id="form_sysconfig">\n\t<div id=\'tab_system_settings\'>\n\t\t<ul id=\'config_tab_index\'>\n\t\t\t<li><a href=\'#tab_content_system_settings\'>')
        # SOURCE LINE 190
        __M_writer(escape(_("Settings")))
        __M_writer(u"</a></li>\n\t\t\t<li><a href='#tab_content_system_defaults'>")
        # SOURCE LINE 191
        __M_writer(escape(_("Token defaults")))
        __M_writer(u"</a></li>\n\t\t\t<li><a href='#tab_content_system_gui'>")
        # SOURCE LINE 192
        __M_writer(escape(_("GUI settings")))
        __M_writer(u'</a></li>\n\t\t</ul>\n\t\t<div id="tab_content_system_settings">\n\t\t\t<div style="float:right">\n\t\t\t<a href=\'')
        # SOURCE LINE 196
        __M_writer(escape(c.help_url))
        __M_writer(u'/configuration/system_config.html#settings\' target="_blank">\n\t\t\t<img alt="(?)" width=24\n\t\t\tsrc="/images/help32.png"  \n\t\t\ttitle=\'')
        # SOURCE LINE 199
        __M_writer(escape(_("Open help on system settings")))
        __M_writer(u'\'>\n\t\t\t</a>\n\t\t\t</div>\n\t\t\t<fieldset>\n\t\t\t\t<table>\n         \t\t\t<tr><td><label for="sys_splitAtSign">')
        # SOURCE LINE 204
        __M_writer(escape(_("splitAtSign")))
        __M_writer(u'</label>: </td>\n         \t\t\t\t<td><input type="checkbox" name="sys_splitAtSign" id="sys_splitAtSign" value="sys_splitAtSign"\n         \t\t\t\t\ttitle="')
        # SOURCE LINE 206
        __M_writer(escape(_('This will use the part right of an @-sign as realm')))
        __M_writer(u'"></td></tr>\n         \t\t\t<tr><td><label for="sys_allowSamlAttributes">')
        # SOURCE LINE 207
        __M_writer(escape(_("Return SAML Attributes")))
        __M_writer(u'</label>: </td>\n\t\t    \t\t\t<td><input type="checkbox" name="sys_allowSamlAttributes" id="sys_allowSamlAttributes" value="sys_allowSamlAttributes"\n\t\t    \t\t\t\ttitle="')
        # SOURCE LINE 209
        __M_writer(escape(_('The /validate/samlcheck controller will also return user attributes')))
        __M_writer(u'"></td></tr>\n         \t\t\t<tr><td><label for="sys_failCounterInc">')
        # SOURCE LINE 210
        __M_writer(escape(_("FailCounterIncOnFalsePin")))
        __M_writer(u'</label>: </td>\n         \t\t\t\t<td><input type="checkbox" name="sys_failCounterInc" id="sys_failCounterInc" value="sys_failCounterInc"\n         \t\t\t\t\ttitle="')
        # SOURCE LINE 212
        __M_writer(escape(_('This will increase the failcounter, if the user provided a wrong PIN.')))
        __M_writer(u'"></td></tr>\n         \t\t\t<tr><td><label for="sys_prependPin">')
        # SOURCE LINE 213
        __M_writer(escape(_("PrependPin")))
        __M_writer(u': </label></td>\n         \t\t\t\t<td><input type="checkbox" name="sys_prependPin" id="sys_prependPin" value="sys_prependPin" id="sys_prependPin"\n         \t\t\t\t\ttitle="')
        # SOURCE LINE 215
        __M_writer(escape(_('This will prepend the PIN to the OTP value. Otherwise the PIN will be appended.')))
        __M_writer(u'"></td></tr>\n\t\t\t\t\t<tr><td><label for="sys_autoResync"> ')
        # SOURCE LINE 216
        __M_writer(escape(_("Auto resync")))
        __M_writer(u': </label></td>\n         \t\t\t\t<td><input type="checkbox" name="sys_autoResync" id="sys_autoResync" value="sys_autoResync"\n         \t\t\t\t\ttitle="')
        # SOURCE LINE 218
        __M_writer(escape(_('This will automatically resync OTP counter of HMAC based tokens.')))
        __M_writer(u'"></td></tr>\n\t\t \t\t\t<tr><td><label for="sys_autoResyncTimeout"> ')
        # SOURCE LINE 219
        __M_writer(escape(_("Auto resync timeout")))
        __M_writer(u': </label></td>\n\t\t   \t\t\t\t<td><input type="text" name="sys_autoResyncTimeout" class="required"  id="sys_autoResyncTimeout"\n\t\t   \t\t\t\t\ttitle="')
        # SOURCE LINE 221
        __M_writer(escape(_('The time in which the two successive OTP values need to be entered (in seconds)')))
        __M_writer(u'"\n\t\t   \t\t\t\t\t size="4" maxlength="3"></td></tr>\n\t\t\t\t</table>\n\t\t\t</fieldset>\n    \t\t<fieldset>\n    \t\t\t<legend>')
        # SOURCE LINE 226
        __M_writer(escape(_("Authentication")))
        __M_writer(u'</legend>\n    \t\t\t<table>\n    \t\t\t\t<tr><td><label for=sys_passOnUserNotFound>')
        # SOURCE LINE 228
        __M_writer(escape(_("Pass on user not found")))
        __M_writer(u': </label></td>\n         \t\t\t\t<td><input type="checkbox" name="sys_passOnUserNotFound" id="sys_passOnUserNotFound" value="sys_passOnUserNotFound"\n         \t\t\t\t\ttitle="')
        # SOURCE LINE 230
        __M_writer(escape(_('If checked, users who are not found in the useridresolvers are authenticated successfully. USE WITH CAUTION!')))
        __M_writer(u'"></td></tr>\n\t\t   \t\t\t<tr><td><label for=sys_passOnUserNoToken>')
        # SOURCE LINE 231
        __M_writer(escape(_("Pass on user no token")))
        __M_writer(u': </label></td>\n         \t\t\t\t<td><input type="checkbox" name="sys_passOnUserNoToken" id="sys_passOnUserNoToken" value="sys_passOnUserNoToken"\n\t\t\t\t\t\t\ttitle="')
        # SOURCE LINE 233
        __M_writer(escape(_('If checked, users who have no token get authenticated automatically successful. USE WITH CAUTION!')))
        __M_writer(u'"></td></tr>\n\t\t\t\t</table>\n\t\t\t</fieldset>\n\t\t\t<fieldset>\n\t\t\t\t<legend>')
        # SOURCE LINE 237
        __M_writer(escape(_("Authorization")))
        __M_writer(u'</legend>\n\t\t\t\t\t<label for=sys_mayOverwriteClient>')
        # SOURCE LINE 238
        __M_writer(escape(_("Override Authentication client")))
        __M_writer(u':</label>\n\t\t\t\t\t<input type=\'text\' name=\'sys_mayOverwriteClient\' id=\'sys_mayOverwriteClient\' size=\'40\'\n\t\t\t\t\ttitle="')
        # SOURCE LINE 240
        __M_writer(escape(_('This is a comma separated list of clients, that may send another client IP for authorization policies.')))
        __M_writer(u'">\n\t\t\t</fieldset>\n\t\t    <fieldset id=\'ocra_config\'>\n\t\t    \t<legend>')
        # SOURCE LINE 243
        __M_writer(escape(_("OCRA settings")))
        __M_writer(u'</legend>\n\t\t    \t<table>\n\t\t    \t\t<tr><td><label for=ocra_max_challenge>')
        # SOURCE LINE 245
        __M_writer(escape(_("maximum concurrent OCRA challenges")))
        __M_writer(u'</label></td>\n\t\t    \t\t\t<td><input type="text" id="ocra_max_challenge" maxlength="4" class=integer\n\t\t    \t\t\t\ttitle=\'')
        # SOURCE LINE 247
        __M_writer(escape(_("This is the maximum concurrent challenges per OCRA Token.")))
        __M_writer(u"'/></td></tr>\n\t\t    \t\t<tr><td><label for=ocra_challenge_timeout>")
        # SOURCE LINE 248
        __M_writer(escape(_("OCRA challenge timeout")))
        __M_writer(u'</label></td>\n\t\t    \t\t\t<td><input type="text" id="ocra_challenge_timeout" maxlength="6"\n\t\t    \t\t\t\ttitle=\'')
        # SOURCE LINE 250
        __M_writer(escape(_("After this time a challenge can not be used anymore. Valid entries are like 1D, 2H or 5M where D=day, H=hour, M=minute.")))
        __M_writer(u'\'></td></tr>\n\t\t    \t</table>\n\t\t    </fieldset>\n    </div> <!-- tab with settings -->\n    \t<div id=\'tab_content_system_defaults\'>\n    \t\t<div style="float:right">\n\t\t\t<a href=\'')
        # SOURCE LINE 256
        __M_writer(escape(c.help_url))
        __M_writer(u'/configuration/system_config.html#token-default-settings\' target="_blank">\n\t\t\t<img alt="(?)" width=24\n\t\t\tsrc="/images/help32.png"  \n\t\t\ttitle=\'')
        # SOURCE LINE 259
        __M_writer(escape(_("Open help on system settings")))
        __M_writer(u"'>\n\t\t\t</a>\n\t\t\t</div>\n    \t\t<fieldset>\n    \t\t\t<legend>")
        # SOURCE LINE 263
        __M_writer(escape(_("Misc settings")))
        __M_writer(u'</legend>\n\t\t\t\t<table>\n    \t\t\t\t<tr><td><label for=sys_resetFailCounter>')
        # SOURCE LINE 265
        __M_writer(escape(_("DefaultResetFailCount")))
        __M_writer(u':</label></td>\n\t\t\t\t\t\t<td><input type="checkbox" name="sys_resetFailCounter" id="sys_resetFailCounter" value="sys_resetFailCounter"\n\t\t\t\t\t\t\ttitle=\'')
        # SOURCE LINE 267
        __M_writer(escape(_("Will reset the fail counter when the user authenticated successfully")))
        __M_writer(u"'></td></tr>\n\t       \t\t\t<tr><td><label for=sys_maxFailCount> ")
        # SOURCE LINE 268
        __M_writer(escape(_("DefaultMaxFailCount")))
        __M_writer(u': </label></td>\n         \t\t\t\t<td><input type="text" name="sys_maxFailCount" class="required"  id="sys_maxFailCount" size="4" maxlength="3"\n         \t\t\t\t\ttitle=\'')
        # SOURCE LINE 270
        __M_writer(escape(_("This is the maximum allowed failed logins for a new enrolled token.")))
        __M_writer(u"'></td></tr>\n\t\t\t\t\t<tr><td><label for=sys_syncWindow> ")
        # SOURCE LINE 271
        __M_writer(escape(_("DefaultSyncWindow")))
        __M_writer(u': </label></td>\n         \t\t\t\t<td><input type="text" name="sys_syncWindow" class="required"  id="sys_syncWindow" size="4" maxlength="6"\n         \t\t\t\t\ttitle=\'')
        # SOURCE LINE 273
        __M_writer(escape(_("A new token will have this windows to do the manual or automatic OTP sync.")))
        __M_writer(u"'></td></tr>\n         \t\t\t<tr><td><label for=sys_otpLen> ")
        # SOURCE LINE 274
        __M_writer(escape(_("DefaultOtpLen")))
        __M_writer(u': </label></td>\n         \t\t\t\t<td><input type="text" name="sys_otpLen" class="required"  id="sys_otpLen" size="4" maxlength="1"\n         \t\t\t\t\ttitle=\'')
        # SOURCE LINE 276
        __M_writer(escape(_("A new token will be set to this OTP length.")))
        __M_writer(u"'></td></tr>\n         \t\t\t<tr><td><label for=sys_countWindow> ")
        # SOURCE LINE 277
        __M_writer(escape(_("DefaultCountWindow")))
        __M_writer(u': </label></td>\n         \t\t\t\t<td><input type="text" name="sys_countWindow" class="required"  id="sys_countWindow" size="4" maxlength="3"\n         \t\t\t\t\ttitle=\'')
        # SOURCE LINE 279
        __M_writer(escape(_("This is the default look ahead window for counter based tokens.")))
        __M_writer(u"'></td></tr>\n\t\t\t\t<tr><td><label for='sys_challengeTimeout'> ")
        # SOURCE LINE 280
        __M_writer(escape(_("DefaultChallengeValidityTime")))
        __M_writer(u': </label></td>\n\t\t\t\t\t<td><input type="text" name="sys_challengeTimeout" class="required"  id="sys_challengeTimeout" size="4" maxlength="3"\n\t\t\t\t\t\ttitle=\'')
        # SOURCE LINE 282
        __M_writer(escape(_("Default validity timeframe of a challenge.")))
        __M_writer(u"' value=120></td></tr>\n\n\t\t\t\t</table>\n\t\t\t</fieldset>\n    \t\t<fieldset>\n    \t\t\t<legend>")
        # SOURCE LINE 287
        __M_writer(escape(_("OCRA settings")))
        __M_writer(u'</legend>\n    \t\t\t<table>\n    \t\t\t\t<tr><td><label for=ocra_default_suite>')
        # SOURCE LINE 289
        __M_writer(escape(_("default OCRA suite")))
        __M_writer(u'</label></td>\n    \t\t\t\t\t<td><input type="text" name="ocra_default_suite" id="ocra_default_suite" size=\'30\' maxlength="40"\n    \t\t\t\t\t\ttitle="')
        # SOURCE LINE 291
        __M_writer(escape(_('This is the suite for newly enrolled OCRA tokens. Default is OCRA-1:HOTP-SHA256-8:C-QA08')))
        __M_writer(u'"></td></tr>\n    \t\t\t\t<tr><td><label for=ocra_default_qr_suite>')
        # SOURCE LINE 292
        __M_writer(escape(_("default QR suite")))
        __M_writer(u'</label></td>\n    \t\t\t\t\t<td><input type="text" name="ocra_default_qr_suite" id="ocra_default_qr_suite" maxlength=40 size=30\n    \t\t\t\t\t\ttitle=\'')
        # SOURCE LINE 294
        __M_writer(escape(_("This is the suite for newly enrolled QR tokens. Default is OCRA-1:HOTP-SHA256-6:C-QA64")))
        __M_writer(u'\'></td></tr>\n    \t\t\t</table>\n    \t\t</fieldset>\n    \t</div> <!-- tab with defaults -->\n    \t<div id=\'tab_content_system_gui\'>\n    \t\t<div style="float:right">\n\t\t\t<a href=\'')
        # SOURCE LINE 300
        __M_writer(escape(c.help_url))
        __M_writer(u'/configuration/system_config.html#gui-settings\' target="_blank">\n\t\t\t<img alt="(?)" width=24\n\t\t\tsrc="/images/help32.png"  \n\t\t\ttitle=\'')
        # SOURCE LINE 303
        __M_writer(escape(_("Open help on system settings")))
        __M_writer(u"'>\n\t\t\t</a>\n\t\t\t</div>\n    \t\t<fieldset>\n    \t\t\t\t<legend>")
        # SOURCE LINE 307
        __M_writer(escape(_("Login dialog")))
        __M_writer(u'</legend>\n\t\t    \t\t<table>\n\t\t    \t\t\t<tr><td><label for=sys_realmbox>')
        # SOURCE LINE 309
        __M_writer(escape(_("display realm select box")))
        __M_writer(u"</label></td>\n\t\t    \t\t\t<td><input type='checkbox' name='sys_realmbox' id='sys_realmbox' value='sys_realmbox'\n\t\t    \t\t\t\ttitle='")
        # SOURCE LINE 311
        __M_writer(escape(_("If checked a realm dropdown box will be displayed on the logon page.")))
        __M_writer(u"'></td></tr>\n\t\t    \t\t\t<tr><td><label for=sys_loginhelp>")
        # SOURCE LINE 312
        __M_writer(escape(_("display help button on login dialog")))
        __M_writer(u"</label></td>\n\t\t    \t\t\t<td><input type='checkbox' name='sys_loginhelp' id='sys_loginhelp' value='sys_loginhelp'\n\t\t    \t\t\t\ttitle='")
        # SOURCE LINE 314
        __M_writer(escape(_("If checked a help button will be displayed on the logon window.")))
        __M_writer(u"'></td></tr>\n\t\t    \t\t\t<tr><td><label for=sys_singletoken>")
        # SOURCE LINE 315
        __M_writer(escape(_("Allow only one token to be selected")))
        __M_writer(u"</label></td>\n\t\t    \t\t\t<td><input type='checkbox' name='sys_singletoken' id='sys_singletoken' value='sys_singletoken'\n\t\t    \t\t\t\ttitle='")
        # SOURCE LINE 317
        __M_writer(escape(_("If checked an administrator may only select one token in the token view.")))
        __M_writer(u'\'></td></tr>\n\t\t    \t\t</table>\n\t\t    </fieldset>\n    \t</div>  <!-- tab system settings gui -->\n    </div> <!-- tab container system settings -->\n    </form>\n</div>\n\n<script>\n\tfunction translate_system_settings() {\n\t\t$("#dialog_system_settings" ).dialog( "option", "title", \'')
        # SOURCE LINE 327
        __M_writer(escape(_("System config")))
        __M_writer(u"' );\n\t\t$('#button_system_save .ui-button-text').html('")
        # SOURCE LINE 328
        __M_writer(escape(_("Save config")))
        __M_writer(u"');\n\t\t$('#button_system_cancel .ui-button-text').html('")
        # SOURCE LINE 329
        __M_writer(escape(_("Cancel")))
        __M_writer(u"');\n\t}\n</script>\n\n<!-- ############ system settings ################# -->\n<div id='dialog_token_settings'>\n\t<div id='tab_token_settings'><!-- tab container token settings -->\n\t\t<ul id='token_tab_index'>\n")
        # SOURCE LINE 337
        for entry in c.token_config_tab:
            # SOURCE LINE 338
            __M_writer(u'\t\t\t<li> <a href="#')
            __M_writer(escape(entry))
            __M_writer(u'_token_settings">')
            __M_writer(c.token_config_tab[entry] )
            __M_writer(u'</a></li>\n')
        # SOURCE LINE 340
        __M_writer(u'\t\t</ul> <!-- tab with token settings -->\n')
        # SOURCE LINE 341
        for entry in c.token_config_div:
            # SOURCE LINE 342
            __M_writer(u'\t\t\t<div id="')
            __M_writer(escape(entry))
            __M_writer(u'_token_settings">\n\t\t\t\t')
            # SOURCE LINE 343
            __M_writer(c.token_config_div[entry] )
            __M_writer(u'\n\t\t\t</div>\n')
        # SOURCE LINE 346
        __M_writer(u'\n    </div> <!-- tab container system settings -->\n</div>\n\n<script>\n\tfunction translate_token_settings() {\n\t\t$("#dialog_token_settings" ).dialog( "option", "title", \'')
        # SOURCE LINE 352
        __M_writer(escape(_("Tokentype Configuration")))
        __M_writer(u"' );\n\t\t$('#button_token_save .ui-button-text').html('")
        # SOURCE LINE 353
        __M_writer(escape(_("Save config")))
        __M_writer(u"');\n\t\t$('#button_token_cancel .ui-button-text').html('")
        # SOURCE LINE 354
        __M_writer(escape(_("Cancel")))
        __M_writer(u"');\n\t}\n</script>\n\n\n\n<!-- ##################### Set PIN ######################### -->\n<div id='dialog_set_pin'>\n\t<p>")
        # SOURCE LINE 362
        __M_writer(escape(_("You may reset the PINs for the tokens")))
        __M_writer(u'\n\t\t<span id=\'dialog_set_pin_token_string\'> </span>\n\t\t</p>\n\n\t<form>\n\t\t<input id=\'setpin_tokens\' type=\'hidden\'>\n\t\t<fieldset>\n    \t\t<table>\n\t    \t\t<tr><td>\n\t    \t\t<label for="pintype">')
        # SOURCE LINE 371
        __M_writer(escape(_("PIN type")))
        __M_writer(u'</label>\n\t    \t\t</td><td>\n\t    \t\t<select name="pintype" id="pintype">\n\t    \t\t<option value="motp">mOTP PIN</option>\n\t    \t\t<option value="ocra">OCRA PIN</option>\n\t    \t\t<option selected value="otp">OTP PIN</option>\n\t    \t\t</select>\n\t    \t\t</td></tr><tr><td>\n\t    \t\t<label for="pin1">PIN</label>\n\t    \t\t</td><td>\n\t    \t\t<input type="password" autocomplete="off" onkeyup="checkpins(\'pin1\',\'pin2\');" name="pin1" id="pin1"\n\t    \t\t\tclass="text ui-widget-content ui-corner-all" />\n\t    \t\t</td></tr><tr><td>\n\t    \t\t<label for="pin2">')
        # SOURCE LINE 384
        __M_writer(escape(_("PIN (again)")))
        __M_writer(u'</label>\n\t    \t\t</td><td>\n\t    \t\t<input type="password" autocomplete="off" onkeyup="checkpins(\'pin1\',\'pin2\');" name="pin2" id="pin2" class="text ui-widget-content ui-corner-all" />\n\t    \t\t</td></tr>\n\t\t\t</table>\n    \t</fieldset>\n    </form>\n</div>\n\n<script>\n\tfunction translate_set_pin() {\n\t\t$("#dialog_set_pin" ).dialog( "option", "title", \'')
        # SOURCE LINE 395
        __M_writer(escape(_("Set PIN")))
        __M_writer(u"' );\n\t\t$('#button_setpin_setpin .ui-button-text').html('")
        # SOURCE LINE 396
        __M_writer(escape(_("Set PIN")))
        __M_writer(u"');\n\t\t$('#button_setpin_cancel .ui-button-text').html('")
        # SOURCE LINE 397
        __M_writer(escape(_("Cancel")))
        __M_writer(u"');\n\t}\n</script>\n\n\n<!-- ############## Token enroll ################################ -->\n<div id='dialog_token_enroll'>\n\t<div id='enroll_info_text_user'>\n\t\t<p>\n\t\t")
        # SOURCE LINE 406
        __M_writer(escape(_("The token will be enrolled for user")))
        __M_writer(u'\n\t\t<b><span id=\'enroll_info_user\'> </span></b>.\n\t\t</p>\n\t</div>\n    <div id=\'enroll_info_text_nouser\'>\n\t\t<table width="100%"><tr>\n    \t<td><label for=\'enroll_info_text_nouser_cb\'>')
        # SOURCE LINE 412
        __M_writer(escape(_("Currently this token will not be assigned to any users.")))
        __M_writer(u'</label></td>\n    \t<td align="right"><label for=\'enroll_info_text_nouser_cb\'>')
        # SOURCE LINE 413
        __M_writer(escape(_("[?]")))
        __M_writer(u'</label></td>\n    \t</tr></table>\n    \t<blockquote>\n\t\t<input type=\'checkbox\' id=\'enroll_info_text_nouser_cb\' checked="checked"  style="display:none;"\n\t\t\tonclick="cb_changed(\'enroll_info_text_nouser_cb\',[\'enroll_info_text_nouser_cb_more\'])">\n\t\t<label id=\'enroll_info_text_nouser_cb_more\' class=\'italic_label\' style="display:none;">')
        # SOURCE LINE 418
        __M_writer(escape(_("If you select one user, this token will be "+
        		"automatically assigned to this user. Anyhow, you can assign this token to any user later on.")))
        # SOURCE LINE 419
        __M_writer(u"</label>\n        </blockquote>\n    </div>\n    <div id='enroll_info_text_multiuser'>\n    \t<p>")
        # SOURCE LINE 423
        __M_writer(escape(_("You selected more than one user. If you want to assign the token to a user during enrollment, "+
        		"you need to select only one user.  Anyhow, you can assign this token to any user later on.")))
        # SOURCE LINE 424
        __M_writer(u'\n        </p>\n    </div>\n   \t<script type="text/javascript">tokentype_changed();</script>\n    <form id="form_enroll_token">\n    \t<fieldset>\n    \t\t<table>\n    \t\t\t<tr><td><label for="tokentype">')
        # SOURCE LINE 431
        __M_writer(escape(_("Token type")))
        __M_writer(u'</label></td><td>\n    \t\t\t\t<select name="tokentype" id="tokentype" onchange="tokentype_changed();">\n\t\t\t\t\t\t<option value="ocra">')
        # SOURCE LINE 433
        __M_writer(escape(_("OCRA - challenge/response Token")))
        __M_writer(u'</option>\n\t\t\t\t\t\t<!-- we do not sort by the key/conf but for the value -->\n')
        # SOURCE LINE 435
        for tok in sorted(c.token_enroll_tab, key=lambda t: c.token_enroll_tab[t]):
            # SOURCE LINE 436
            if tok == 'hmac':
                # SOURCE LINE 437
                __M_writer(u'\t\t\t\t\t\t  <option selected value="')
                __M_writer(escape(tok))
                __M_writer(u'">')
                __M_writer(c.token_enroll_tab[tok] )
                __M_writer(u'</option>\n')
                # SOURCE LINE 438
            else:
                # SOURCE LINE 439
                __M_writer(u'\t\t\t\t\t\t  <option value="')
                __M_writer(escape(tok))
                __M_writer(u'">')
                __M_writer(c.token_enroll_tab[tok] )
                __M_writer(u'</option>\n')
        # SOURCE LINE 442
        __M_writer(u'    \t\t\t\t</select>\n    \t\t\t</td></tr>\n    \t\t</table>\n\n    \t\t<div id="token_enroll_ocra">\n    \t\t\t<p><span id=\'ocra_key_intro\'>\n    \t\t\t\t')
        # SOURCE LINE 448
        __M_writer(escape(_("Please enter or copy the OCRA key.")))
        __M_writer(u'</span></p>\n    \t\t\t<table><tr>\n    \t\t\t<td><label for="ocra_key" id=\'ocra_key_label\'>')
        # SOURCE LINE 450
        __M_writer(escape(_("OCRA key")))
        __M_writer(u'</label></td>\n    \t\t\t<td><input type="text" name="ocra_key" id="ocra_key" value="" class="text ui-widget-content ui-corner-all" /></td>\n    \t\t\t</tr>\n    \t\t\t<tr><td> </td><td><input type=\'checkbox\' id=\'ocra_key_cb\' onclick="cb_changed(\'ocra_key_cb\',[\'ocra_key\',\'ocra_key_label\',\'ocra_key_intro\']);">\n    \t\t\t\t<label for=ocra_key_cb>')
        # SOURCE LINE 454
        __M_writer(escape(_("Generate OCRA key.")))
        __M_writer(u'</label></td></tr>\n    \t\t\t</table>\n    \t\t</div>\n\n')
        # SOURCE LINE 458
        for tok in c.token_enroll_div:
            # SOURCE LINE 459
            __M_writer(u'\t\t\t <div id="token_enroll_')
            __M_writer(escape(tok))
            __M_writer(u'">')
            __M_writer(c.token_enroll_div[tok] )
            __M_writer(u'</div>\n')
        # SOURCE LINE 461
        __M_writer(u'\n    \t</fieldset>\n\t</form>\n</div>\n\n<script>\n\tfunction translate_token_enroll() {\n\t\t$("#dialog_token_enroll" ).dialog( "option", "title", \'')
        # SOURCE LINE 468
        __M_writer(escape(_("Enroll token")))
        __M_writer(u"' );\n\t\t$('#button_enroll_enroll .ui-button-text').html('")
        # SOURCE LINE 469
        __M_writer(escape(_("Enroll")))
        __M_writer(u"');\n\t\t$('#button_enroll_cancel .ui-button-text').html('")
        # SOURCE LINE 470
        __M_writer(escape(_("Cancel")))
        __M_writer(u'\');\n\t}\n</script>\n\n\n<!-- ####################################### get serial ############# -->\n<div id=\'dialog_get_serial\'>\n\t<div style="float:right">\n\t\t\t<a href=\'')
        # SOURCE LINE 478
        __M_writer(escape(c.help_url))
        __M_writer(u'/tools/index.html#get-serial-by-otp-value\' target="_blank">\n\t\t\t<img alt="(?)" width=24\n\t\t\tsrc="/images/help32.png"  \n\t\t\ttitle=\'')
        # SOURCE LINE 481
        __M_writer(escape(_("Open help on getting serial")))
        __M_writer(u"'>\n\t\t\t</a>\n\t\t\t</div>\n\t<p>")
        # SOURCE LINE 484
        __M_writer(escape(_("Here you can search for the serial of a token."+
    	"You need to enter the current OTP value, and choose where you want to search for this token.")))
        # SOURCE LINE 485
        __M_writer(u'</p>\n    \t<p>')
        # SOURCE LINE 486
        __M_writer(escape(_("Beware: This can be time consuming!")))
        __M_writer(u'</p>\n    \t<p><label for="tools_getserial_type">')
        # SOURCE LINE 487
        __M_writer(escape(_("Type")))
        __M_writer(u'</label> <input id=\'tools_getserial_type\'></p>\n    \t<p><label for="tools_getserial_assigned">')
        # SOURCE LINE 488
        __M_writer(escape(_("Assigned Token")))
        __M_writer(u'</label>\n    \t\t<select id=\'tools_getserial_assigned\'><option> </option>\n    \t\t\t<option value="1">')
        # SOURCE LINE 490
        __M_writer(escape(_("assigned")))
        __M_writer(u'</option>\n    \t\t\t<option value="0">')
        # SOURCE LINE 491
        __M_writer(escape(_("not assigned")))
        __M_writer(u'</option>\n\t\t\t</select></p>\n    \t<p><label for="tools_getserial_realm">')
        # SOURCE LINE 493
        __M_writer(escape(_("Realm")))
        __M_writer(u'</label> <select id=\'tools_getserial_realm\'> </select></p>\n    \t<p><label for="tools_getserial_otp">')
        # SOURCE LINE 494
        __M_writer(escape(_("OTP value")))
        __M_writer(u'</label> <input id=\'tools_getserial_otp\'></p>\n</div>\n\n<script>\n\tfunction translate_get_serial() {\n\t\t$("#dialog_get_serial" ).dialog( "option", "title", \'')
        # SOURCE LINE 499
        __M_writer(escape(_("Get Serial by OTP value")))
        __M_writer(u"' );\n\t\t$('#button_tools_getserial_ok .ui-button-text').html('")
        # SOURCE LINE 500
        __M_writer(escape(_("Get Serial")))
        __M_writer(u"');\n\t\t$('#button_tools_getserial_close .ui-button-text').html('")
        # SOURCE LINE 501
        __M_writer(escape(_("Close")))
        __M_writer(u'\');\n\t}\n</script>\n\n\n<!------------------------ check policy ------------------------->\n<div id="dialog_check_policy">\n\t<div style="float:right">\n\t\t\t<a href=\'')
        # SOURCE LINE 509
        __M_writer(escape(c.help_url))
        __M_writer(u'/tools/index.html#check-policy\' target="_blank">\n\t\t\t<img alt="(?)" width=24\n\t\t\tsrc="/images/help32.png"  \n\t\t\ttitle=\'')
        # SOURCE LINE 512
        __M_writer(escape(_("Open help on Policy checker")))
        __M_writer(u"'>\n\t\t\t</a>\n\t\t\t</div>\n\t<p>")
        # SOURCE LINE 515
        __M_writer(escape(_("Here you can check your policies.")))
        __M_writer(u'</p>\n\t<p>')
        # SOURCE LINE 516
        __M_writer(escape(_("You can enter the corresponding values and the system will check, if there is any matching policy for this scenario.")))
        __M_writer(u'</p>\n\t<form class="cmxform" id="form_check_policy">\n\t<table>\n\t\t<tr><td><label for=cp_scope>')
        # SOURCE LINE 519
        __M_writer(escape(_("scope")))
        __M_writer(u"</label></td>\n\t\t\t<td>\n\t\t\t\t<select id='cp_scope'>\n")
        # SOURCE LINE 522
        for scope in c.polDefs.keys():
            # SOURCE LINE 523
            __M_writer(u'\t\t\t\t\t<option value="')
            __M_writer(escape(scope))
            __M_writer(u'">')
            __M_writer(escape(scope))
            __M_writer(u'</option>\n')
        # SOURCE LINE 525
        __M_writer(u'\t\t\t\t</select>\n\t\t\t</td></tr>\n\t\t<tr><td><label for="cp_realm">')
        # SOURCE LINE 527
        __M_writer(escape(_("realm")))
        __M_writer(u'</label></td>\n\t\t\t<td><input id="cp_realm" class="required"></td></tr>\n\t\t<tr><td><label for="cp_action">')
        # SOURCE LINE 529
        __M_writer(escape(_("action")))
        __M_writer(u'</label></td>\n     \t\t<td><input id="cp_action" class="required"></td></tr>\n\t \t<tr><td><label for="cp_user">')
        # SOURCE LINE 531
        __M_writer(escape(_("user")))
        __M_writer(u'</label></td>\n\t \t\t<td><input id="cp_user" class="required"></td></tr>\n    \t<tr><td><label for="cp_client">')
        # SOURCE LINE 533
        __M_writer(escape(_("client")))
        __M_writer(u'</label></td>\n    \t\t<td><input id="cp_client"></td></tr>\n    </table>\n    <hr>\n    <div id="cp_allowed">')
        # SOURCE LINE 537
        __M_writer(escape(_("This action is allowed by the following policy:")))
        __M_writer(u'</div>\n    <div id="cp_forbidden">')
        # SOURCE LINE 538
        __M_writer(escape(_("This action is not allowed by any policy!")))
        __M_writer(u'</div>\n    <div><pre id="cp_policy"> </pre></div>\n    </form>\n</div>\n\n<script>\n\tfunction translate_check_policy() {\n\t\t$("#dialog_check_policy" ).dialog( "option", "title", \'')
        # SOURCE LINE 545
        __M_writer(escape(_("Check Policy")))
        __M_writer(u"' );\n\t\t$('#button_tools_checkpolicy_ok .ui-button-text').html('")
        # SOURCE LINE 546
        __M_writer(escape(_("Check Policy")))
        __M_writer(u"');\n\t\t$('#button_tools_checkpolicy_close .ui-button-text').html('")
        # SOURCE LINE 547
        __M_writer(escape(_("Close")))
        __M_writer(u'\');\n\t}\n</script>\n\n<!------------------------ export token ------------------------------->\n\n<div id="dialog_export_token">\n\t<div style="float:right">\n\t\t\t<a href=\'')
        # SOURCE LINE 555
        __M_writer(escape(c.help_url))
        __M_writer(u'/tools/index.html#export-token-information\' target="_blank">\n\t\t\t<img alt="(?)" width=24\n\t\t\tsrc="/images/help32.png"  \n\t\t\ttitle=\'')
        # SOURCE LINE 558
        __M_writer(escape(_("Open help on export token information")))
        __M_writer(u"'>\n\t\t\t</a>\n\t\t\t</div>\n\t<p>")
        # SOURCE LINE 561
        __M_writer(escape(_("Here you can export token information of the tokens you are allowed to view to a CSV file.")))
        __M_writer(u'</p>\n\t<p>')
        # SOURCE LINE 562
        __M_writer(escape(_("You can enter additional attributes, you defined in the user mapping in the UserIdResolver. These attributes will be added to the CSV file.")))
        __M_writer(u'</p>\n\t<form class="cmxform" id="form_export_token">\n\t\t<input id="exporttoken_attributes">\n    </form>\n</div>\n\n<script>\n\tfunction translate_export_token() {\n\t\t$("#dialog_export_token" ).dialog( "option", "title", \'')
        # SOURCE LINE 570
        __M_writer(escape(_("Export token information")))
        __M_writer(u"' );\n\t\t$('#button_export_token .ui-button-text').html('")
        # SOURCE LINE 571
        __M_writer(escape(_("Export")))
        __M_writer(u'\');\n\t}\n</script>\n\n<!------------------------ export audit ------------------------------->\n\n<div id="dialog_export_audit">\n\t<div style="float:right">\n\t\t\t<a href=\'')
        # SOURCE LINE 579
        __M_writer(escape(c.help_url))
        __M_writer(u'/tools/index.html#export-audit-information\' target="_blank">\n\t\t\t<img alt="(?)" width=24\n\t\t\tsrc="/images/help32.png"  \n\t\t\ttitle=\'')
        # SOURCE LINE 582
        __M_writer(escape(_("Open help on export audit information")))
        __M_writer(u"'>\n\t\t\t</a>\n\t\t\t</div>\n\t<p>")
        # SOURCE LINE 585
        __M_writer(escape(_("Here you can export the audit information to a CSV file.")))
        __M_writer(u'</p>\n\t<p><label for="export_audit_number">')
        # SOURCE LINE 586
        __M_writer(escape(_("Number of audit entries to export")))
        __M_writer(u':</label>\n\t\t<input id="export_audit_number" size=7 maxlength=6\n\t\ttitle=\'')
        # SOURCE LINE 588
        __M_writer(escape(_("Enter the number of audit entries you want to export.")))
        __M_writer(u'\'> \n\t\t</p>\n\t<p><label for="export_audit_page">')
        # SOURCE LINE 590
        __M_writer(escape(_("Page to export")))
        __M_writer(u':</label>\n\t\t<input id="export_audit_page"  size=7 maxlength=6\n\t\ttitle=\'')
        # SOURCE LINE 592
        __M_writer(escape(_("Enter the page of the audit entries you want to export.")))
        __M_writer(u'\'> \n\t\t</p>\n</div>\n\n<script>\n\tfunction translate_export_audit() {\n\t\t$("#dialog_export_audit" ).dialog( "option", "title", \'')
        # SOURCE LINE 598
        __M_writer(escape(_("Export audit information")))
        __M_writer(u"' );\n\t\t$('#button_export_audit .ui-button-text').html('")
        # SOURCE LINE 599
        __M_writer(escape(_("Export")))
        __M_writer(u'\');\n\t}\n</script>\n\n\n<!-- ###################### copy token ####################### -->\n<div id=\'dialog_copy_token\'>\n\t<div style="float:right">\n\t\t\t<a href=\'')
        # SOURCE LINE 607
        __M_writer(escape(c.help_url))
        __M_writer(u'/tools/index.html#copy-token-pin\' target="_blank">\n\t\t\t<img alt="(?)" width=24\n\t\t\tsrc="/images/help32.png"  \n\t\t\ttitle=\'')
        # SOURCE LINE 610
        __M_writer(escape(_("Open help on Copy token PIN tool")))
        __M_writer(u"'>\n\t\t\t</a>\n\t\t\t</div>\n\t<p>")
        # SOURCE LINE 613
        __M_writer(escape(_("Here you can copy the OTP PIN from one token to the other.")))
        __M_writer(u'</p>\n\t<p>')
        # SOURCE LINE 614
        __M_writer(escape(_("Please enter the serial number of the token with the existing PIN and the serial number of the token, that should get the same PIN.")))
        __M_writer(u'</p>\n    <p><label for=copy_from_token>')
        # SOURCE LINE 615
        __M_writer(escape(_("from token")))
        __M_writer(u"</label> <input id='copy_from_token'></p>\n    <p><label for=copy_to_token>")
        # SOURCE LINE 616
        __M_writer(escape(_("to token")))
        __M_writer(u'</label> <input id=\'copy_to_token\'></p>\n</div>\n\n<script>\n\tfunction translate_copy_token() {\n\t\t$("#dialog_copy_token" ).dialog( "option", "title", \'')
        # SOURCE LINE 621
        __M_writer(escape(_("Copy Token PIN")))
        __M_writer(u"' );\n\t\t$('#button_tools_copytokenpin_ok .ui-button-text').html('")
        # SOURCE LINE 622
        __M_writer(escape(_("Copy PIN")))
        __M_writer(u"');\n\t\t$('#button_tools_copytokenpin_close .ui-button-text').html('")
        # SOURCE LINE 623
        __M_writer(escape(_("Close")))
        __M_writer(u'\');\n\t}\n</script>\n\n<!-- ############# import Safenet ######################### -->\n<div id=\'dialog_import_safenet\'>\n\t<form id="load_tokenfile_form_aladdin" action="/admin/loadtokens" method="post"\n\t\t\t\tenctype="multipart/form-data" onsubmit="return false;">\n\t\t\t<div style="float:right">\n\t\t\t<a href=\'')
        # SOURCE LINE 632
        __M_writer(escape(c.help_url))
        __M_writer(u'/import/index.html#safenet-xml\' target="_blank">\n\t\t\t<img alt="(?)" width=24\n\t\t\tsrc="/images/help32.png"  \n\t\t\ttitle=\'')
        # SOURCE LINE 635
        __M_writer(escape(_("Open help on XML import")))
        __M_writer(u"'>\n\t\t\t</a>\n\t\t\t</div>\n\t\t<p>")
        # SOURCE LINE 638
        __M_writer(escape(_("Here you can upload the XML file that came with your SafeNet eToken PASS.")))
        __M_writer(u'</p>\n  \t\t<p>')
        # SOURCE LINE 639
        __M_writer(escape(_("Please choose the token file")))
        __M_writer(u':<br>\n    \t<input name="file" type="file" size="30" maxlength="1000000" accept="text/*">\n    \t<p>\n\t\t\t<label for=aladdin_hashlib>')
        # SOURCE LINE 642
        __M_writer(escape(_("Hash Algorithm")))
        __M_writer(u':</label>\n\t\t\t <select id=\'aladdin_hashlib\' name=aladdin_hashlib >\n\t\t\t\t<option value="auto">')
        # SOURCE LINE 644
        __M_writer(escape(_("automatic detection")))
        __M_writer(u'</option>\n\t\t\t\t<option value="sha1">sha1</option>\n\t\t\t\t<option value="sha256">sha256</option>\n\t\t\t</select>\n\t\t</p>\n\t\t<p>\n    \t<input name="type" type="hidden" value="aladdin-xml">\n    \t<input name="session" id="loadtokens_session_aladdin" type="hidden" value="">\n    \t</p>\n\t</form>\n</div>\n\n<script>\n\tfunction translate_import_safenet() {\n\t\t$("#dialog_import_safenet" ).dialog( "option", "title", \'')
        # SOURCE LINE 658
        __M_writer(escape(_("Aladdin XML Token file")))
        __M_writer(u"' );\n\t\t$('#button_aladdin_load .ui-button-text').html('")
        # SOURCE LINE 659
        __M_writer(escape(_("load token file")))
        __M_writer(u"');\n\t\t$('#button_aladdin_cancel .ui-button-text').html('")
        # SOURCE LINE 660
        __M_writer(escape(_("Cancel")))
        __M_writer(u'\');\n\t}\n</script>\n\n<!-- ################ import PSKC ########################### -->\n<div id=\'dialog_import_pskc\'>\n\t<script type="text/javascript">pskc_type_changed();</script>\n\t<form id="load_tokenfile_form_pskc" action="/admin/loadtokens" method="post"\n\t\t\tenctype="multipart/form-data" onsubmit="return false;">\n\t\t\t<p>')
        # SOURCE LINE 669
        __M_writer(escape(_("Here you may upload the XML file of any OATH compliant OTP Token."+
				"The privacyIDEA server will automatically recognize "+
				"if the token is an HOTP (event based) or a TOTP (time based) token. "+
				"If the HMAC secrets are encrypted you either "+
				"need - depending on the encryption - the password or the encryption key.")))
        # SOURCE LINE 673
        __M_writer(u'</p>\n  \t\t\t<p>')
        # SOURCE LINE 674
        __M_writer(escape(_("Please choose the token file")))
        __M_writer(u':<br>\n    \t\t<input name="file" type="file" size="30" maxlength="1000000" accept="text/*">\n    \t\t<input name="type" type="hidden" value="pskc">\n    \t\t<p>\n\t\t\t<input type="checkbox" name="pskc_checkserial" value="True" id=\'pskc_checkserial\'>\n\t\t\t\t<label for=\'pskc_checkserial\'>\n\t\t\t\t\t')
        # SOURCE LINE 680
        __M_writer(escape(_("Check the serial numbers for OATH compliance (non-compliant serial numbers will be ignored)")))
        __M_writer(u'\n\t\t\t\t\t</label>\n\t\t\t</p>\n\t\t\t<p>\n\t\t\t<select id=\'pskc_type\' name=\'pskc_type\' onchange="pskc_type_changed();">\n\t\t\t\t<option value=\'plain selected\'>')
        # SOURCE LINE 685
        __M_writer(escape(_("plain value")))
        __M_writer(u"</option>\n\t\t\t\t<option value='key'>")
        # SOURCE LINE 686
        __M_writer(escape(_("preshared key")))
        __M_writer(u"</option>\n\t\t\t\t<option value='password'>")
        # SOURCE LINE 687
        __M_writer(escape(_("password protected")))
        __M_writer(u'</option>\n\t\t\t</select>\n\t\t\t<input id=\'pskc_password\' name=\'pskc_password\' type=\'password\' size=\'32\'>\n\t\t\t<input id=\'pskc_preshared\' name=\'pskc_preshared\' size=\'32\'>\n\t\t\t</p>\n\t\t\t<input name="session" id="loadtokens_session_pskc" type="hidden" value="">\n\t</form>\n</div>\n\n<script>\n\tfunction translate_import_pskc() {\n\t\t$("#dialog_import_pskc" ).dialog( "option", "title", \'')
        # SOURCE LINE 698
        __M_writer(escape(_("PSKC Key file")))
        __M_writer(u"' );\n\t\t$('#button_pskc_load .ui-button-text').html('")
        # SOURCE LINE 699
        __M_writer(escape(_("load token file")))
        __M_writer(u"');\n\t\t$('#button_pskc_cancel .ui-button-text').html('")
        # SOURCE LINE 700
        __M_writer(escape(_("Cancel")))
        __M_writer(u'\');\n\t}\n</script>\n\n<!-- ###################### import OATH CSV ####################### -->\n<div id=\'dialog_import_oath\'>\n\t<form id="load_tokenfile_form_oathcsv" action="/admin/loadtokens" method="post"\n\t\t\tenctype="multipart/form-data" onsubmit="return false;">\n\t\t<div style="float:right">\n\t\t\t<a href=\'')
        # SOURCE LINE 709
        __M_writer(escape(c.help_url))
        __M_writer(u'/import/index.html#oath-csv\' target="_blank">\n\t\t\t<img alt="(?)" width=24\n\t\t\tsrc="/images/help32.png"  \n\t\t\ttitle=\'')
        # SOURCE LINE 712
        __M_writer(escape(_("Open help on OATH CSV import")))
        __M_writer(u"'>\n\t\t\t</a>\n\t\t\t</div>\n\t\t<p>")
        # SOURCE LINE 715
        __M_writer(escape(_("Here you can upload a csv file for your OATH token. The file is supposed to contain one token per line")))
        __M_writer(u':</p>\n\t\t<p>')
        # SOURCE LINE 716
        __M_writer(escape(_("For HOTP and TOTP tokens:")))
        __M_writer(u'</p>\n\t\t<p>')
        # SOURCE LINE 717
        __M_writer(escape(_("serial number, seed, type, otplen, timeStep")))
        __M_writer(u'</p>\n\t\t<p>')
        # SOURCE LINE 718
        __M_writer(escape(_("For OCRA tokens:")))
        __M_writer(u'</p>\n\t\t<p>')
        # SOURCE LINE 719
        __M_writer(escape(_("serial number, seed, type, ocrasuite")))
        __M_writer(u'</p>\n\t\t<p>')
        # SOURCE LINE 720
        __M_writer(escape(_("type (default hotp), otplen (default 6), timeStep (default 30) and ocrasuite are optional.")))
        __M_writer(u'</p>\n  \t\t<p>')
        # SOURCE LINE 721
        __M_writer(escape(_("Please choose the token file")))
        __M_writer(u':\n    \t\t<input name="file" type="file" size="30" maxlength="1000000" accept="text/*">\n    \t\t<input name="type" type="hidden" value="oathcsv">')
        # SOURCE LINE 724
        __M_writer(u'    \t\t<input name="session" id="loadtokens_session_oathcsv" type="hidden" value="">')
        # SOURCE LINE 725
        __M_writer(u'\t\t</p>\n\t</form>\n</div>\n\n<script>\n\tfunction translate_import_oath() {\n\t\t$("#dialog_import_oath" ).dialog( "option", "title", \'')
        # SOURCE LINE 731
        __M_writer(escape(_("OATH csv Token file")))
        __M_writer(u"' );\n\t\t$('#button_oathcsv_load .ui-button-text').html('")
        # SOURCE LINE 732
        __M_writer(escape(_("load token file")))
        __M_writer(u"');\n\t\t$('#button_oathcsv_cancel .ui-button-text').html('")
        # SOURCE LINE 733
        __M_writer(escape(_("Cancel")))
        __M_writer(u'\');\n\t}\n</script>\n\n<!-- ###################### import Yubikey CSV ####################### -->\n<div id=\'dialog_import_yubikey\'>\n\t<form id="load_tokenfile_form_yubikeycsv" action="/admin/loadtokens" method="post"\n\t\t\tenctype="multipart/form-data" onsubmit="return false;">\n\t\t<div style="float:right">\n\t\t\t<a href=\'')
        # SOURCE LINE 742
        __M_writer(escape(c.help_url))
        __M_writer(u'/import/index.html#yubikey-csv\' target="_blank">\n\t\t\t<img alt="(?)" width=24\n\t\t\tsrc="/images/help32.png"  \n\t\t\ttitle=\'')
        # SOURCE LINE 745
        __M_writer(escape(_("Open help on Yubikey import")))
        __M_writer(u"'>\n\t\t\t</a>\n\t\t\t</div>\n\t\t<p>")
        # SOURCE LINE 748
        __M_writer(escape(_("Here you can upload a csv file for your Yubikey token. The file is supposed to contain one token per line")))
        __M_writer(u':</p>\n  \t\t<p>')
        # SOURCE LINE 749
        __M_writer(escape(_("Please choose the token file")))
        __M_writer(u':\n    \t\t<input name="file" type="file" size="30" maxlength="1000000" accept="text/*">\n    \t\t<input name="type" type="hidden" value="yubikeycsv">')
        # SOURCE LINE 752
        __M_writer(u'    \t\t<input name="session" id="loadtokens_session_yubikeycsv" type="hidden" value="">')
        # SOURCE LINE 753
        __M_writer(u'\t\t</p>\n\t</form>\n</div>\n\n<script>\n\tfunction translate_import_yubikey() {\n\t\t$("#dialog_import_yubikey" ).dialog( "option", "title", \'')
        # SOURCE LINE 759
        __M_writer(escape(_("Yubikey csv Token file")))
        __M_writer(u"' );\n\t\t$('#button_yubikeycsv_load .ui-button-text').html('")
        # SOURCE LINE 760
        __M_writer(escape(_("load token file")))
        __M_writer(u"');\n\t\t$('#button_yubikeycsv_cancel .ui-button-text').html('")
        # SOURCE LINE 761
        __M_writer(escape(_("Cancel")))
        __M_writer(u'\');\n\t}\n</script>\n\n<!-- ##################### import Tagespasswort ######################## -->\n<div id=\'dialog_import_dpw\'>\n\t<form id="load_tokenfile_form_dpw" action="/admin/loadtokens" method="post"\n\t\t\tenctype="multipart/form-data" onsubmit="return false;">\n  \t\t<p>')
        # SOURCE LINE 769
        __M_writer(escape(_("Here you can upload the data file that came with your Tagespasswort tokens.")))
        __M_writer(u'</p>\n\t\t<p>')
        # SOURCE LINE 770
        __M_writer(escape(_("Please choose the token file")))
        __M_writer(u':\n    \t\t<input name="file" type="file" size="30" maxlength="1000000" accept="text/*">\n    \t\t<input name="type" type="hidden" value="dpw">\n    \t\t<input name="session" id="loadtokens_session_dpw" type="hidden" value="">\n    \t</p>\n\t</form>\n</div>\n\n<script>\n\tfunction translate_import_dpw() {\n\t\t$("#dialog_import_dpw" ).dialog( "option", "title", \'')
        # SOURCE LINE 780
        __M_writer(escape(_("Tagespasswort Token file")))
        __M_writer(u"' );\n\t\t$('#button_dpw_load .ui-button-text').html('")
        # SOURCE LINE 781
        __M_writer(escape(_("load token file")))
        __M_writer(u"');\n\t\t$('#button_dpw_cancel .ui-button-text').html('")
        # SOURCE LINE 782
        __M_writer(escape(_("Cancel")))
        __M_writer(u'\');\n\t}\n</script>\n\n<!-- ##################### import eToken dat file ######################## -->\n<div id=\'dialog_import_dat\'>\n    <form id="load_tokenfile_form_dat" action="/admin/loadtokens" method="post"\n            enctype="multipart/form-data" onsubmit="return false;">\n        <p>')
        # SOURCE LINE 790
        __M_writer(escape(_("Here you can upload the data file that came with your eToken.")))
        __M_writer(u'</p>\n        <p>')
        # SOURCE LINE 791
        __M_writer(escape(_("Please choose the token file")))
        __M_writer(u':</p>\n            <input name="file" type="file" size="30" maxlength="1000000" accept="text/* data/*">\n            <p>\n                <label for=\'startdate\'>Startdate</label>\n                <input id=\'startdate\' name="startdate" type="datetime" value="1.1.2000"/>\n            </p>\n            <input name="type" type="hidden" value="dat">\n            <input name="session" id="loadtokens_session_dat" type="hidden" value="">\n    </form>\n</div>\n\n<script>\n    function translate_import_dat() {\n        $("#dialog_import_dat" ).dialog( "option", "title", \'')
        # SOURCE LINE 804
        __M_writer(escape(_("eToken dat file")))
        __M_writer(u"' );\n        $('#button_dat_load .ui-button-text').html('")
        # SOURCE LINE 805
        __M_writer(escape(_("load token file")))
        __M_writer(u"');\n        $('#button_dat_cancel .ui-button-text').html('")
        # SOURCE LINE 806
        __M_writer(escape(_("Cancel")))
        __M_writer(u'\');\n    }\n</script>\n\n<!-- ######################## import Feitian ############################# -->\n\n<div id=\'dialog_import_feitian\'>\n\t<form id="load_tokenfile_form_feitian" action="/admin/loadtokens" method="post"\n\t\t\t\tenctype="multipart/form-data" onsubmit="return false;">\n  \t\t\t\t<p>')
        # SOURCE LINE 815
        __M_writer(escape(_("Here you can upload the XML file that came with your Feitian tokens.")))
        __M_writer(u'</p>\n\t\t\t\t<p>')
        # SOURCE LINE 816
        __M_writer(escape(_("Please choose the token file")))
        __M_writer(u':<br>\n    \t\t\t<input name="file" type="file" size="30" maxlength="1000000" accept="text/*">\n    \t\t\t<input name="type" type="hidden" value="feitian">\n    \t\t\t<input name="session" id="loadtokens_session_feit" type="hidden" value="">\n    \t\t\t</p></form>\n</div>\n<script>\n\tfunction translate_import_feitian() {\n\t\t$("#dialog_import_feitian" ).dialog( "option", "title", \'')
        # SOURCE LINE 824
        __M_writer(escape(_("Feitian XML Token file")))
        __M_writer(u"' );\n\t\t$('#button_feitian_load .ui-button-text').html('")
        # SOURCE LINE 825
        __M_writer(escape(_("load token file")))
        __M_writer(u"');\n\t\t$('#button_feitian_cancel .ui-button-text').html('")
        # SOURCE LINE 826
        __M_writer(escape(_("Cancel")))
        __M_writer(u'\');\n\t}\n</script>\n\n<!-- ################ import VASCO ################################## -->\n<div id=\'dialog_import_vasco\'>\n\t<form id="load_tokenfile_form_vasco" action="/admin/loadtokens" method="post"\n\t\t\t\tenctype="multipart/form-data" onsubmit="return false;">\n  \t\t\t\t<p>')
        # SOURCE LINE 834
        __M_writer(escape(_("Here you can upload your Vasco dpx file.")))
        __M_writer(u'</p>\n\t\t\t\t<p>')
        # SOURCE LINE 835
        __M_writer(escape(_("Please choose the token file")))
        __M_writer(u':<br>\n    \t\t\t<input name="file" type="file" size="30" maxlength="1000000" accept="text/*"></p>\n    \t\t\t<input name="type" type="hidden" value="vasco">\n    \t\t\t<p><label for=vasco_otplen>')
        # SOURCE LINE 838
        __M_writer(escape(_("OTP length")))
        __M_writer(u':</label>\n    \t\t\t\t <select name=\'vasco_otplen\' id=\'vasco_otplen\'><option selected>6</option>\n    \t\t\t<option>8</option></select>\n    \t\t\t<input name="session" id="loadtokens_session_vasco" type="hidden" value="">\n    \t\t\t</p></form>\n</div>\n<script>\n\tfunction translate_import_vasco() {\n\t\t$("#dialog_import_vasco" ).dialog( "option", "title", \'')
        # SOURCE LINE 846
        __M_writer(escape(_("Vasco dpx file")))
        __M_writer(u"' );\n\t\t$('#button_vasco_load .ui-button-text').html('")
        # SOURCE LINE 847
        __M_writer(escape(_("load token file")))
        __M_writer(u"');\n\t\t$('#button_vasco_cancel .ui-button-text').html('")
        # SOURCE LINE 848
        __M_writer(escape(_("Cancel")))
        __M_writer(u'\');\n\t}\n</script>\n\n<!-- ################### dialog import policies ################# -->\n<div id=\'dialog_import_policy\'>\n\t<form id="load_policies" action="/system/importPolicy" method="post"\n\t\t\t\tenctype="multipart/form-data" onsubmit="return false;">\n  \t\t\t\t<p>')
        # SOURCE LINE 856
        __M_writer(escape(_("Here you can import your policy file.")))
        __M_writer(u'</p>\n\t\t\t\t<p>')
        # SOURCE LINE 857
        __M_writer(escape(_("Please choose the policy file")))
        __M_writer(u':<br>\n    \t\t\t<input name="file" type="file" size="30" maxlength="1000000" accept="text/*"></p>\n    \t\t\t<input name="type" type="hidden" value="policy">\n    \t\t\t</form>\n</div>\n<script>\n\tfunction translate_import_policy() {\n\t\t$("#dialog_import_policies" ).dialog( "option", "title", \'')
        # SOURCE LINE 864
        __M_writer(escape(_("Import policies")))
        __M_writer(u"' );\n\t\t$('#button_policy_load .ui-button-text').html('")
        # SOURCE LINE 865
        __M_writer(escape(_("Import policy file")))
        __M_writer(u"');\n\t\t$('#button_policy_cancel .ui-button-text').html('")
        # SOURCE LINE 866
        __M_writer(escape(_("Cancel")))
        __M_writer(u'\');\n\t}\n</script>\n\n\n\n<!-- ##################### realms ##################################### -->\n<div id=\'dialog_realms\'>\n\t<div style="float:right">\n\t<a href=\'')
        # SOURCE LINE 875
        __M_writer(escape(c.help_url))
        __M_writer(u'/configuration/realms.html\' target="_blank">\n\t<img alt="(?)" width=24\n\tsrc="/images/help32.png"  \n\ttitle=\'')
        # SOURCE LINE 878
        __M_writer(escape(_("Open help on realms")))
        __M_writer(u"'>\n\t</a>\n\t</div>\n\t<p>")
        # SOURCE LINE 881
        __M_writer(escape(_("Create a new realm or select one available realm")))
        __M_writer(u':</p>\n\t<div id=\'realm_list\'> </div>\n</div>\n<script>\n\tfunction translate_dialog_realms() {\n\t\t$("#dialog_realms" ).dialog( "option", "title", \'')
        # SOURCE LINE 886
        __M_writer(escape(_("Realms")))
        __M_writer(u"' );\n\t\t$('#button_realms_new .ui-button-text').html('")
        # SOURCE LINE 887
        __M_writer(escape(_("New")))
        __M_writer(u"');\n\t\t$('#button_realms_edit .ui-button-text').html('")
        # SOURCE LINE 888
        __M_writer(escape(_("Edit")))
        __M_writer(u"');\n\t\t$('#button_realms_delete .ui-button-text').html('")
        # SOURCE LINE 889
        __M_writer(escape(_("Delete")))
        __M_writer(u"');\n\t\t$('#button_realms_close .ui-button-text').html('")
        # SOURCE LINE 890
        __M_writer(escape(_("Close")))
        __M_writer(u"');\n\t\t$('#button_realms_setdefault .ui-button-text').html('")
        # SOURCE LINE 891
        __M_writer(escape(_("Set Default")))
        __M_writer(u"');\n\t\t$('#button_realms_cleardefault .ui-button-text').html('")
        # SOURCE LINE 892
        __M_writer(escape(_("Clear Default")))
        __M_writer(u'\');\n\t}\n</script>\n<!-- ######################### resolvers ############################## -->\n<div id=\'dialog_resolvers\'>\n\t<div style="float:right">\n\t<a href=\'')
        # SOURCE LINE 898
        __M_writer(escape(c.help_url))
        __M_writer(u'/configuration/useridresolvers.html\' target="_blank">\n\t<img alt="(?)" width=24\n\tsrc="/images/help32.png"  \n\ttitle=\'')
        # SOURCE LINE 901
        __M_writer(escape(_("Open help on UserIdResolvers")))
        __M_writer(u"'>\n\t</a>\n\t</div>\n\t<p>")
        # SOURCE LINE 904
        __M_writer(escape(_("Create a new or select one available UserIdResolver")))
        __M_writer(u':</p>\n\t<div id=\'resolvers_list\'> </div>\n</div>\n<script>\n\tfunction translate_dialog_resolvers() {\n\t\t$("#dialog_resolvers" ).dialog( "option", "title", \'')
        # SOURCE LINE 909
        __M_writer(escape(_("Resolver")))
        __M_writer(u"' );\n\t\t$('#button_resolver_new .ui-button-text').html('")
        # SOURCE LINE 910
        __M_writer(escape(_("New")))
        __M_writer(u"');\n\t\t$('#button_resolver_edit .ui-button-text').html('")
        # SOURCE LINE 911
        __M_writer(escape(_("Edit")))
        __M_writer(u"');\n\t\t$('#button_resolver_delete .ui-button-text').html('")
        # SOURCE LINE 912
        __M_writer(escape(_("Delete")))
        __M_writer(u"');\n\t\t$('#button_resolver_close .ui-button-text').html('")
        # SOURCE LINE 913
        __M_writer(escape(_("Close")))
        __M_writer(u'\');\n\t}\n</script>\n\n<!-- ###################### create resolver ########################### -->\n<div id=\'dialog_resolver_create\'>\n\t<div style="float:right">\n\t<a href=\'')
        # SOURCE LINE 920
        __M_writer(escape(c.help_url))
        __M_writer(u'/configuration/useridresolvers.html\' target="_blank">\n\t<img alt="(?)" width=24\n\tsrc="/images/help32.png"  \n\ttitle=\'')
        # SOURCE LINE 923
        __M_writer(escape(_("Open help on UserIdResolvers")))
        __M_writer(u"'>\n\t</a>\n\t</div>\n\t")
        # SOURCE LINE 926
        __M_writer(escape(_("Which type of resolver do you want to create?")))
        __M_writer(u'\n</div>\n<script>\n\tfunction translate_dialog_resolver_create() {\n\t\t$("#dialog_resolver_create" ).dialog( "option", "title", \'')
        # SOURCE LINE 930
        __M_writer(escape(_("Creating a new UserIdResolver")))
        __M_writer(u"' );\n\t\t$('#button_new_resolver_type_ldap .ui-button-text').html('")
        # SOURCE LINE 931
        __M_writer(escape(_("LDAP")))
        __M_writer(u"');\n\t\t$('#button_new_resolver_type_sql .ui-button-text').html('")
        # SOURCE LINE 932
        __M_writer(escape(_("SQL")))
        __M_writer(u"');\n\t\t$('#button_new_resolver_type_scim .ui-button-text').html('")
        # SOURCE LINE 933
        __M_writer(escape(_("SCIM")))
        __M_writer(u"');\n\t\t$('#button_new_resolver_type_flatfile .ui-button-text').html('")
        # SOURCE LINE 934
        __M_writer(escape(_("Flatfile")))
        __M_writer(u"');\n\t\t$('#button_new_resolver_type_cancel .ui-button-text').html('")
        # SOURCE LINE 935
        __M_writer(escape(_("Cancel")))
        __M_writer(u'\');\n\t}\n</script>\n\n<!-- ################### edit realm ####################################### -->\n<div id=\'dialog_edit_realms\'>\n\t<div style="float:right">\n\t<a href=\'')
        # SOURCE LINE 942
        __M_writer(escape(c.help_url))
        __M_writer(u'/configuration/realms.html#edit-realm\' target="_blank">\n\t<img alt="(?)" width=24\n\tsrc="/images/help32.png"  \n\ttitle=\'')
        # SOURCE LINE 945
        __M_writer(escape(_("Open help on Realms")))
        __M_writer(u"'>\n\t</a>\n\t</div>\n\t<!--")
        # SOURCE LINE 948
        __M_writer(escape(_("Here you can add or remove existing resolvers to the realm")))
        __M_writer(u':-->\n\t<form class="cmxform" id="form_realmconfig">\n\t\t<div id=\'realm_intro_new\'>\n\t\t\t<p>')
        # SOURCE LINE 951
        __M_writer(escape(_("You are creating a new realm.")))
        __M_writer(u'\n\t\t\t')
        # SOURCE LINE 952
        __M_writer(escape(_("You may add resolvers by holding down Ctrl-Key and left-clicking.")))
        __M_writer(u'</p>')
        # SOURCE LINE 953
        __M_writer(u'\t\t\t<p><label for=realm_name>')
        __M_writer(escape(_("Realm name")))
        __M_writer(u':</label>\n\t\t\t\t<input type=\'text\' class="required" id=\'realm_name\' size=\'20\' maxlength=\'60\' value="" />\n\t\t\t\t</p>\n\t\t</div>\n\t\t<div id=\'realm_intro_edit\'>\n\t\t\t<p>')
        # SOURCE LINE 958
        __M_writer(escape(_("Here you may define the resolvers belonging to the realm")))
        __M_writer(u":</p>\n\t\t\t\t<p><b><span id='realm_edit_realm_name'> </span></b></p>\n\t\t\t\t<p>")
        # SOURCE LINE 960
        __M_writer(escape(_("You may add resolvers by holding down Ctrl-Key and left-clicking.")))
        __M_writer(u'</p>\n\t\t\t\t<input type=\'hidden\' id=\'realm_name\' size=\'20\' maxlength=\'60\'/>\n\t\t</div>\n\n\t\t<div id=\'realm_edit_resolver_list\'> </div>\n    </form>\n</div>\n<script>\n\tfunction translate_dialog_realm_edit() {\n\t\t$("#dialog_edit_realms" ).dialog( "option", "title", \'')
        # SOURCE LINE 969
        __M_writer(escape(_("Edit Realm")))
        __M_writer(u"' );\n\t\t$('#button_editrealms_cancel .ui-button-text').html('")
        # SOURCE LINE 970
        __M_writer(escape(_("Cancel")))
        __M_writer(u"');\n\t\t$('#button_editrealms_save .ui-button-text').html('")
        # SOURCE LINE 971
        __M_writer(escape(_("Save")))
        __M_writer(u"');\n\t}\n</script>\n\n<!-- ################# delete token ######################### -->\n<div id='dialog_delete_token'>\n\t<p>")
        # SOURCE LINE 977
        __M_writer(escape(_("The following tokens will be permanently deleted and can not be recovered.")))
        __M_writer(u'\n\t</p>\n\t<span id=\'delete_info\'>\t</span>\n</div>\n<script>\n\tfunction translate_dialog_delete_token() {\n\t\t$("#dialog_delete_token" ).dialog( "option", "title", \'')
        # SOURCE LINE 983
        __M_writer(escape(_("Delete selected tokens?")))
        __M_writer(u"' );\n\t\t$('#button_delete_delete .ui-button-text').html('")
        # SOURCE LINE 984
        __M_writer(escape(_("Delete tokens")))
        __M_writer(u"');\n\t\t$('#button_delete_cancel .ui-button-text').html('")
        # SOURCE LINE 985
        __M_writer(escape(_("Cancel")))
        __M_writer(u"');\n\t}\n</script>\n\n\n<!-- ########################### token enrollment ############ -->\n<div id='dialog_show_enroll_url'>\n\t<p>\n\t")
        # SOURCE LINE 993
        __M_writer(escape(_("Enrolled the token")))
        __M_writer(u" <b><span id='token_enroll_serial'> </span></b>\n\t")
        # SOURCE LINE 994
        __M_writer(escape(_("for user")))
        __M_writer(u' <span id=\'token_enroll_user\'> </span>.\n\t</p>\n\n\t<div id=\'enroll_url\'> </div>\n</div>\n<script>\n\tfunction translate_dialog_show_enroll_url() {\n\t\t$("#dialog_show_enroll_url" ).dialog( "option", "title", \'')
        # SOURCE LINE 1001
        __M_writer(escape(_("token enrollment")))
        __M_writer(u"' );\n\t\t$('#button_show_enroll_ok .ui-button-text').html('")
        # SOURCE LINE 1002
        __M_writer(escape(_("OK")))
        __M_writer(u"');\n\t}\n</script>\n<!--\n<div id='dialog_enroll'>\n\t<p>\n\t")
        # SOURCE LINE 1008
        __M_writer(escape(_("Enrolled the token")))
        __M_writer(u" <b><span id='token_enroll_serial_0'> </span></b>\n\t")
        # SOURCE LINE 1009
        __M_writer(escape(_("for user")))
        __M_writer(u' <span id=\'token_enroll_user_0\'> </span>.\n\t</p>\n\t<div id=\'enroll_dialog\'> </div>\n</div>\n<script>\n\tfunction translate_dialog_show_enroll_url() {\n\t\t$("#dialog_show_enroll_url" ).dialog( "option", "title", \'')
        # SOURCE LINE 1015
        __M_writer(escape(_("token enrollment")))
        __M_writer(u"' );\n\t\t$('#button_show_enroll_ok .ui-button-text').html('")
        # SOURCE LINE 1016
        __M_writer(escape(_("OK")))
        __M_writer(u"');\n\t}\n</script>\n-->\n<!-- #################### dialog lost token######################### -->\n<div id='dialog_lost_token'>\n\t<p>")
        # SOURCE LINE 1022
        __M_writer(escape(_("Token serial")))
        __M_writer(u" <span id='lost_token_serial'> </span> </p>\n\t<p>")
        # SOURCE LINE 1023
        __M_writer(escape(_("The token was lost? You may enroll a temporary token and automatically disable the lost token.")))
        __M_writer(u'</p>\n</div>\n<script>\n\tfunction translate_dialog_lost_token() {\n\t\t$("#dialog_lost_token" ).dialog( "option", "title", \'')
        # SOURCE LINE 1027
        __M_writer(escape(_("Lost Token")))
        __M_writer(u"' );\n\t\t$('#button_losttoken_ok .ui-button-text').html('")
        # SOURCE LINE 1028
        __M_writer(escape(_("Get temporary token")))
        __M_writer(u"');\n\t\t$('#button_losttoken_cancel .ui-button-text').html('")
        # SOURCE LINE 1029
        __M_writer(escape(_("Cancel")))
        __M_writer(u'\');\n\t}\n</script>\n\n<!-- ##################### dialog token info######################### -->\n<div id=\'dialog_token_info\'>\n</div>\n<script>\n\tfunction translate_dialog_token_info() {\n\t\t$("#dialog_token_info" ).dialog( "option", "title", \'')
        # SOURCE LINE 1038
        __M_writer(escape(_("Token info")))
        __M_writer(u"' );\n\t\t$('#button_ti_hashlib .ui-button-text').html('")
        # SOURCE LINE 1039
        __M_writer(escape(_("Hashlib")))
        __M_writer(u"');\n\t\t$('#button_ti_close .ui-button-text').html('")
        # SOURCE LINE 1040
        __M_writer(escape(_("Close")))
        __M_writer(u"');\n\t\t$('#button_ti_otplength .ui-button-text').html('")
        # SOURCE LINE 1041
        __M_writer(escape(_("OTP length")))
        __M_writer(u"');\n\t\t$('#button_ti_counterwindow .ui-button-text').html('")
        # SOURCE LINE 1042
        __M_writer(escape(_("Counter Window")))
        __M_writer(u"');\n\t\t$('#button_ti_failcount .ui-button-text').html('")
        # SOURCE LINE 1043
        __M_writer(escape(_("Max Fail Counter")))
        __M_writer(u"');\n\t\t$('#button_ti_countauthmax .ui-button-text').html('")
        # SOURCE LINE 1044
        __M_writer(escape(_("Max Auth Count")))
        __M_writer(u"');\n\t\t$('#button_ti_countauthsuccessmax .ui-button-text').html('")
        # SOURCE LINE 1045
        __M_writer(escape(_("Max Successful Auth Count")))
        __M_writer(u"');\n\t\t$('#button_ti_validityPeriodStart .ui-button-text').html('")
        # SOURCE LINE 1046
        __M_writer(escape(_("Validity start")))
        __M_writer(u"');\n\t\t$('#button_ti_validityPeriodEnd .ui-button-text').html('")
        # SOURCE LINE 1047
        __M_writer(escape(_("Validity end")))
        __M_writer(u"');\n\t\t$('#button_ti_syncwindow .ui-button-text').html('")
        # SOURCE LINE 1048
        __M_writer(escape(_("Sync Window")))
        __M_writer(u"');\n\t\t$('#button_ti_timewindow .ui-button-text').html('")
        # SOURCE LINE 1049
        __M_writer(escape(_("Time Window")))
        __M_writer(u"');\n\t\t$('#button_ti_timeshift .ui-button-text').html('")
        # SOURCE LINE 1050
        __M_writer(escape(_("Time Shift")))
        __M_writer(u"');\n\t\t$('#button_ti_timestep .ui-button-text').html('")
        # SOURCE LINE 1051
        __M_writer(escape(_("Time Step")))
        __M_writer(u'\');\n\t}\n</script>\n\n<!-- ############### dialog token info details ######################### -->\n<div id=\'dialog_tokeninfo_set\'>\n\n</div>\n<script>\n\tfunction translate_dialog_ti_hashlib() {\n\t\t$("#dialog_tokeninfo_set" ).dialog( "option", "title", \'')
        # SOURCE LINE 1061
        __M_writer(escape(_("set Hashlib")))
        __M_writer(u"' );\n\t\t$('#button_tokeninfo_ok .ui-button-text').html('")
        # SOURCE LINE 1062
        __M_writer(escape(_("OK")))
        __M_writer(u"');\n\t\t$('#button_tokeninfo_cancel .ui-button-text').html('")
        # SOURCE LINE 1063
        __M_writer(escape(_("Cancel")))
        __M_writer(u'\');\n\t}\n\tfunction translate_dialog_ti_otplength() {\n\t\t$("#dialog_tokeninfo_set" ).dialog( "option", "title", \'')
        # SOURCE LINE 1066
        __M_writer(escape(_("set OTP length")))
        __M_writer(u"' );\n\t\t$('#button_tokeninfo_ok .ui-button-text').html('")
        # SOURCE LINE 1067
        __M_writer(escape(_("OK")))
        __M_writer(u"');\n\t\t$('#button_tokeninfo_cancel .ui-button-text').html('")
        # SOURCE LINE 1068
        __M_writer(escape(_("Cancel")))
        __M_writer(u'\');\n\t}\n\tfunction translate_dialog_ti_counterwindow() {\n\t\t$("#dialog_tokeninfo_set" ).dialog( "option", "title", \'')
        # SOURCE LINE 1071
        __M_writer(escape(_("set Counter Window")))
        __M_writer(u"' );\n\t\t$('#button_tokeninfo_ok .ui-button-text').html('")
        # SOURCE LINE 1072
        __M_writer(escape(_("OK")))
        __M_writer(u"');\n\t\t$('#button_tokeninfo_cancel .ui-button-text').html('")
        # SOURCE LINE 1073
        __M_writer(escape(_("Cancel")))
        __M_writer(u'\');\n\t}\n\tfunction translate_dialog_ti_maxfailcount() {\n\t\t$("#dialog_tokeninfo_set" ).dialog( "option", "title", \'')
        # SOURCE LINE 1076
        __M_writer(escape(_("set Max Failcount")))
        __M_writer(u"' );\n\t\t$('#button_tokeninfo_ok .ui-button-text').html('")
        # SOURCE LINE 1077
        __M_writer(escape(_("OK")))
        __M_writer(u"');\n\t\t$('#button_tokeninfo_cancel .ui-button-text').html('")
        # SOURCE LINE 1078
        __M_writer(escape(_("Cancel")))
        __M_writer(u'\');\n\t}\n\tfunction translate_dialog_ti_countauthmax() {\n\t\t$("#dialog_tokeninfo_set" ).dialog( "option", "title", \'')
        # SOURCE LINE 1081
        __M_writer(escape(_("set Max Auth Count")))
        __M_writer(u"' );\n\t\t$('#button_tokeninfo_ok .ui-button-text').html('")
        # SOURCE LINE 1082
        __M_writer(escape(_("OK")))
        __M_writer(u"');\n\t\t$('#button_tokeninfo_cancel .ui-button-text').html('")
        # SOURCE LINE 1083
        __M_writer(escape(_("Cancel")))
        __M_writer(u'\');\n\t}\n\tfunction translate_dialog_ti_countauthsuccessmax() {\n\t\t$("#dialog_tokeninfo_set" ).dialog( "option", "title", \'')
        # SOURCE LINE 1086
        __M_writer(escape(_("set Max Successful Auth Count")))
        __M_writer(u"' );\n\t\t$('#button_tokeninfo_ok .ui-button-text').html('")
        # SOURCE LINE 1087
        __M_writer(escape(_("OK")))
        __M_writer(u"');\n\t\t$('#button_tokeninfo_cancel .ui-button-text').html('")
        # SOURCE LINE 1088
        __M_writer(escape(_("Cancel")))
        __M_writer(u'\');\n\t}\n\tfunction translate_dialog_ti_validityPeriodStart() {\n\t\t$("#dialog_tokeninfo_set" ).dialog( "option", "title", \'')
        # SOURCE LINE 1091
        __M_writer(escape(_("Validity start")))
        __M_writer(u"' );\n\t\t$('#button_tokeninfo_ok .ui-button-text').html('")
        # SOURCE LINE 1092
        __M_writer(escape(_("OK")))
        __M_writer(u"');\n\t\t$('#button_tokeninfo_cancel .ui-button-text').html('")
        # SOURCE LINE 1093
        __M_writer(escape(_("Cancel")))
        __M_writer(u'\');\n\t}\n\tfunction translate_dialog_ti_validityPeriodEnd() {\n\t\t$("#dialog_tokeninfo_set" ).dialog( "option", "title", \'')
        # SOURCE LINE 1096
        __M_writer(escape(_("Validity end")))
        __M_writer(u"' );\n\t\t$('#button_tokeninfo_ok .ui-button-text').html('")
        # SOURCE LINE 1097
        __M_writer(escape(_("OK")))
        __M_writer(u"');\n\t\t$('#button_tokeninfo_cancel .ui-button-text').html('")
        # SOURCE LINE 1098
        __M_writer(escape(_("Cancel")))
        __M_writer(u'\');\n\t}\n\tfunction translate_dialog_ti_countauthmax() {\n\t\t$("#dialog_tokeninfo_set" ).dialog( "option", "title", \'')
        # SOURCE LINE 1101
        __M_writer(escape(_("set Max Auth Count")))
        __M_writer(u"' );\n\t\t$('#button_tokeninfo_ok .ui-button-text').html('")
        # SOURCE LINE 1102
        __M_writer(escape(_("OK")))
        __M_writer(u"');\n\t\t$('#button_tokeninfo_cancel .ui-button-text').html('")
        # SOURCE LINE 1103
        __M_writer(escape(_("Cancel")))
        __M_writer(u'\');\n\t}\n\tfunction translate_dialog_ti_countauthsuccessmax() {\n\t\t$("#dialog_tokeninfo_set" ).dialog( "option", "title", \'')
        # SOURCE LINE 1106
        __M_writer(escape(_("set Max Successful Auth Count")))
        __M_writer(u"' );\n\t\t$('#button_tokeninfo_ok .ui-button-text').html('")
        # SOURCE LINE 1107
        __M_writer(escape(_("OK")))
        __M_writer(u"');\n\t\t$('#button_tokeninfo_cancel .ui-button-text').html('")
        # SOURCE LINE 1108
        __M_writer(escape(_("Cancel")))
        __M_writer(u'\');\n\t}\n\tfunction translate_dialog_ti_validityPeriodStart() {\n\t\t$("#dialog_tokeninfo_set" ).dialog( "option", "title", \'')
        # SOURCE LINE 1111
        __M_writer(escape(_("Validity start")))
        __M_writer(u"' );\n\t\t$('#button_tokeninfo_ok .ui-button-text').html('")
        # SOURCE LINE 1112
        __M_writer(escape(_("OK")))
        __M_writer(u"');\n\t\t$('#button_tokeninfo_cancel .ui-button-text').html('")
        # SOURCE LINE 1113
        __M_writer(escape(_("Cancel")))
        __M_writer(u'\');\n\t}\n\tfunction translate_dialog_ti_validityPeriodEnd() {\n\t\t$("#dialog_tokeninfo_set" ).dialog( "option", "title", \'')
        # SOURCE LINE 1116
        __M_writer(escape(_("Validity end")))
        __M_writer(u"' );\n\t\t$('#button_tokeninfo_ok .ui-button-text').html('")
        # SOURCE LINE 1117
        __M_writer(escape(_("OK")))
        __M_writer(u"');\n\t\t$('#button_tokeninfo_cancel .ui-button-text').html('")
        # SOURCE LINE 1118
        __M_writer(escape(_("Cancel")))
        __M_writer(u'\');\n\t}\n\tfunction translate_dialog_ti_phone() {\n\t\t$("#dialog_tokeninfo_set" ).dialog( "option", "title", \'')
        # SOURCE LINE 1121
        __M_writer(escape(_("Mobile phone number")))
        __M_writer(u"' );\n\t\t$('#button_tokeninfo_ok .ui-button-text').html('")
        # SOURCE LINE 1122
        __M_writer(escape(_("OK")))
        __M_writer(u"');\n\t\t$('#button_tokeninfo_cancel .ui-button-text').html('")
        # SOURCE LINE 1123
        __M_writer(escape(_("Cancel")))
        __M_writer(u'\');\n\t}\n\tfunction translate_dialog_ti_syncwindow(){\n\t\t$("#dialog_tokeninfo_set" ).dialog( "option", "title", \'')
        # SOURCE LINE 1126
        __M_writer(escape(_("set Sync Window")))
        __M_writer(u"' );\n\t\t$('#button_tokeninfo_ok .ui-button-text').html('")
        # SOURCE LINE 1127
        __M_writer(escape(_("OK")))
        __M_writer(u"');\n\t\t$('#button_tokeninfo_cancel .ui-button-text').html('")
        # SOURCE LINE 1128
        __M_writer(escape(_("Cancel")))
        __M_writer(u'\');\n\t}\n\tfunction translate_dialog_ti_timewindow(){\n\t\t$("#dialog_tokeninfo_set" ).dialog( "option", "title", \'')
        # SOURCE LINE 1131
        __M_writer(escape(_("set Time Window")))
        __M_writer(u"' );\n\t\t$('#button_tokeninfo_ok .ui-button-text').html('")
        # SOURCE LINE 1132
        __M_writer(escape(_("OK")))
        __M_writer(u"');\n\t\t$('#button_tokeninfo_cancel .ui-button-text').html('")
        # SOURCE LINE 1133
        __M_writer(escape(_("Cancel")))
        __M_writer(u'\');\n\t}\n\tfunction translate_dialog_ti_timeshift(){\n\t\t$("#dialog_tokeninfo_set" ).dialog( "option", "title", \'')
        # SOURCE LINE 1136
        __M_writer(escape(_("set Time Shift")))
        __M_writer(u"' );\n\t\t$('#button_tokeninfo_ok .ui-button-text').html('")
        # SOURCE LINE 1137
        __M_writer(escape(_("OK")))
        __M_writer(u"');\n\t\t$('#button_tokeninfo_cancel .ui-button-text').html('")
        # SOURCE LINE 1138
        __M_writer(escape(_("Cancel")))
        __M_writer(u'\');\n\t}\n\tfunction translate_dialog_ti_timestep(){\n\t\t$("#dialog_tokeninfo_set" ).dialog( "option", "title", \'')
        # SOURCE LINE 1141
        __M_writer(escape(_("set Time Step")))
        __M_writer(u"' );\n\t\t$('#button_tokeninfo_ok .ui-button-text').html('")
        # SOURCE LINE 1142
        __M_writer(escape(_("OK")))
        __M_writer(u"');\n\t\t$('#button_tokeninfo_cancel .ui-button-text').html('")
        # SOURCE LINE 1143
        __M_writer(escape(_("Cancel")))
        __M_writer(u'\');\n\t}\n\tfunction translate_dialog_ti_description(){\n\t\t$("#dialog_tokeninfo_set" ).dialog( "option", "title", \'')
        # SOURCE LINE 1146
        __M_writer(escape(_("set Description")))
        __M_writer(u"' );\n\t\t$('#button_tokeninfo_ok .ui-button-text').html('")
        # SOURCE LINE 1147
        __M_writer(escape(_("OK")))
        __M_writer(u"');\n\t\t$('#button_tokeninfo_cancel .ui-button-text').html('")
        # SOURCE LINE 1148
        __M_writer(escape(_("Cancel")))
        __M_writer(u"');\n\t}\n</script>\n\n\n\n<!-- ##################### resync token ############################# -->\n<div id='dialog_resync_token'>\n\t<p>")
        # SOURCE LINE 1156
        __M_writer(escape(_("You may resync the token:")))
        __M_writer(u" <span id='tokenid_resync'> </span>.</p>\n\t<p>")
        # SOURCE LINE 1157
        __M_writer(escape(_("Therefor please enter two OTP values.")))
        __M_writer(u'</p>\n\t<form><fieldset><table>\n    \t\t<tr><td>\n    \t\t<label for="otp1">OTP 1</label>\n    \t\t</td><td>\n    \t\t<input type="text" name="otp1" id="otp1" class="text ui-widget-content ui-corner-all" />\n    \t\t</td></tr><tr><td>\n    \t\t<label for="otp2">OTP 2</label>\n    \t\t</td><td>\n    \t\t<input type="text" name="otp2" id="otp2" class="text ui-widget-content ui-corner-all" />\n    \t\t</td></tr></table>\n    \t\t</fieldset>\n\t\t</form>\n</div>\n\n<script>\n\tfunction translate_dialog_resync_token() {\n\t\t$("#dialog_resync_token" ).dialog( "option", "title", \'')
        # SOURCE LINE 1174
        __M_writer(escape(_("Resync Token")))
        __M_writer(u"' );\n\t\t$('#button_resync_resync .ui-button-text').html('")
        # SOURCE LINE 1175
        __M_writer(escape(_("Resync")))
        __M_writer(u"');\n\t\t$('#button_resync_cancel .ui-button-text').html('")
        # SOURCE LINE 1176
        __M_writer(escape(_("Cancel")))
        __M_writer(u'\');\n\t}\n</script>\n\n<!-- ######################## dialog edit token realm ############# -->\n<div id=\'dialog_edit_tokenrealm\'>\n\t<form class="cmxform" id="form_tokenrealm">\n \t<p>')
        # SOURCE LINE 1183
        __M_writer(escape(_("Here you may define to which realms the token shall belong to:")))
        __M_writer(u"\n \t\t<span id='tokenid_realm'> </span></p>\n    <p>")
        # SOURCE LINE 1185
        __M_writer(escape(_("You may add realms by holding down Ctrl-Key and left-clicking.")))
        __M_writer(u'</p>\n\t<input type=\'hidden\' id=\'realm_name\' size=\'20\' maxlength=\'60\'>\n\t<div id=\'token_realm_list\'> </div>\n\t</form>\n</div>\n<script>\n\tfunction translate_dialog_token_realm() {\n\t\t$("#dialog_edit_tokenrealm" ).dialog( "option", "title", \'')
        # SOURCE LINE 1192
        __M_writer(escape(_("Edit Realms of Token")))
        __M_writer(u"' );\n\t\t$('#button_tokenrealm_save .ui-button-text').html('")
        # SOURCE LINE 1193
        __M_writer(escape(_("Save")))
        __M_writer(u"');\n\t\t$('#button_tokenrealm_cancel .ui-button-text').html('")
        # SOURCE LINE 1194
        __M_writer(escape(_("Cancel")))
        __M_writer(u"');\n\t}\n</script>\n\n<!-- ############### get list of OTP valus ############################ -->\n<div id='dialog_getmulti'>\n\t<p>")
        # SOURCE LINE 1200
        __M_writer(escape(_("You may get OTP values for token:")))
        __M_writer(u" <span id='tokenid_getmulti'> </span></p>\n    <p><label for=otp_values_count>")
        # SOURCE LINE 1201
        __M_writer(escape(_("Enter the number, how many OTP values you want to retrieve:")))
        __M_writer(u'</label></p>\n    <input id=\'otp_values_count\' maxlength=\'6\' class=\'required\'></input>\n</div>\n\n<script>\n\tfunction translate_dialog_getmulti() {\n\t\t$("#dialog_getmulti" ).dialog( "option", "title", \'')
        # SOURCE LINE 1207
        __M_writer(escape(_("Get OTP values")))
        __M_writer(u"' );\n\t\t$('#button_getmulti_ok .ui-button-text').html('")
        # SOURCE LINE 1208
        __M_writer(escape(_("OK")))
        __M_writer(u"');\n\t\t$('#button_getmulti_cancel .ui-button-text').html('")
        # SOURCE LINE 1209
        __M_writer(escape(_("Cancel")))
        __M_writer(u"');\n\t}\n</script>\n\n<!-- ########### unassign token############################# -->\n<div id='dialog_unassign_token'>\n\t<p>")
        # SOURCE LINE 1215
        __M_writer(escape(_("The following Tokens will be unassigned from the their users:")))
        __M_writer(u"\n\t\t<span id='tokenid_unassign'> </span></p>\n\t<p>")
        # SOURCE LINE 1217
        __M_writer(escape(_("The users will not be able to authenticate with this token anymore. Are you sure?")))
        __M_writer(u'\n\t</p>\n</div>\n<script>\n\tfunction translate_dialog_unassign() {\n\t\t$("#dialog_unassign_token" ).dialog( "option", "title", \'')
        # SOURCE LINE 1222
        __M_writer(escape(_("Unassign selected tokens?")))
        __M_writer(u"' );\n\t\t$('#button_unassign_unassign .ui-button-text').html('")
        # SOURCE LINE 1223
        __M_writer(escape(_("Unassign")))
        __M_writer(u"');\n\t\t$('#button_unassign_cancel .ui-button-text').html('")
        # SOURCE LINE 1224
        __M_writer(escape(_("Cancel")))
        __M_writer(u"');\n\t}\n</script>\n<!-- #################### realm ask delete ###################### -->\n<div id='dialog_realm_ask_delete'>\n\t")
        # SOURCE LINE 1229
        __M_writer(escape(_("Do you want to delete the realm")))
        __M_writer(u' <b><span id=\'realm_delete_name\'> </span></b>?\n</div>\n<script>\n\tfunction translate_dialog_realm_ask_delete() {\n\t\t$("#dialog_realm_ask_delete" ).dialog( "option", "title", \'')
        # SOURCE LINE 1233
        __M_writer(escape(_("Deleting realm")))
        __M_writer(u"' );\n\t\t$('#button_realm_ask_delete_delete .ui-button-text').html('")
        # SOURCE LINE 1234
        __M_writer(escape(_("Delete")))
        __M_writer(u"');\n\t\t$('#button_realm_ask_delete_cancel .ui-button-text').html('")
        # SOURCE LINE 1235
        __M_writer(escape(_("Cancel")))
        __M_writer(u"');\n\t}\n</script>\n<!-- ################## resolver ask delete ###################### -->\n<div id='dialog_resolver_ask_delete'>\n\t<p>")
        # SOURCE LINE 1240
        __M_writer(escape(_("Do you want to delete the resolver?")))
        __M_writer(u'</p>\n\t<p>\n\t\t')
        # SOURCE LINE 1242
        __M_writer(escape(_("Name")))
        __M_writer(u": <span id='delete_resolver_name'> </span><br>\n\t\t")
        # SOURCE LINE 1243
        __M_writer(escape(_("Type")))
        __M_writer(u': <span id=\'delete_resolver_type\'> </span>\n\t</p>\n</div>\n<script>\n\tfunction translate_dialog_resolver_ask_delete() {\n\t\t$("#dialog_resolver_ask_delete" ).dialog( "option", "title", \'')
        # SOURCE LINE 1248
        __M_writer(escape(_("Deleting resolver")))
        __M_writer(u"' );\n\t\t$('#button_resolver_ask_delete_delete .ui-button-text').html('")
        # SOURCE LINE 1249
        __M_writer(escape(_("Delete")))
        __M_writer(u"');\n\t\t$('#button_resolver_ask_delete_cancel .ui-button-text').html('")
        # SOURCE LINE 1250
        __M_writer(escape(_("Cancel")))
        __M_writer(u"');\n\t}\n</script>\n\n<!-- ############# temp token dialog ############################ -->\n<div id='dialog_view_temporary_token'>\n\t<p>\n\t\t")
        # SOURCE LINE 1257
        __M_writer(escape(_("Token enrolled. Use the old PIN with the password new password.")))
        __M_writer(u'\n\t\t')
        # SOURCE LINE 1258
        __M_writer(escape(_("The temporary token can be used till the end date.")))
        __M_writer(u'\n\t</p>\n\t<p>\n\t\t')
        # SOURCE LINE 1261
        __M_writer(escape(_("Serial")))
        __M_writer(u": <span id='temp_token_serial'> </span><br>\n\t\t")
        # SOURCE LINE 1262
        __M_writer(escape(_("Password")))
        __M_writer(u": <span id='temp_token_password'> </span><br>\n\t\t")
        # SOURCE LINE 1263
        __M_writer(escape(_("End date")))
        __M_writer(u': <span id=\'temp_token_enddate\'> </span>\n</div>\n<script>\n\tfunction translate_dialog_view_temptoken() {\n\t\t$("#dialog_view_temporary_token" ).dialog( "option", "title", \'')
        # SOURCE LINE 1267
        __M_writer(escape(_("New temporary token")))
        __M_writer(u"' );\n\t\t$('#button_view_temporary_token_close .ui-button-text').html('")
        # SOURCE LINE 1268
        __M_writer(escape(_("Close")))
        __M_writer(u'\');\n\t}\n</script>\n\n<!-- ################## dialog LDAP resolver ######################### -->\n\n<div id=\'dialog_ldap_resolver\'>\n\t<div style="float:right">\n\t<a href=\'')
        # SOURCE LINE 1276
        __M_writer(escape(c.help_url))
        __M_writer(u'/configuration/useridresolvers.html#ldap-resolver\' target="_blank">\n\t<img alt="(?)" width=24\n\tsrc="/images/help32.png"  \n\ttitle=\'')
        # SOURCE LINE 1279
        __M_writer(escape(_("Open help on LDAP resolver")))
        __M_writer(u'\'>\n\t</a>\n\t</div>\n\t<form class="cmxform" id="form_ldapconfig"><fieldset name="Server config"><table>\n\t\t\t<tr><td><label for=ldap_resolvername>')
        # SOURCE LINE 1283
        __M_writer(escape(_("Resolver name")))
        __M_writer(u':</label></td>\n\t\t\t\t<td><input type="text" name="ldap_resolvername" class="required"  id="ldap_resolvername" size="35" maxlength="20"></td></tr>\n\t\t\t<tr><td><label for=ldap_uri>')
        # SOURCE LINE 1285
        __M_writer(escape(_("Server-URI")))
        __M_writer(u':</label></td>\n\t\t\t\t<td><input type="text" name="ldap_uri" class="required"  id="ldap_uri" size="35" maxlength="200"\n\t\t\t\t\tonkeyup="ldap_resolver_ldaps();"></td></tr>\n\t\t\t<tr id="ldap_resolver_certificate"><td>\n\t\t\t\t<label for="ldap_certificate">')
        # SOURCE LINE 1289
        __M_writer(escape(_("CA Certificate")))
        __M_writer(u':</label></td>\n\t\t\t\t<td><textarea name="ldap_certificate" id="ldap_certificate" cols="34" rows="5"\n\t\t\t\t\t title=\'')
        # SOURCE LINE 1291
        __M_writer(escape(_("If you are using LDAPS you can enter the CA certificate in PEM format here.")))
        __M_writer(u"'> </textarea></td>\n\t\t\t\t\t </tr>\n\t\t\t<tr><td><label for=ldap_basedn>")
        # SOURCE LINE 1293
        __M_writer(escape(_("BaseDN")))
        __M_writer(u':</label></td>\n\t\t\t\t<td><input type="text" name="ldap_basedn" class="required"  id="ldap_basedn" size="35" maxlength="200"></td></tr>\n\t\t\t<tr><td><label for=ldap_binddn>')
        # SOURCE LINE 1295
        __M_writer(escape(_("BindDN")))
        __M_writer(u':</label></td>\n\t\t\t\t<td><input type="text" name="ldap_binddn" id="ldap_binddn" size="35" maxlength="200"></td></tr>\n\t\t\t<tr><td><label for=ldap_password>')
        # SOURCE LINE 1297
        __M_writer(escape(_("Bind Password")))
        __M_writer(u'</label>:</td>\n\t\t\t\t<td><input type="password" autocomplete="off" name="ldap_password" id="ldap_password" size="35" maxlength="60"></td></tr>\n\t\t\t<tr><td><label for=ldap_timeout>')
        # SOURCE LINE 1299
        __M_writer(escape(_("Timeout")))
        __M_writer(u'</label>:</td>\n\t\t\t\t<td><input type="text" name="ldap_timeout" class="required"  id="ldap_timeout" size="35" maxlength="5"></td></tr>\n\t\t\t<tr><td><label for=ldap_sizelimit>')
        # SOURCE LINE 1301
        __M_writer(escape(_("Sizelimit")))
        __M_writer(u':</label></td>\n\t\t\t\t<td><input type="text" name="ldap_sizelimit" class="required"  id="ldap_sizelimit" size="35" maxlength="10"></td></tr>\n\t\t\t<tr><td> </td>\n\t\t\t\t<td><input type="checkbox" name="noreferrals" value="noreferralss" id="ldap_noreferrals">\n\t\t\t\t\t<label for=ldap_noreferrals>')
        # SOURCE LINE 1305
        __M_writer(escape(_("No anonymous referral chasing")))
        __M_writer(u"</label></td></tr>\n\t\t\t</table>\n\t\t\t</fieldset>\n\t\t\t<fieldset name='")
        # SOURCE LINE 1308
        __M_writer(escape(_("LDAP attributes")))
        __M_writer(u"'><table>\n\t\t\t<tr><td><label for=ldap_loginattr>")
        # SOURCE LINE 1309
        __M_writer(escape(_("LoginName Attribute")))
        __M_writer(u':</label></td>\n\t\t\t\t<td><input type="text" name="ldap_loginattr" class="required"  id="ldap_loginattr" size="35" maxlength="60"></td></tr>\n\t\t\t<tr><td><label for=ldap_searchfilter>')
        # SOURCE LINE 1311
        __M_writer(escape(_("Searchfilter")))
        __M_writer(u':</label></td>\n\t\t\t\t<td><input type="text" name="ldap_searchfilter" class="required"  id="ldap_searchfilter" size="35" maxlength="200"></td></tr>\n\t\t\t<tr><td><label for=ldap_userfilter>')
        # SOURCE LINE 1313
        __M_writer(escape(_("Userfilter")))
        __M_writer(u':</label></td>\n\t\t\t\t<td><input type="text" name="ldap_userfilter" class="required"  id="ldap_userfilter" size="35" maxlength="200"></td></tr>\n\t\t\t<tr><td><label for=ldap_mapping>')
        # SOURCE LINE 1315
        __M_writer(escape(_("Attribute mapping")))
        __M_writer(u':</label></td>\n\t\t\t\t<td><input type="text" name="ldap_mapping" class="required"  id="ldap_mapping" size="35" maxlength="200"></td></tr>\n\t\t\t<tr><td><label for=ldap_uidtype>')
        # SOURCE LINE 1317
        __M_writer(escape(_("UID Type")))
        __M_writer(u':</label></td>\n\t\t\t\t<td><input type="text" name="ldap_uidtype" id="ldap_uidtype" size="20" maxlength="20"></td></tr>\n\t\t\t</table>\n\t\t\t<button class="action-button" id="button_preset_ad">')
        # SOURCE LINE 1320
        __M_writer(escape(_("Preset AD")))
        __M_writer(u'</button>\n\t\t\t<button class="action-button" id="button_preset_ldap">')
        # SOURCE LINE 1321
        __M_writer(escape(_("Preset LDAP")))
        __M_writer(u'</button>\n\t\t\t</fieldset></form>\n\t\t\t<div id="progress_test_ldap"><img src="/images/ajax-loader.gif" border="0" alt=""> ')
        # SOURCE LINE 1323
        __M_writer(escape(_("Testing connections...")))
        __M_writer(u' </div>\n\t\t\t<button class="action-button" id="button_test_ldap">')
        # SOURCE LINE 1324
        __M_writer(escape(_("Test LDAP connection")))
        __M_writer(u'</button>')
        # SOURCE LINE 1325
        __M_writer(u'</div>\n<script>\n\tfunction translate_dialog_ldap_resolver() {\n\t\t$("#dialog_ldap_resolver" ).dialog( "option", "title", \'')
        # SOURCE LINE 1328
        __M_writer(escape(_("LDAP Resolver")))
        __M_writer(u"' );\n\t\t$('#button_test_ldap .ui-button-text').html('")
        # SOURCE LINE 1329
        __M_writer(escape(_("Test LDAP connection")))
        __M_writer(u"');\n\t\t$('#button_preset_ad .ui-button-text').html('")
        # SOURCE LINE 1330
        __M_writer(escape(_("Preset AD")))
        __M_writer(u"');\n\t\t$('#button_preset_ldap .ui-button-text').html('")
        # SOURCE LINE 1331
        __M_writer(escape(_("Preset LDAP")))
        __M_writer(u'\');\n\t}\n</script>\n\n<!-- #################### dialog SQL resolver #################################### -->\n\n<div id=\'dialog_sql_resolver\'>\n\t<div style="float:right">\n\t<a href=\'')
        # SOURCE LINE 1339
        __M_writer(escape(c.help_url))
        __M_writer(u'/configuration/useridresolvers.html#sql-resolver\' target="_blank">\n\t<img alt="(?)" width=24\n\tsrc="/images/help32.png"  \n\ttitle=\'')
        # SOURCE LINE 1342
        __M_writer(escape(_("Open help on SQL resolver")))
        __M_writer(u'\'>\n\t</a>\n\t</div>\n<form class="cmxform" id="form_sqlconfig"><fieldset name=\'')
        # SOURCE LINE 1345
        __M_writer(escape(_("Server config")))
        __M_writer(u"'><table>\n\t\t<tr><td><label for=sql_resolvername>")
        # SOURCE LINE 1346
        __M_writer(escape(_("Resolver name")))
        __M_writer(u':</label></td>\n\t\t\t<td><input type="text" name="sql_resolvername" class="required"  id="sql_resolvername" size="35" maxlength="20"></td></tr>\n\t\t<tr><td><label for=sql_driver>')
        # SOURCE LINE 1348
        __M_writer(escape(_("Driver")))
        __M_writer(u':</label></td>\n\t\t\t<td><input type="text" name="sql_driver" class="required"  id="sql_driver" size="35" maxlength="40"></td></tr>\n\t\t<tr><td><label for=sql_server>')
        # SOURCE LINE 1350
        __M_writer(escape(_("Server")))
        __M_writer(u':</label></td>\n\t\t\t<td><input type="text" name="sql_server"  id="sql_server" size="35" maxlength="80"></td></tr>\n\t\t<tr><td><label for=sql_port>')
        # SOURCE LINE 1352
        __M_writer(escape(_("Port")))
        __M_writer(u':</label></td>\n\t\t\t<td><input type="text" name="sql_port"  id="sql_port" size="35" maxlength="5"></td></tr>\n\t\t<tr><td><label for=sql_database>')
        # SOURCE LINE 1354
        __M_writer(escape(_("Database")))
        __M_writer(u':</label></td>\n\t\t\t<td><input type="text" name="sql_database"  id="sql_database" size="35" maxlength="60"></td></tr>\n\t\t<tr><td><label for=sql_user>')
        # SOURCE LINE 1356
        __M_writer(escape(_("User")))
        __M_writer(u':</label></td>\n\t\t\t<td><input type="text" name="sql_user"   id="sql_user" size="35" maxlength="60"></td></tr>\n\t\t<tr><td><label for=sql_password>')
        # SOURCE LINE 1358
        __M_writer(escape(_("Password")))
        __M_writer(u':</label></td>\n\t\t\t<td><input type="password" autocomplete="off" name="sql_password"  id="sql_password" size="35" maxlength="60"></td></tr>\n\t\t</table>\n\t\t</fieldset>\n\t\t<fieldset name=\'')
        # SOURCE LINE 1362
        __M_writer(escape(_("SQL attributes")))
        __M_writer(u"'>\n\t\t\t<legend>")
        # SOURCE LINE 1363
        __M_writer(escape(_("SQL attributes")))
        __M_writer(u'</legend>\n\t\t<table>\n\t\t<tr><td><label for=sql_table>')
        # SOURCE LINE 1365
        __M_writer(escape(_("Database table")))
        __M_writer(u':</label></td>\n\t\t\t<td><input type="text" name="sql_table" class="required"  id="sql_table" size="35" maxlength="60"></td></tr>\n\t\t<tr><td><label for=sql_limit>')
        # SOURCE LINE 1367
        __M_writer(escape(_("Limit")))
        __M_writer(u':</label></td>\n\t\t\t<td><input type="text" name="sql_limit" class="required"  id="sql_limit" size="35" maxlength="5"></td></tr>\n\t\t<tr><td><label for=sql_mapping>')
        # SOURCE LINE 1369
        __M_writer(escape(_("Attribute mapping")))
        __M_writer(u':</label></td>\n\t\t\t<td><input type="text" name="sql_mapping" class="required"  id="sql_mapping" size="35" maxlength="200"></td></tr>\n\t\t<tr><td><label for=sql_where>')
        # SOURCE LINE 1371
        __M_writer(escape(_("Where statement")))
        __M_writer(u':</label></td>\n\t\t\t<td><input type="text" name="sql_where" class="optional"  id="sql_where" size="35" maxlength="200"></td></tr>\n\t\t<tr><td><label for=sql_encoding>')
        # SOURCE LINE 1373
        __M_writer(escape(_("Database encoding")))
        __M_writer(u':</label></td>\n\t\t\t<td><input type="text" name="sql_encoding" class="optional"  id="sql_encoding" size="35" maxlength="200"></td></tr>\n\t\t<tr><td><label for=sql_conparams>')
        # SOURCE LINE 1375
        __M_writer(escape(_("Additional connection parameters")))
        __M_writer(u':</label></td>\n\t\t\t<td><input type="text" name="sql_conparams" class="optional"  id="sql_conparams" size="35" maxlength="200"></td></tr>\n\t\t</table>\t\t\n\t\t<fieldset name=\'')
        # SOURCE LINE 1378
        __M_writer(escape(_("Preset database attributes")))
        __M_writer(u"'>\n\t\t\t<legend>")
        # SOURCE LINE 1379
        __M_writer(escape(_("Preset database attributes")))
        __M_writer(u'</legend>\n\t\t<button  id="button_preset_sql_wordpress">')
        # SOURCE LINE 1380
        __M_writer(escape(_("Wordpress")))
        __M_writer(u'</button>\n\t\t<button  id="button_preset_sql_otrs">')
        # SOURCE LINE 1381
        __M_writer(escape(_("OTRS")))
        __M_writer(u'</button>\n\t\t<button  id="button_preset_sql_tine20">')
        # SOURCE LINE 1382
        __M_writer(escape(_("Tine 2.0")))
        __M_writer(u'</button>\n\t\t<button  id="button_preset_sql_owncloud">')
        # SOURCE LINE 1383
        __M_writer(escape(_("Owncloud")))
        __M_writer(u'</button>\n\t\t</fieldset>\n\t\t</fieldset></form>\n\t\t<div id="progress_test_sql"><img src="/images/ajax-loader.gif" border="0" alt=""> ')
        # SOURCE LINE 1386
        __M_writer(escape(_("Testing connections...")))
        __M_writer(u' </div>\n\t\t<button class="action-button" id="button_test_sql">')
        # SOURCE LINE 1387
        __M_writer(escape(_("Test SQL connection")))
        __M_writer(u'</button>\n</div>\n<script>\n\tfunction translate_dialog_sql_resolver() {\n\t\t$("#dialog_sql_resolver" ).dialog( "option", "title", \'')
        # SOURCE LINE 1391
        __M_writer(escape(_("SQL Resolver")))
        __M_writer(u"' );\n\t\t$('#button_test_sql .ui-button-text').html('")
        # SOURCE LINE 1392
        __M_writer(escape(_("Test SQL connection")))
        __M_writer(u'\');\n\t}\n</script>\n\n<!-- #################### dialog SCIM resolver #################################### -->\n\n<div id=\'dialog_scim_resolver\'>\n\t<div style="float:right">\n\t<a href=\'')
        # SOURCE LINE 1400
        __M_writer(escape(c.help_url))
        __M_writer(u'/configuration/useridresolvers.html#SCIM-resolver\' target="_blank">\n\t<img alt="(?)" width=24\n\tsrc="/images/help32.png"  \n\ttitle=\'')
        # SOURCE LINE 1403
        __M_writer(escape(_("Open help on SCIM resolver")))
        __M_writer(u'\'>\n\t</a>\n\t</div>\n<form class="cmxform" id="form_scimconfig">\n\t\t<fieldset name=\'')
        # SOURCE LINE 1407
        __M_writer(escape(_("SCIM config")))
        __M_writer(u"'><table>\n\t\t<tr><td><label for=scim_resolvername>")
        # SOURCE LINE 1408
        __M_writer(escape(_("Resolver name")))
        __M_writer(u':</label></td>\n\t\t\t<td><input type="text" name="scim_resolvername" class="required"  id="scim_resolvername" size="35" maxlength="20"></td></tr>\n\t\t<tr><td><label for=scim_authserver>')
        # SOURCE LINE 1410
        __M_writer(escape(_("URI auth server")))
        __M_writer(u':</label></td>\n\t\t\t<td><input type="text" name="scim_authserver" class="required"  id="scim_authserver" size="40" maxlength="80"></td></tr>\n\t\t<tr><td><label for=scim_resourceserver>')
        # SOURCE LINE 1412
        __M_writer(escape(_("URI resource server")))
        __M_writer(u':</label></td>\n\t\t\t<td><input type="text" name="scim_resourceserver"  id="scim_resourceserver" size="40" maxlength="80"></td></tr>\n\t\t<tr><td><label for=scim_client>')
        # SOURCE LINE 1414
        __M_writer(escape(_("Client")))
        __M_writer(u':</label></td>\n\t\t\t<td><input type="text" name="scim_client"  id="scim_client" size="40" maxlength="55"></td></tr>\n\t\t<tr><td><label for=scim_secret>')
        # SOURCE LINE 1416
        __M_writer(escape(_("Secret")))
        __M_writer(u':</label></td>\n\t\t\t<td><input type="text" autocomplete="off" name="scim_secret"  id="scim_secret" size="40" maxlength="55"></td></tr>\n\t\t<tr><td><label for=scim_mapping>')
        # SOURCE LINE 1418
        __M_writer(escape(_("Mapping")))
        __M_writer(u':</label></td>\n\t\t\t<td><input type="text" name="scim_mapping"  id="scim_mapping" size="40" maxlength="200"></td></tr>\n\t\t</table>\n\t\t</fieldset>\n\t\t</form>\n\t\t<div id="progress_test_scim"><img src="/images/ajax-loader.gif" border="0" alt=""> ')
        # SOURCE LINE 1423
        __M_writer(escape(_("Testing connections...")))
        __M_writer(u' </div>\n\t\t<button class="action-button" id="button_test_scim">')
        # SOURCE LINE 1424
        __M_writer(escape(_("Test SCIM connection")))
        __M_writer(u'</button>\n</div>\n<script>\n\tfunction translate_dialog_scim_resolver() {\n\t\t$("#dialog_scim_resolver" ).dialog( "option", "title", \'')
        # SOURCE LINE 1428
        __M_writer(escape(_("SCIM Resolver")))
        __M_writer(u"' );\n\t\t$('#button_test_scim .ui-button-text').html('")
        # SOURCE LINE 1429
        __M_writer(escape(_("Test SCIM connection")))
        __M_writer(u"');\n\t}\n</script>\n\n<!-- ################# confirm delete machine ######################### -->\n<div id='dialog_delete_machine_confirm'>\n    <p>")
        # SOURCE LINE 1435
        __M_writer(escape(_("The following machine with all assignments will be deleted.")))
        __M_writer(u'\n    </p>\n    <span id=\'delete_machine_info\'>    </span>\n</div>\n<script>\n    function translate_dialog_delete_machine_confirm() {\n        $("#dialog_delete_machine_confirm" ).dialog( "option", "title", \'')
        # SOURCE LINE 1441
        __M_writer(escape(_("Delete selected machine?")))
        __M_writer(u"' );\n        $('#button_delete_machine .ui-button-text').html('")
        # SOURCE LINE 1442
        __M_writer(escape(_("Delete machine")))
        __M_writer(u"');\n        $('#button_delete_machine_cancel .ui-button-text').html('")
        # SOURCE LINE 1443
        __M_writer(escape(_("Cancel")))
        __M_writer(u"');\n    }\n</script>\n\n<!-- ################# confirm delete application ######################### -->\n<div id='dialog_delete_app_confirm'>\n    <p>")
        # SOURCE LINE 1449
        __M_writer(escape(_("The following application and token will be removed from the machine:")))
        __M_writer(u'\n    </p>\n    <span id=\'delete_app_info\'>    </span>\n</div>\n<script>\n    function translate_dialog_delete_app_confirm() {\n        $("#dialog_delete_app_confirm" ).dialog( "option", "title", \'')
        # SOURCE LINE 1455
        __M_writer(escape(_("Remove selected application?")))
        __M_writer(u"' );\n        $('#button_delete_app .ui-button-text').html('")
        # SOURCE LINE 1456
        __M_writer(escape(_("Remove application")))
        __M_writer(u"');\n        $('#button_delete_app_cancel .ui-button-text').html('")
        # SOURCE LINE 1457
        __M_writer(escape(_("Cancel")))
        __M_writer(u'\');\n    }\n</script>\n\n<!-- ################ dialog file resolver #################### -->\n\n<div id="dialog_file_resolver">\n\t<div style="float:right">\n\t<a href=\'')
        # SOURCE LINE 1465
        __M_writer(escape(c.help_url))
        __M_writer(u'/configuration/useridresolvers.html#flatfile-resolver\' target="_blank">\n\t<img alt="(?)" width=24\n\tsrc="/images/help32.png"  \n\ttitle=\'')
        # SOURCE LINE 1468
        __M_writer(escape(_("Open help on LDAP resolver")))
        __M_writer(u'\'>\n\t</a>\n\t</div>\n<form class="cmxform" id="form_fileconfig"><fieldset name=\'')
        # SOURCE LINE 1471
        __M_writer(escape(_("File configuration")))
        __M_writer(u"'><table>\n\t\t<tr><td><label for=file_resolvername>")
        # SOURCE LINE 1472
        __M_writer(escape(_("Resolver name")))
        __M_writer(u':</label></td>\n\t\t\t<td><input type="text" name="file_resolvername" class="required"  id="file_resolvername" size="35" maxlength="20"></td></tr>\n\t\t<tr><td><label for=file_filename>')
        # SOURCE LINE 1474
        __M_writer(escape(_("filename")))
        __M_writer(u':</label></td>\n\t\t\t<td><input type="text" name="file_filename" class="required"  id="file_filename" size="35" maxlength="200"></td></tr>\n\t\t</table></fieldset></form>\n</div>\n<script>\n\tfunction translate_dialog_file_resolver() {\n\t\t$("#dialog_file_resolver" ).dialog( "option", "title", \'')
        # SOURCE LINE 1480
        __M_writer(escape(_("File Resolver")))
        __M_writer(u'\' );\n\t}\n</script>\n\n<!--  ################## dialog create default realm ################## -->\n\n<div id="dialog_autocreate_realm">\n\t<div style="float:right">\n\t<a href=\'')
        # SOURCE LINE 1488
        __M_writer(escape(c.help_url))
        __M_writer(u'/configuration/realms.html#autocreate-realm\' target="_blank">\t\n\t<img alt="(?)" width=24\n\tsrc="/images/help32.png"  \n\ttitle=\'')
        # SOURCE LINE 1491
        __M_writer(escape(_("Open help on auto creating default realm")))
        __M_writer(u'\'>\n\t</a>\n\t</div>\n\t<form class="cmxform" id="form_autocreate_realm">\n\t\t<p>\n\t\t')
        # SOURCE LINE 1496
        __M_writer(escape(_("""You have no user realm configured, yet. You will not be able 
		       to assign tokens to users. If you wish to, the system can create a 
		       default realm for you with the local users on the server.""")))
        # SOURCE LINE 1498
        __M_writer(u'\n\t\t</p>\n\t\t<p>\n\t\t')
        # SOURCE LINE 1501
        __M_writer(escape(_("""To learn more about realms and resolvers, click the question mark
			   in the green circle.""")))
        # SOURCE LINE 1502
        __M_writer(u'\n\t\t</p>\n\t\t<p>\n\t\t<br>\n\t\t')
        # SOURCE LINE 1506
        __M_writer(escape(_("Shall the system create this realm?")))
        __M_writer(u'\n\t\t</p>\n\t\t<p>\n\t\t<input type=checkbox id=cb_autocreate_realm \n\t\t       name=cb_autocreate_realm value="remember"> \n\t\t       ')
        # SOURCE LINE 1511
        __M_writer(escape(_("Do not ask again.")))
        __M_writer(u'\n\t\t</p>\n\t</form>\n</div>\n<script>\n\tfunction translate_dialog_autocreate_realm() {\n\t\t$("#dialog_autocreate_realm").dialog( "option", "title", \'')
        # SOURCE LINE 1517
        __M_writer(escape(_("Create default realm")))
        __M_writer(u"' );\n\t\t$('#button_autocreate_realm_yes .ui-button-text').html('")
        # SOURCE LINE 1518
        __M_writer(escape(_("Create realm")))
        __M_writer(u"');\n\t\t$('#button_autocreate_realm_no .ui-button-text').html('")
        # SOURCE LINE 1519
        __M_writer(escape(_("No")))
        __M_writer(u'\');\n\t}\n</script>\n\n<!-- ################ Alert ################################### -->\n<div id="all_alerts" style="display:none; height:0px;">\n<div id="text_resync_fail">')
        # SOURCE LINE 1525
        __M_writer(escape(_("Resyncing of token failed")))
        __M_writer(u'</div>\n<div id="text_resync_success">')
        # SOURCE LINE 1526
        __M_writer(escape(_("Resynced token successfully")))
        __M_writer(u'</div>\n<div id="text_setpin_success">')
        # SOURCE LINE 1527
        __M_writer(escape(_("set PIN successfully")))
        __M_writer(u'</div>\n<div id="text_only_one_token_ti">')
        # SOURCE LINE 1528
        __M_writer(escape(_("When displaying Token information you may only select one single Token.")))
        __M_writer(u'</div>\n<div id="text_only_one_token_type">')
        # SOURCE LINE 1529
        __M_writer(escape(_("When retrieving the token type you may only select one single Token.")))
        __M_writer(u'</div>\n<div id="text_enroll_type_error">')
        # SOURCE LINE 1530
        __M_writer(escape(_("Error: unknown tokentype in function token_enroll()")))
        __M_writer(u'</div>\n<div id="text_get_serial_no_otp">')
        # SOURCE LINE 1531
        __M_writer(escape(_("Could not find a token for this OTP value.")))
        __M_writer(u'</div>\n<div id="text_get_serial_error">')
        # SOURCE LINE 1532
        __M_writer(escape(_("Error finding a token to this OTP value.")))
        __M_writer(u'</div>\n<div id="text_privacyidea_comm_fail">')
        # SOURCE LINE 1533
        __M_writer(escape(_("Failed to communicate to privacyIDEA server")))
        __M_writer(u'</div>\n<div id="text_import_unknown_type">')
        # SOURCE LINE 1534
        __M_writer(escape(_("unknown token type to load!")))
        __M_writer(u'</div>\n<div id="text_sms_save_error">')
        # SOURCE LINE 1535
        __M_writer(escape(_("Error saving SMS configuration. Please check your configuration and your server")))
        __M_writer(u'</div>\n<div id="text_system_save_error">')
        # SOURCE LINE 1536
        __M_writer(escape(_("Error saving system configuration. Please check your configuration and your server")))
        __M_writer(u'</div>\n<div id="text_system_save_error_checkbox">')
        # SOURCE LINE 1537
        __M_writer(escape(_("Error saving system checkboxes configuration. Please check your configuration and your server")))
        __M_writer(u'</div>\n<div id="text_realm_regexp_error">')
        # SOURCE LINE 1538
        __M_writer(escape(_("Regexp error in realm. You need to select ONE realm to set it as default.")))
        __M_writer(u'</div>\n<div id="text_realm_name_error">')
        # SOURCE LINE 1539
        __M_writer(escape(_("There is an error in the realm name!")))
        __M_writer(u'</div>\n<div id="text_policy_set">')
        # SOURCE LINE 1540
        __M_writer(escape(_("Policy set.")))
        __M_writer(u'</div>\n<div id="text_policy_name_not_empty">')
        # SOURCE LINE 1541
        __M_writer(escape(_("Policy name is not defined!")))
        __M_writer(u'</div>\n<div id="text_policy_deleted">')
        # SOURCE LINE 1542
        __M_writer(escape(_("Policy deleted.")))
        __M_writer(u'</div>\n<div id="text_error_fetching_list">')
        # SOURCE LINE 1543
        __M_writer(escape(_("Error fetching list!")))
        __M_writer(u'</div>\n<div id="text_created_token">')
        # SOURCE LINE 1544
        __M_writer(escape(_("created token with serial")))
        __M_writer(u' <span class="text_param1"> </span></div>\n<div id="text_losttoken_failed">')
        # SOURCE LINE 1545
        __M_writer(escape(_("losttoken failed")))
        __M_writer(u': <span class="text_param1"> </span></div>\n<div id="text_setpin_failed">')
        # SOURCE LINE 1546
        __M_writer(escape(_("set token PIN failed")))
        __M_writer(u': <span class="text_param1"> </span></div>\n<div id="text_fetching_tokentype_failed">')
        # SOURCE LINE 1547
        __M_writer(escape(_("Error while fetching the tokentype")))
        __M_writer(u': <span class="text_param1"> </span></div>\n<div id="text_error_creating_token">')
        # SOURCE LINE 1548
        __M_writer(escape(_("Error creating token")))
        __M_writer(u': <span class="text_param1"> </span></div>\n<div id="text_failed">')
        # SOURCE LINE 1549
        __M_writer(escape(_("Failed")))
        __M_writer(u': <span class="text_param1"> </span></div>\n<div id="text_token_import_failed">')
        # SOURCE LINE 1550
        __M_writer(escape(_("Failed to import token")))
        __M_writer(u': <span class="text_param1"> </span></div>\n<div id="text_token_import_result">')
        # SOURCE LINE 1551
        __M_writer(escape(_("Token import result")))
        __M_writer(u': <span class="text_param1"> </span></div>\n<div id="text_policy_import_failed">')
        # SOURCE LINE 1552
        __M_writer(escape(_("Failed to import policies")))
        __M_writer(u': <span class="text_param1"> </span></div>\n<div id="text_policy_import_result">')
        # SOURCE LINE 1553
        __M_writer(escape(_("Policy import result")))
        __M_writer(u': <span class="text_param1"> </span></div>\n<div id="text_error_ldap">')
        # SOURCE LINE 1554
        __M_writer(escape(_("Error saving ldap configuration.")))
        __M_writer(u': <span class="text_param1"> </span></div>\n<div id="text_error_realm">')
        # SOURCE LINE 1555
        __M_writer(escape(_("Error saving realm configuration.")))
        __M_writer(u': <span class="text_param1"> </span></div>\n<div id="text_realm_created">')
        # SOURCE LINE 1556
        __M_writer(escape(_("Realm created")))
        __M_writer(u': <span class="text_param1"> </span></div>\n<div id="text_error_set_realm">')
        # SOURCE LINE 1557
        __M_writer(escape(_("Error setting Token realms")))
        __M_writer(u': <span class="text_param1"> </span></div>\n<div id="text_error_save_file">')
        # SOURCE LINE 1558
        __M_writer(escape(_("Error saving file configuration")))
        __M_writer(u': <span class="text_param1"> </span></div>\n<div id="text_error_save_sql">')
        # SOURCE LINE 1559
        __M_writer(escape(_("Error saving sql configuration")))
        __M_writer(u': <span class="text_param1"> </span></div>\n<div id="text_error_save_scim">')
        # SOURCE LINE 1560
        __M_writer(escape(_("Error saving SCIM configuration")))
        __M_writer(u': <span class="text_param1"> </span></div>\n<div id="text_resolver_delete_success">')
        # SOURCE LINE 1561
        __M_writer(escape(_("Resolver deleted successfully")))
        __M_writer(u': <span class="text_param1"> </span></div>\n<div id="text_resolver_delete_fail">')
        # SOURCE LINE 1562
        __M_writer(escape(_("Failed deleting resolver")))
        __M_writer(u': <span class="text_param1"> </span></div>\n<div id="text_realm_delete_success">')
        # SOURCE LINE 1563
        __M_writer(escape(_("Realm deleted")))
        __M_writer(u': <span class="text_param1"> </span></div>\n<div id="text_realm_delete_fail">')
        # SOURCE LINE 1564
        __M_writer(escape(_("Failed deleting Realm")))
        __M_writer(u': <span class="text_param1"> </span></div>\n<div id="text_regexp_error">')
        # SOURCE LINE 1565
        __M_writer(escape(_("Error in regular expression for")))
        __M_writer(u': <span class="text_param1"> </span></div>\n<div id="text_ldap_config_success">')
        # SOURCE LINE 1566
        __M_writer(escape(_("LDAP config seems to be OK! Number of users found")))
        __M_writer(u': <span class="text_param1"> </span></div>\n<div id="text_ldap_load_error">')
        # SOURCE LINE 1567
        __M_writer(escape(_("Error loading LDAP resolver")))
        __M_writer(u': <span class="text_param1"> </span></div>\n<div id="text_sql_load_error">')
        # SOURCE LINE 1568
        __M_writer(escape(_("Error loading SQL resolver")))
        __M_writer(u': <span class="text_param1"> </span></div>\n<div id="text_scim_load_error">')
        # SOURCE LINE 1569
        __M_writer(escape(_("Error loading SCIM resolver")))
        __M_writer(u': <span class="text_param1"> </span></div>\n<div id="text_sql_config_success">')
        # SOURCE LINE 1570
        __M_writer(escape(_("SQL config seems to be OK! Number of users found")))
        __M_writer(u': <span class="text_param1"> </span></div>\n<div id="text_sql_config_fail">')
        # SOURCE LINE 1571
        __M_writer(escape(_("SQL config contains errors")))
        __M_writer(u': <span class="text_param1"> </span></div>\n<div id="text_scim_config_success">')
        # SOURCE LINE 1572
        __M_writer(escape(_("SCIM config seems to be OK! Number of users found")))
        __M_writer(u': <span class="text_param1"> </span></div>\n<div id="text_scim_config_fail">')
        # SOURCE LINE 1573
        __M_writer(escape(_("SCIM config contains errors")))
        __M_writer(u': <span class="text_param1"> </span></div>\n<div id="text_unknown_pintype">')
        # SOURCE LINE 1574
        __M_writer(escape(_("Unknown PIN type")))
        __M_writer(u': <span class="text_param1"> </span></div>\n<div id="text_error_saving_system_config">')
        # SOURCE LINE 1575
        __M_writer(escape(_("You entered invalid data. Please check all the Tabs!")))
        __M_writer(u'</div>\n<div id="text_catching_generic_error">')
        # SOURCE LINE 1576
        __M_writer(escape(_("Error occurred during processing")))
        __M_writer(u': <span class="text_param1"> </span></div>\n<div id="text_no_realm">')
        # SOURCE LINE 1577
        __M_writer(escape(_("You have defined UserIdResolvers. But you need to create at least one realm that contains some of your UserIdResolvers. The realm Dialog will now open to do this.")))
        __M_writer(u'</div>\n<div id="text_already_default_realm">')
        # SOURCE LINE 1578
        __M_writer(escape(_("This realm is already the default realm.")))
        __M_writer(u'</div>\n<div id="text_form_validation_error1">')
        # SOURCE LINE 1579
        __M_writer(escape(_("Incorrect or missing input at")))
        __M_writer(u':<ul><span class="text_param1"> </span></ul>\n\t<div>')
        # SOURCE LINE 1580
        __M_writer(escape(_("Please have a look at each of the forms for more details.")))
        __M_writer(u'</div></div>\n<div id="text_form_validation_error_title">')
        # SOURCE LINE 1581
        __M_writer(escape(_("Form Validation Error")))
        __M_writer(u'</div>\n<div id="text_preset_sql">')
        # SOURCE LINE 1582
        __M_writer(escape(_("Please verify the presetted data. You might need to change the database table name.")))
        __M_writer(u'</div>\n<div id="title_preset_sql">')
        # SOURCE LINE 1583
        __M_writer(escape(_("SQL preset")))
        __M_writer(u'</div>\n<div id="text_delete_machine_success">')
        # SOURCE LINE 1584
        __M_writer(escape(_("Machine successfully deleted.")))
        __M_writer(u'</span></span></div>\n<div id="text_delete_app_success">')
        # SOURCE LINE 1585
        __M_writer(escape(_("Application removed successfully from machine.")))
        __M_writer(u'</span></span></div>\n<div id="text_create_machine_success">')
        # SOURCE LINE 1586
        __M_writer(escape(_("Machine created successfully.")))
        __M_writer(u'</span></span></div>\n<div id="text_add_option_missing_entry">')
        # SOURCE LINE 1587
        __M_writer(escape(_("Machine name, serial and application must not be emptry!")))
        __M_writer(u'</span></span></div>\n\n</div> <!-- all alerts -->\n</div> <!--end of hidden-->\n</div>  <!-- end of wrap -->\n\n</body>\n</html>\n\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


