# -*- coding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 9
_modified_time = 1422216484.887167
_enable_loop = True
_template_filename = '/usr/lib/python2.7/dist-packages/privacyidea/lib/tokens/emailtoken.mako'
_template_uri = '/emailtoken.mako'
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
        if c.scope == 'config.title' :
            # SOURCE LINE 4
            __M_writer(escape(_("E-mail OTP token")))
            __M_writer(u'\n')
        # SOURCE LINE 6
        __M_writer(u'\n\n')
        # SOURCE LINE 8
        if c.scope == 'config' :
            # SOURCE LINE 9
            __M_writer(u'<!-- #################### E-mail provider ################### -->\n<script>\n/*\n * \'typ\'_get_config_val()\n *\n * this method is called, when the token config dialog is opened\n * - it contains the mapping of config entries to the form id\n * - according to the Config entries, the form entries will be filled\n *\n */\nfunction email_get_config_val(){\n\tvar ret = {};\n\tret[\'EmailProvider\'] = \'c_email_provider\';\n\tret[\'EmailProviderConfig\'] = \'c_email_provider_config\';\n\tret[\'EmailChallengeValidityTime\'] = \'c_email_challenge_validity\';\n\tret[\'EmailBlockingTimeout\'] = \'c_email_blocking\';\n\treturn ret;\n}\n/*\n * \'typ\'_get_config_params()\n *\n * this method is called, when the token config is submitted\n * - it will return a hash of parameters for system/setConfig call\n *\n */\nfunction email_get_config_params(){\n\tvar ret = {};\n\tret[\'EmailProvider\'] = $(\'#c_email_provider\').val();\n\tret[\'EmailProviderConfig\'] = $(\'#c_email_provider_config\').val();\n\tret[\'EmailProviderConfig.type\'] = \'password\';\n\tret[\'EmailChallengeValidityTime\'] = $(\'#c_email_challenge_validity\').val();\n\tret[\'EmailBlockingTimeout\'] = $(\'#c_email_blocking\').val();\n\treturn ret;\n}\n\n$(document).ready(function () {\n    $("#form_emailconfig").validate();\n});\n</script>\n\n<form class="cmxform" id="form_emailconfig">\n<fieldset>\n    <legend>')
            # SOURCE LINE 51
            __M_writer(escape(_("E-mail provider config")))
            __M_writer(u'</legend>\n    <table>\n        <tr>\n\t        <td><label for="c_email_provider">')
            # SOURCE LINE 54
            __M_writer(escape(_("E-mail provider")))
            __M_writer(u'</label>: </td>\n\t        <td><input type="text" name="email_provider" class="required"  id="c_email_provider" size="37" maxlength="80"></td>\n        </tr>\n        <tr>\n\t        <td><label for="c_email_provider_config">')
            # SOURCE LINE 58
            __M_writer(escape(_("E-mail provider config")))
            __M_writer(u'</label>: </td>\n\t        <td><textarea name="email_provider_config" class="required"  id="c_email_provider_config" cols=\'35\' rows=\'6\' maxlength="400">{}\t        \t\n\t        </textarea></td>\n        </tr>\n        <tr>\n\t        <td><label for="c_email_challenge_validity">')
            # SOURCE LINE 63
            __M_writer(escape(_("E-mail challenge validity (sec)")))
            __M_writer(u'</label>: </td>\n\t        <td><input type="text" name="email_challenge_validity" class="required"  id="c_email_challenge_validity" size="5" maxlength="5"></td>\n        </tr>\n        <tr>\n\t        <td><label for="c_email_blocking">')
            # SOURCE LINE 67
            __M_writer(escape(_("Time between e-mails (sec)")))
            __M_writer(u'</label>: </td>\n\t        <td><input type="text" name="email_blocking" class="required"  id="c_email_blocking" size="5" maxlength="5" value"30"></td>\n\t    </tr>\n    </table>\n</fieldset>\n</form>\n\n')
        # SOURCE LINE 75
        __M_writer(u'\n')
        # SOURCE LINE 76
        if c.scope == 'enroll.title' :
            # SOURCE LINE 77
            __M_writer(escape(_("E-mail token")))
            __M_writer(u'\n')
        # SOURCE LINE 79
        __M_writer(u'\n')
        # SOURCE LINE 80
        if c.scope == 'enroll' :
            # SOURCE LINE 81
            __M_writer(u'<script>\nfunction email_enroll_setup_defaults(config){\n\t// in case we enroll e-mail otp, we get the e-mail address of the user\n\temail_addresses = get_selected_email();\n\t$(\'#email_address\').val($.trim(email_addresses[0]));\n}\n\n/*\n * \'typ\'_get_enroll_params()\n *\n * this method is called, when the token  is submitted\n * - it will return a hash of parameters for admin/init call\n *\n */\nfunction email_get_enroll_params(){\n    var params = {};\n    // phone number\n    params[\'email_address\']\t= $(\'#email_address\').val();\n    params[\'description\'] = $(\'#email_address\').val() + " " + $(\'#enroll_email_desc\').val();\n    jQuery.extend(params, add_user_data());\n    return params;\n}\n</script>\n\n<table><tr>\n\t<td><label for="email_address">')
            # SOURCE LINE 106
            __M_writer(escape(_("E-mail address")))
            __M_writer(u'</label></td>\n\t<td><input type="text" name="email_address" id="email_address" value="" class="text ui-widget-content ui-corner-all"></td>\n</tr><tr>\n    <td><label for="enroll_email_desc" id=\'enroll_email_desc_label\'>')
            # SOURCE LINE 109
            __M_writer(escape(_("Description")))
            __M_writer(u'</label></td>\n    <td><input type="text" name="enroll_email_desc" id="enroll_email_desc" value="webGUI_generated" class="text" /></td>\n</tr>\n</table>\n\n')
        # SOURCE LINE 115
        __M_writer(u'\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


