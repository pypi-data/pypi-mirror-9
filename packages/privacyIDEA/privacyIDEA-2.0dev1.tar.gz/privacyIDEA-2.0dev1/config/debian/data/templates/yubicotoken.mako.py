# -*- coding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 9
_modified_time = 1422216484.849514
_enable_loop = True
_template_filename = '/usr/lib/python2.7/dist-packages/privacyidea/lib/tokens/yubicotoken.mako'
_template_uri = '/yubicotoken.mako'
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
        __M_writer(u'\n\n')
        # SOURCE LINE 4
        if c.scope == 'config.title' :
            # SOURCE LINE 5
            __M_writer(u' ')
            __M_writer(escape(_("Yubico")))
            __M_writer(u'\n')
        # SOURCE LINE 7
        __M_writer(u'\n')
        # SOURCE LINE 8
        if c.scope == 'selfservice.title.enroll':
            # SOURCE LINE 9
            __M_writer(escape(_("Enroll Yubikey")))
            __M_writer(u'\n')
        # SOURCE LINE 11
        __M_writer(u'\n')
        # SOURCE LINE 12
        if c.scope == 'config' :
            # SOURCE LINE 13
            __M_writer(u'<script>\n\n/*\n * \'typ\'_get_config_val()\n *\n * this method is called, when the token config dialog is opened\n * - it contains the mapping of config entries to the form id\n * - according to the Config entries, the form entries will be filled\n *\n */\n\n\nfunction yubico_get_config_val(){\n\tvar id_map = {};\n\n    id_map[\'yubico.id\'] \t\t= \'sys_yubico_id\';\n    id_map[\'yubico.secret\'] = \'sys_yubico_secret\';\n\n\treturn id_map;\n\n}\n\n/*\n * \'typ\'_get_config_params()\n *\n * this method is called, when the token config is submitted\n * - it will return a hash of parameters for system/setConfig call\n *\n */\nfunction yubico_get_config_params(){\n\tvar url_params ={};\n\n    url_params[\'yubico.id\'] \t= $(\'#sys_yubico_id\').val();\n    url_params[\'yubico.secret\'] \t= $(\'#sys_yubico_secret\').val();\n\n\treturn url_params;\n}\n\n</script>\n\n<form class="cmxform" id=\'form_config_yubico\'>\n\t<p>\n\t\t')
            # SOURCE LINE 55
            __M_writer(escape(_("You get your own API key from the yubico website ")))
            __M_writer(u'\n\t\t<a href="https://upgrade.yubico.com/getapikey/" target="yubico">upgrade.yubico.com</a>.\n\t</p>\n\t<p>\n\t\t')
            # SOURCE LINE 59
            __M_writer(escape(_("If you do not use your own API key, the privacyIDEA demo API key will be used!")))
            __M_writer(u'\n\t</p>\n\t<table>\n\t<tr>\n\t<td><label for="sys_yubico_id" title=\'')
            # SOURCE LINE 63
            __M_writer(escape(_("You need to enter a valid API id")))
            __M_writer(u"'>\n\t\t")
            # SOURCE LINE 64
            __M_writer(escape(_("Yubico ID")))
            __M_writer(u'</label></td>\n\t<td><input class="required" type="text" name="sys_yubico_id" id="sys_yubico_id"\n\t\tclass="text ui-widget-content ui-corner-all"\n\t\tvalue="get-your-own"/></td>\n\t</tr>\n\n\t<tr>\n\t<td><label for="sys_yubico_secret" title=\'')
            # SOURCE LINE 71
            __M_writer(escape(_("You need to enter a valid API key")))
            __M_writer(u"'>\n\t\t")
            # SOURCE LINE 72
            __M_writer(escape(_("Yubico API key")))
            __M_writer(u'</label></td>\n\t<td><input class="required" type="text" name="sys_yubico_secret" id="sys_yubico_secret"\n\t\tclass="text ui-widget-content ui-corner-all"\n\t\tvalue="get-your-own"/></td>\n\t</tr>\n\n\t</table>\n\n</form>\n')
        # SOURCE LINE 82
        __M_writer(u'\n\n')
        # SOURCE LINE 84
        if c.scope == 'enroll.title' :
            # SOURCE LINE 85
            __M_writer(escape(_("Yubikey")))
            __M_writer(u'\n')
        # SOURCE LINE 87
        __M_writer(u'\n')
        # SOURCE LINE 88
        if c.scope == 'enroll' :
            # SOURCE LINE 89
            __M_writer(u'<script>\n\n/*\n * \'typ\'_get_enroll_params()\n *\n * this method is called, when the token  is submitted\n * - it will return a hash of parameters for admin/init call\n *\n */\n\nfunction yubico_get_enroll_params(){\n\tvar params ={};\n\n    params[\'yubico.tokenid\'] \t\t= $(\'#yubico_token_id\').val();\n    params[\'description\'] \t\t\t= $("#yubico_enroll_desc").val();\n\n\tjQuery.extend(params, add_user_data());\n\n\treturn params;\n}\n\n</script>\n\n<p>')
            # SOURCE LINE 112
            __M_writer(escape(_("Here you need to enter the token ID of the Yubikey.")))
            __M_writer(u'</p>\n<p>')
            # SOURCE LINE 113
            __M_writer(escape(_("You can do this by inserting the Yubikey and simply push the button.")))
            __M_writer(u'</p>\n<table>\n<tr>\n\t<td><label for="yubico_token_id" title=\'')
            # SOURCE LINE 116
            __M_writer(escape(_("You need to enter the Yubikey token ID")))
            __M_writer(u"'>\n\t\t")
            # SOURCE LINE 117
            __M_writer(escape(_("Token ID")))
            __M_writer(u'</label></td>\n\t<td><input class="required" type="text" name="yubico_token_id" id="yubico_token_id" min=12\n\t\tclass="text ui-widget-content ui-corner-all"/></td>\n</tr>\n<tr>\n    <td><label for="yubico_enroll_desc" id=\'yubico_enroll_desc_label\'>')
            # SOURCE LINE 122
            __M_writer(escape(_("Description")))
            __M_writer(u'</label></td>\n    <td><input type="text" name="yubico_enroll_desc" id="yubico_enroll_desc" value="Yubico Cloud token" class="text" /></td>\n</tr>\n</table>\n\n')
        # SOURCE LINE 128
        __M_writer(u'\n\n')
        # SOURCE LINE 130
        if c.scope == 'selfservice.enroll':
            # SOURCE LINE 131
            __M_writer(u'<script>\n\nfunction self_yubico_get_param()\n{\n\tvar urlparam = {};\n\tvar typ = \'yubico\';\n\n\turlparam[\'type\'] \t= typ;\n\turlparam[\'otplen\'] \t= 44;\n\turlparam[\'description\']    = $("#yubico_self_desc").val();\n\turlparam[\'yubico.tokenid\'] = $(\'#yubico_tokenid\').val();\n\n\treturn urlparam;\n}\n\nfunction self_tokenid_clear()\n{\n\t$(\'#yubico_tokenid\').val(\'\');\n\n}\nfunction self_yubico_submit(){\n\n\tvar ret = false;\n\tvar params =  self_yubico_get_param();\n\n\tenroll_token( params );\n\tret = true;\n\treturn ret;\n}\n\n</script>\n\n<h1>')
            # SOURCE LINE 163
            __M_writer(escape(_("Enroll your Yubikey")))
            __M_writer(u'</h1>\n<div id=\'enroll_yubico_form\'>\n\t<form class="cmxform" id=\'form_enroll_yubico\'>\n\t\t<p>\n\t\t\t')
            # SOURCE LINE 167
            __M_writer(escape(_("Enter the TokenId of your Yubikey. Simply insert the Yubikey and press the button.")))
            __M_writer(u"\n\t\t</p>\n\t<fieldset>\n\t\t<table>\n\t\t<tr>\n\t\t\t<td><label for='yubico_tokenid'>")
            # SOURCE LINE 172
            __M_writer(escape(_("Yubikey TokenId")+':'))
            __M_writer(u'</label></td>\n\t\t\t<td><input id=\'yubico_tokenid\' name=\'yubico_tokenid\'\n\t\t\t\tclass="required ui-widget-content ui-corner-all" min="12" maxlength=\'44\'/></td>\n\t\t</tr>\n\t\t<tr>\n\t\t    <td><label for="yubico_self_desc" id=\'yubico_self_desc_label\'>')
            # SOURCE LINE 177
            __M_writer(escape(_("Description")))
            __M_writer(u'</label></td>\n\t\t    <td><input type="text" name="yubico_self_desc" id="yubico_self_desc" value="Yubico Cloud (self)" class="text" /></td>\n\t\t</tr>\n\n        </table>\n\t    <button class=\'action-button\' id=\'button_enroll_yubico\'\n\t    \t    onclick="self_yubico_submit();">')
            # SOURCE LINE 183
            __M_writer(escape(_("enroll yubico token")))
            __M_writer(u'</button>\n\n    </fieldset>\n    </form>\n</div>\n\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


