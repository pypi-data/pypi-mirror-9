# -*- coding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 9
_modified_time = 1422216484.916012
_enable_loop = True
_template_filename = '/usr/lib/python2.7/dist-packages/privacyidea/lib/tokens/hmactoken.mako'
_template_uri = '/hmactoken.mako'
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
            __M_writer(escape(_("HMAC Token Settings")))
            __M_writer(u'\n')
        # SOURCE LINE 7
        __M_writer(u'\n\n')
        # SOURCE LINE 9
        if c.scope == 'config' :
            pass
        # SOURCE LINE 11
        __M_writer(u'\n\n')
        # SOURCE LINE 13
        if c.scope == 'enroll.title' :
            # SOURCE LINE 14
            __M_writer(escape(_("HMAC eventbased")))
            __M_writer(u'\n')
        # SOURCE LINE 16
        __M_writer(u'\n')
        # SOURCE LINE 17
        if c.scope == 'enroll' :
            # SOURCE LINE 18
            __M_writer(u"<script>\n\n/*\n * 'typ'_get_enroll_params()\n *\n * this method is called, when the token  is submitted\n * - it will return a hash of parameters for admin/init call\n *\n */\n\nfunction hmac_get_enroll_params(){\n    var url = {};\n    url['type'] = 'hmac';\n   \turl['description'] = $('#enroll_hmac_desc').val();\n\n    // If we have got to generate the hmac key, we do it here:\n    if  ( $('#hmac_key_cb').attr('checked') ) {\n    \turl['genkey'] = 1;\n\n    } else {\n        // OTP Key\n        url['otpkey'] = $('#hmac_key').val();\n    }\n\n    jQuery.extend(url, add_user_data());\n\n    url['hashlib']\t= $('#hmac_algorithm').val();\n\turl['otplen']\t= $('#hmac_otplen').val();\n\n\n    return url;\n}\n</script>\n\n<p><span id='hmac_key_intro'>\n\t")
            # SOURCE LINE 53
            __M_writer(escape(_("Please enter or copy the HMAC key.")))
            __M_writer(u'</span></p>\n<table><tr>\n\t<td><label for="hmac_key" id=\'hmac_key_label\'>')
            # SOURCE LINE 55
            __M_writer(escape(_("HMAC key")))
            __M_writer(u'</label></td>\n\t<td><input type="text" name="hmac_key" id="hmac_key" value="" class="text ui-widget-content ui-corner-all" /></td>\n</tr><tr>\n\t<td> </td><td><input type=\'checkbox\' id=\'hmac_key_cb\' onclick="cb_changed(\'hmac_key_cb\',[\'hmac_key\',\'hmac_key_label\',\'hmac_key_intro\']);">\n\t<label for=hmac_key_cb>')
            # SOURCE LINE 59
            __M_writer(escape(_("Generate HMAC key.")))
            __M_writer(u'</label></td>\n</tr><tr>\n\t<td><label for="hmac_otplen">')
            # SOURCE LINE 61
            __M_writer(escape(_("OTP Length")))
            __M_writer(u'</label></td>\n\t<td><select name="pintype" id="hmac_otplen">\n\t\t\t<option  value="4">4</option>\n\t\t\t<option  selected value="6">6</option>\n\t\t\t<option  value="8">8</option>\n\t\t\t<option  value="10">10</option>\n\t\t\t<option  value="12">12</option>\n\t</select></td>\n\n</tr><tr>\n\t<td><label for="hmac_algorithm">')
            # SOURCE LINE 71
            __M_writer(escape(_("Hash algorithm")))
            __M_writer(u'</label></td>\n\t<td><select name="algorithm" id=\'hmac_algorithm\' >\n\t        <option selected value="sha1">sha1</option>\n\t        <option value="sha256">sha256</option>\n\t        <option value="sha512">sha512</option>\n    </select></td>\n</tr>\n<tr>\n    <td><label for="enroll_hmac_desc" id=\'enroll_hmac_desc_label\'>')
            # SOURCE LINE 79
            __M_writer(escape(_("Description")))
            __M_writer(u'</label></td>\n    <td><input type="text" name="enroll_hmac_desc" id="enroll_hmac_desc" value="webGUI_generated" class="text" /></td>\n</tr>\n\n</table>\n\n')
        # SOURCE LINE 86
        __M_writer(u'\n\n\n\n')
        # SOURCE LINE 90
        if c.scope == 'selfservice.title.enroll':
            # SOURCE LINE 91
            __M_writer(escape(_("Enroll your HOTP Token")))
            __M_writer(u'\n')
        # SOURCE LINE 93
        __M_writer(u'\n\n')
        # SOURCE LINE 95
        if c.scope == 'selfservice.enroll':
            # SOURCE LINE 96
            __M_writer(u'<script>\n\tjQuery.extend(jQuery.validator.messages, {\n\t\trequired: "')
            # SOURCE LINE 98
            __M_writer(escape(_('required input field')))
            __M_writer(u'",\n\t\tminlength: "')
            # SOURCE LINE 99
            __M_writer(escape(_('minimum length must be greater than {0}')))
            __M_writer(u'",\n\t\tmaxlength: "')
            # SOURCE LINE 100
            __M_writer(escape(_('maximum length must be lower than {0}')))
            __M_writer(u'",\n\n\t});\n\njQuery.validator.addMethod("hmac_secret", function(value, element, param){\n\tvar res1 = value.match(/^[a-fA-F0-9]+$/i);\n\tvar res2 = !value;\n    return  res1 || res2 ;\n}, \'')
            # SOURCE LINE 108
            __M_writer(escape(_("Please enter a valid init secret. It may only contain numbers and the letters A-F.")))
            __M_writer(u'\'  );\n\n$(\'#form_enroll_hmac\').validate({\n\tdebug: true,\n    rules: {\n        hmac_secret: {\n            minlength: 40,\n            maxlength: 64,\n            number: false,\n            hmac_secret: true,\n\t\t\trequired: function() {\n            \tvar res = $(\'#hmac_key_cb2\').attr(\'checked\') === \'undefined\';\n            return res;\n        }\n        }\n    }\n});\n\nfunction self_hmac_get_param()\n{\n\tvar urlparam = {};\n\tvar typ = \'hmac\';\n\n    if  ( $(\'#hmac_key_cb2\').attr(\'checked\') ) {\n    \turlparam[\'genkey\'] = 1;\n    } else {\n        // OTP Key\n        urlparam[\'otpkey\'] = $(\'#hmac_secret\').val();\n    }\n\n\turlparam[\'type\'] \t= typ;\n\turlparam[\'hashlib\'] = $(\'#hmac_hashlib\').val();\n\turlparam[\'otplen\'] \t= 6;\n\turlparam[\'description\'] = $("#hmac_self_desc").val();\n\n\treturn urlparam;\n}\n\nfunction self_hmac_clear()\n{\n\t$(\'#hmac_secret\').val(\'\');\n\n}\nfunction self_hmac_submit(){\n\n\tvar ret = false;\n\tvar params =  self_hmac_get_param();\n\n\tif  ( $(\'#hmac_key_cb2\').attr(\'checked\') === undefined && $(\'#form_enroll_hmac\').valid() === false) {\n\t\talert(\'')
            # SOURCE LINE 157
            __M_writer(escape(_("Form data not valid.")))
            __M_writer(u'\');\n\t} else {\n\t\tenroll_token( params );\n\t\t$("#hmac_key_cb2").prop("checked", false);\n\t\tcb_changed(\'hmac_key_cb2\',[\'hmac_secret\',\'hmac_key_label2\']);\n\t\tret = true;\n\t}\n\treturn ret;\n\n}\n</script>\n<h1>')
            # SOURCE LINE 168
            __M_writer(escape(_("Enroll your HOTP Token")))
            __M_writer(u'</h1>\n<div id=\'enroll_hmac_form\'>\n\t<form class="cmxform" id=\'form_enroll_hmac\'>\n\t<fieldset>\n\t\t<table><tr>\n\t\t\t<td><label for=\'hmac_key_cb\' id=\'hmac_key_label2\'>')
            # SOURCE LINE 173
            __M_writer(escape(_("Generate HMAC key")+':'))
            __M_writer(u'</label></td>\n\t\t\t<td><input type=\'checkbox\' name=\'hmac_key_cb2\' id=\'hmac_key_cb2\' onclick="cb_changed(\'hmac_key_cb2\',[\'hmac_secret\',\'hmac_key_label2\']);"></td>\n\t\t</tr><tr>\n\t\t\t<td><label id=\'hmac_key_label2\' for=\'hmac_secret\'>')
            # SOURCE LINE 176
            __M_writer(escape(_("Seed for HOTP token")))
            __M_writer(u'</label></td>\n\t\t\t<td><input id=\'hmac_secret\' name=\'hmac_secret\' class="required ui-widget-content ui-corner-all" min="40" maxlength=\'64\'/></td>\n\t\t</tr>\n')
            # SOURCE LINE 179
            if c.hmac_hashlib == 1:
                # SOURCE LINE 180
                __M_writer(u"\t\t\t<input type=hidden id='hmac_hashlib' name='hmac_hashlib' value='sha1'>\n")
            # SOURCE LINE 182
            if c.hmac_hashlib == 2:
                # SOURCE LINE 183
                __M_writer(u"\t\t\t<input type=hidden id='hmac_hashlib' name='hmac_hashlib' value='sha256'>\n")
            # SOURCE LINE 185
            if c.hmac_hashlib == -1:
                # SOURCE LINE 186
                __M_writer(u"\t\t<tr>\n\t\t<td><label for='hmac_hashlib'>")
                # SOURCE LINE 187
                __M_writer(escape(_("hashlib")))
                __M_writer(u"</label></td>\n\t\t<td><select id='hmac_hashlib' name='hmac_hashlib'>\n\t\t\t<option value='sha1' selected>sha1</option>\n\t\t\t<option value='sha256'>sha256</option>\n\t\t\t</select></td>\n\t\t</tr>\n")
            # SOURCE LINE 194
            __M_writer(u'\t\t<tr>\n\t\t    <td><label for="hmac_self_desc" id=\'hmac_self_desc_label\'>')
            # SOURCE LINE 195
            __M_writer(escape(_("Description")))
            __M_writer(u'</label></td>\n\t\t    <td><input type="text" name="hmac_self_desc" id="hmac_self_desc" value="self enrolled" class="text" /></td>\n\t\t</tr>\n\n        </table>\n\t    <button class=\'action-button\' id=\'button_enroll_hmac\'\n\t    \t    onclick="self_hmac_submit();">')
            # SOURCE LINE 201
            __M_writer(escape(_("enroll hmac token")))
            __M_writer(u'</button>\n\n    </fieldset>\n    </form>\n</div>\n\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


