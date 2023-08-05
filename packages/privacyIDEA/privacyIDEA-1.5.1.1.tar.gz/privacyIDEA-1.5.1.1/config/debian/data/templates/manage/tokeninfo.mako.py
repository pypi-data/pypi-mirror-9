# -*- coding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 9
_modified_time = 1422216716.690639
_enable_loop = True
_template_filename = '/usr/lib/python2.7/dist-packages/privacyidea/templates/manage/tokeninfo.mako'
_template_uri = '/manage/tokeninfo.mako'
_source_encoding = 'utf-8'
from webhelpers.html import escape
_exports = []


def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        c = context.get('c', UNDEFINED)
        len = context.get('len', UNDEFINED)
        _ = context.get('_', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 2
        __M_writer(u'\n')
        # SOURCE LINE 3

        ttype = c.tokeninfo.get("privacyIDEA.TokenType").lower()
        
        
        __M_locals_builtin_stored = __M_locals_builtin()
        __M_locals.update(__M_dict_builtin([(__M_key, __M_locals_builtin_stored[__M_key]) for __M_key in ['ttype'] if __M_key in __M_locals_builtin_stored]))
        # SOURCE LINE 5
        __M_writer(u'\n\n<div style="float:right">\n<a href=\'')
        # SOURCE LINE 8
        __M_writer(escape(c.help_url))
        __M_writer(u'/tokenview/index.html#token-info\' target="_blank">\n\t<img alt="(?)" width=24\n\tsrc="/images/help32.png"  \n\ttitle=\'')
        # SOURCE LINE 11
        __M_writer(escape(_("help on tokeninfo")))
        __M_writer(u"'>\n</a>\n</div>\n\n<table class=tokeninfoOuterTable>\n")
        # SOURCE LINE 16
        for value in c.tokeninfo:
            # SOURCE LINE 17
            __M_writer(u'    <tr>\n    \t<!-- left column -->\n    <td class=tokeninfoOuterTable>\n')
            # SOURCE LINE 20
            if value.startswith("privacyIDEA."):
                # SOURCE LINE 21
                __M_writer(u'    \t\t')
                __M_writer(escape(value[len("privacyIDEA."):]))
                __M_writer(u'\n')
                # SOURCE LINE 22
            else:
                # SOURCE LINE 23
                __M_writer(u'    \t\t')
                __M_writer(escape(value))
                __M_writer(u'\n')
            # SOURCE LINE 25
            __M_writer(u'    </td>\n    \t<!-- middle column -->\n    <td class=tokeninfoOuterTable>\n')
            # SOURCE LINE 28
            if "privacyIDEA.TokenInfo" == value:
                # SOURCE LINE 29
                __M_writer(u'    \t<table class=tokeninfoInnerTable>\n')
                # SOURCE LINE 30
                for k in c.tokeninfo[value]:
                    # SOURCE LINE 31
                    __M_writer(u'    \t<tr>  \t\t\n    \t<td class=tokeninfoInnerTable>')
                    # SOURCE LINE 32
                    __M_writer(escape(k))
                    __M_writer(u'</td>\n    \t<td class=tokeninfoInnerTable>')
                    # SOURCE LINE 33
                    __M_writer(escape(c.tokeninfo[value][k]))
                    __M_writer(u'</td>\n    \t</tr>\n')
                # SOURCE LINE 36
                __M_writer(u'    \t</table>\n    \t<div id="toolbar" class="ui-widget-header ui-corner-all">\n    \t\t<button id="ti_button_hashlib">')
                # SOURCE LINE 38
                __M_writer(escape(_("hashlib")))
                __M_writer(u'</button>\n\t\t\t<button id="ti_button_count_auth_max">')
                # SOURCE LINE 39
                __M_writer(escape(_("count auth")))
                __M_writer(u'</button>\n\t\t\t<button id="ti_button_count_auth_max_success">')
                # SOURCE LINE 40
                __M_writer(escape(_("count auth max")))
                __M_writer(u'</button>\n\t\t\t<button id="ti_button_valid_start">')
                # SOURCE LINE 41
                __M_writer(escape(_("count auth max")))
                __M_writer(u'</button>\n\t\t\t<button id="ti_button_valid_end">')
                # SOURCE LINE 42
                __M_writer(escape(_("count auth max")))
                __M_writer(u'</button>\n')
                # SOURCE LINE 43
                if ttype in [ "totp", "ocra" ]:
                    # SOURCE LINE 44
                    __M_writer(u'\t\t\t<button id="ti_button_time_window">')
                    __M_writer(escape(_("time window")))
                    __M_writer(u'</button>\n\t\t\t<button id="ti_button_time_step">')
                    # SOURCE LINE 45
                    __M_writer(escape(_("time step")))
                    __M_writer(u'</button>\n\t\t\t<button id="ti_button_time_shift">')
                    # SOURCE LINE 46
                    __M_writer(escape(_("time shift")))
                    __M_writer(u'</button>\n')
                # SOURCE LINE 48
                if ttype in [ "sms" ]:
                    # SOURCE LINE 49
                    __M_writer(u'\t\t\t<button id="ti_button_mobile_phone">')
                    __M_writer(escape(_("mobile phone number")))
                    __M_writer(u'</button>\n')
                # SOURCE LINE 51
                __M_writer(u'\t\t\t\n\t\t\t\n\t\t</div>\n')
                # SOURCE LINE 54
            elif "privacyIDEA.RealmNames" == value:
                # SOURCE LINE 55
                __M_writer(u'    \t<table class=tokeninfoInnerTable>\n')
                # SOURCE LINE 56
                for r in c.tokeninfo[value]:
                    # SOURCE LINE 57
                    __M_writer(u'    \t<tr>\n    \t\t<td class=tokeninfoInnerTable>')
                    # SOURCE LINE 58
                    __M_writer(escape(r))
                    __M_writer(u'</td>\n    \t</tr>\n')
                # SOURCE LINE 61
                __M_writer(u'    \t</table>\n')
                # SOURCE LINE 62
            else:
                # SOURCE LINE 63
                __M_writer(u'    \t')
                __M_writer(escape(c.tokeninfo[value]))
                __M_writer(u'\n')
            # SOURCE LINE 65
            __M_writer(u'    </td>\n        \t<!-- right column -->\n    <td>\n')
            # SOURCE LINE 68
            if value == "privacyIDEA.TokenDesc":
                # SOURCE LINE 69
                __M_writer(u'    \t\t<button id="ti_button_desc"></button>\n')
                # SOURCE LINE 70
            elif value == "privacyIDEA.OtpLen":
                # SOURCE LINE 71
                __M_writer(u'    \t\t<button id="ti_button_otplen"></button>\n')
                # SOURCE LINE 72
            elif value == "privacyIDEA.SyncWindow":
                # SOURCE LINE 73
                __M_writer(u'    \t\t<button id="ti_button_sync"></button>\n')
                # SOURCE LINE 74
            elif value == "privacyIDEA.CountWindow":
                # SOURCE LINE 75
                __M_writer(u'    \t\t<button id="ti_button_countwindow"></button>\n')
                # SOURCE LINE 76
            elif value == "privacyIDEA.MaxFail":
                # SOURCE LINE 77
                __M_writer(u'    \t\t<button id="ti_button_maxfail"></button>\n')
                # SOURCE LINE 78
            elif value == "privacyIDEA.FailCount":
                # SOURCE LINE 79
                __M_writer(u'    \t\t<button id="ti_button_failcount"></button>\n')
            # SOURCE LINE 81
            __M_writer(u'    \t\n    </td>\n    </tr>        \n')
        # SOURCE LINE 85
        __M_writer(u'</table>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


