# -*- coding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 9
_modified_time = 1422216423.786438
_enable_loop = True
_template_filename = '/usr/lib/python2.7/dist-packages/privacyidea/templates/selfservice/login.mako'
_template_uri = '/selfservice/login.mako'
_source_encoding = 'utf-8'
from webhelpers.html import escape
_exports = []


def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        c = context.get('c', UNDEFINED)
        _ = context.get('_', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 2
        __M_writer(u'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">\n<html>\n<head>\n<title>privacyIDEA</title>\n<meta name="author" content="Cornelius K\xf6lbel">\n<meta name="date" content="2010-07-05T23:23:25+0200">\n<meta name="keywords" content="privacyIDEA login">\n<meta http-equiv="content-type" content="text/html; charset=UTF-8">\n<meta http-equiv="content-type" content="application/xhtml+xml; charset=UTF-8">\n<meta http-equiv="content-style-type" content="text/css">\n\n<link type="text/css" rel="stylesheet" href="/selfservice/style.css" />\n<link type="text/css" rel="stylesheet" href="/selfservice/custom-style.css" />\n<script type="text/javascript" src="/js/jquery-1.7.2.min.js"></script>\n\n</head>\n\n<body>\n\n<script>\n$(document).ready(function() {\n    $(\'form:first *:input[type!=hidden]:first\').focus();\n   \t$(\'#wrongCredentials\').delay(2000).fadeOut("slow");\n});\n</script>\n\n<div id="wrap">\n\n<div id="header-login">\n\t<div id="logo">\n\t</div>\n\t\n\t<div class="float_right">\n\t<span class=portalname>')
        # SOURCE LINE 35
        __M_writer(escape(_("privacyIDEA")))
        __M_writer(u'</span>\n\t</div>\n</div>\n\n\n\n<div id="main-login">\n<h1>')
        # SOURCE LINE 42
        __M_writer(escape(_("Login to privacyIDEA")))
        __M_writer(u'\n</h1>\n\n  <p>\n    <form action="/account/dologin" method="POST">\n      <table>\n        <tr><td><label for=login>')
        # SOURCE LINE 48
        __M_writer(escape(_("Username")))
        __M_writer(u':</label></td>\n        <td><input type="text" id="login" name="login" value="" /></td></tr>\n')
        # SOURCE LINE 50
        if c.realmbox:
            # SOURCE LINE 51
            __M_writer(u'        \t<tr>\n')
            # SOURCE LINE 52
        else:
            # SOURCE LINE 53
            __M_writer(u'\t\t\t<tr style="display:none;">\n')
        # SOURCE LINE 55
        __M_writer(u'\t\t<td>')
        __M_writer(escape(_("Realm")))
        __M_writer(u':</td>\n        <td>\n\t    <select name="realm">\n')
        # SOURCE LINE 58
        for realm in c.realmArray:
            # SOURCE LINE 59
            if c.defaultRealm == realm:
                # SOURCE LINE 60
                __M_writer(u'\t        <option value="')
                __M_writer(escape(realm))
                __M_writer(u'" selected>')
                __M_writer(escape(realm))
                __M_writer(u'</option>\n')
                # SOURCE LINE 61
            else:
                # SOURCE LINE 62
                __M_writer(u'\t        <option value="')
                __M_writer(escape(realm))
                __M_writer(u'">')
                __M_writer(escape(realm))
                __M_writer(u'</option>\n')
        # SOURCE LINE 65
        __M_writer(u'        </select>\n        </td></tr>\n        <tr><td><label for=password>')
        # SOURCE LINE 67
        __M_writer(escape(_("Password")))
        __M_writer(u':</label></td>\n        <td>\n        <input autocomplete="off" type="password" id="password" name="password" value ="" />\n')
        # SOURCE LINE 70
        if c.login_help:
            # SOURCE LINE 71
            __M_writer(u"\t\t\t<a href='")
            __M_writer(escape(c.help_url))
            __M_writer(u'/webui/login.html\' target="_blank">\n\t\t\t<img alt="(?)" width=24\n\t\t\tsrc="/images/help32.png"  \n\t\t\ttitle=\'')
            # SOURCE LINE 74
            __M_writer(escape(_("Open help on WebUI Login")))
            __M_writer(u"'>\n\t\t\t</a>\n")
        # SOURCE LINE 77
        __M_writer(u'        </td></tr>\n        <tr><td></td><td class=passwordWarning id=wrongCredentials>')
        # SOURCE LINE 78
        __M_writer(escape(c.status))
        __M_writer(u'</td></tr>\n        <tr><td></td>\n        <td>   <input type="submit" value="Login" /></td></tr>\n      </table>\n    </form>\n  </p>\n\n<div id=\'errorDiv\'></div>\n<div id=\'successDiv\'></div>\n\n\n</div>  <!-- end of main-->\n\n<!--\n<div id="footer">\n\t')
        # SOURCE LINE 93
        __M_writer(escape(c.version))
        __M_writer(u' | ')
        __M_writer(escape(c.licenseinfo))
        __M_writer(u'\n</div>\n-->\n</div>  <!-- end of wrap -->\n</body>\n</html>\n\n\n\n\n\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


