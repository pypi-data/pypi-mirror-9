# -*- coding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 9
_modified_time = 1422216484.928316
_enable_loop = True
_template_filename = '/usr/lib/python2.7/dist-packages/privacyidea/lib/tokens/spasstoken.mako'
_template_uri = '/spasstoken.mako'
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
            __M_writer(escape(_("Simple Pass Token")))
            __M_writer(u'\n')
        # SOURCE LINE 6
        __M_writer(u'\n')
        # SOURCE LINE 7
        if c.scope == 'enroll' :
            # SOURCE LINE 8
            __M_writer(u'<script>\n/*\n * \'typ\'_get_enroll_params()\n *\n * this method is called, when the token  is submitted\n * - it will return a hash of parameters for admin/init call\n *\n */\n\nfunction spass_get_enroll_params(){\n    var params = {};\n    params[\'type\'] = \'spass\';\n    params[\'otpkey\'] = "1234";\n\tparams[\'description\'] =  $(\'#enroll_spass_desc\').val();\n\n\tjQuery.extend(params, add_user_data());\n\n    return params;\n}\n</script>\n\n<p>')
            # SOURCE LINE 29
            __M_writer(escape(_("The Simple Pass token will not require any one time password component.")))
            __M_writer(u'\n')
            # SOURCE LINE 30
            __M_writer(escape(_("Anyway, you can set an OTP PIN, so that using this token the user can "+
"authenticate always and only with this fixed PIN.")))
            # SOURCE LINE 31
            __M_writer(u'</p>\n\n<table>\n<tr>\n    <td><label for="enroll_spass_desc" id=\'enroll_spass_desc_label\'>')
            # SOURCE LINE 35
            __M_writer(escape(_("Description")))
            __M_writer(u'</label></td>\n    <td><input type="text" name="enroll_spass_desc" id="enroll_spass_desc" value="webGUI_generated" class="text" /></td>\n</tr>\n</table>\n\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


