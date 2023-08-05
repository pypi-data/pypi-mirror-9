# -*- coding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 9
_modified_time = 1422216496.431163
_enable_loop = True
_template_filename = '/usr/lib/python2.7/dist-packages/privacyidea/templates/manage/tokenview.mako'
_template_uri = '/manage/tokenview.mako'
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
        __M_writer(u"\n <button class='ui-button' id='button_losttoken'>")
        # SOURCE LINE 3
        __M_writer(escape(_("Lost token")))
        __M_writer(u"</button>\n <button class='ui-button' id='button_tokeninfo'>")
        # SOURCE LINE 4
        __M_writer(escape(_("Token info")))
        __M_writer(u"</button>\n <button class='ui-button' id='button_resync'>")
        # SOURCE LINE 5
        __M_writer(escape(_("Resync Token")))
        __M_writer(u"</button>\n <button class='ui-button' id='button_tokenrealm'>")
        # SOURCE LINE 6
        __M_writer(escape(_("set token realm")))
        __M_writer(u"</button>\n <button class='ui-button' id='button_getmulti'>")
        # SOURCE LINE 7
        __M_writer(escape(_("get OTP")))
        __M_writer(u"</button>\n \n <a href='")
        # SOURCE LINE 9
        __M_writer(escape(c.help_url))
        __M_writer(u'/tokenview/index.html\' target="_blank">\n\t<img alt="(?)" width=24\n\tsrc="/images/help32.png"  \n\ttitle=\'')
        # SOURCE LINE 12
        __M_writer(escape(_("help on tokenview")))
        __M_writer(u'\'>\n</a>\n \n<table id="token_table" class="flexme2" style="display:none"></table>\n   \n<script type="text/javascript"> \nview_token();\ntokenbuttons();\n</script>\n\n\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


