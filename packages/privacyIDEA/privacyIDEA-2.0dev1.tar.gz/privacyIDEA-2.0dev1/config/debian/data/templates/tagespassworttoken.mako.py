# -*- coding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 9
_modified_time = 1422216484.925574
_enable_loop = True
_template_filename = '/usr/lib/python2.7/dist-packages/privacyidea/lib/tokens/tagespassworttoken.mako'
_template_uri = '/tagespassworttoken.mako'
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
        __M_writer(u'\n')
        # SOURCE LINE 3
        if c.scope == 'enroll.title' :
            # SOURCE LINE 4
            __M_writer(escape(_("Day OTP Token / Tagespasswort")))
            __M_writer(u'\n')
        # SOURCE LINE 6
        __M_writer(u'\n')
        # SOURCE LINE 7
        if c.scope == 'enroll' :
            # SOURCE LINE 8
            __M_writer(u"\n<script>\n/*\n * 'typ'_get_enroll_params()\n *\n * this method is called, when the token  is submitted\n * - it will return a hash of parameters for admin/init call\n *\n */\n\nfunction dpw_get_enroll_params(){\n    var params = {};\n    params['type'] = 'dpw';\n    //params['serial'] = create_serial('DOTP');\n    params['otpkey'] \t= $('#dpw_key').val();\n\tparams['description'] =  $('#enroll_dpw_desc').val();\n\n\tjQuery.extend(params, add_user_data());\n\n    return params;\n}\n</script>\n\n<p>")
            # SOURCE LINE 31
            __M_writer(escape(_("Here you can define the 'Tagespasswort' token, that changes every day.")))
            __M_writer(u'</p>\n<table>\n<tr>\n\t<td><label for="dpw_key">')
            # SOURCE LINE 34
            __M_writer(escape(_("DPW key")))
            __M_writer(u'</label></td>\n\t<td><input type="text" name="dpw_key" id="dpw_key" value="" class="text ui-widget-content ui-corner-all" /></td>\n</tr>\n<tr>\n    <td><label for="enroll_dpw_desc" id=\'enroll_dpw_desc_label\'>')
            # SOURCE LINE 38
            __M_writer(escape(_("Description")))
            __M_writer(u'</label></td>\n    <td><input type="text" name="enroll_dpw_desc" id="enroll_dpw_desc" value="webGUI_generated" class="text" /></td>\n</tr>\n</table>\n\n\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


