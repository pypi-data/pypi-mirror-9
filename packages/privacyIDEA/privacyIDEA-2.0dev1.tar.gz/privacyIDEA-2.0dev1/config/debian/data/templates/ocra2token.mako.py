# -*- coding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 9
_modified_time = 1422216484.859687
_enable_loop = True
_template_filename = '/usr/lib/python2.7/dist-packages/privacyidea/lib/tokens/ocra2token.mako'
_template_uri = '/ocra2token.mako'
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
            __M_writer(escape(_("OCRA2 settings")))
            __M_writer(u'\n')
        # SOURCE LINE 7
        __M_writer(u'\n\n')
        # SOURCE LINE 9
        if c.scope == 'config' :
            # SOURCE LINE 10
            __M_writer(u'\n<table>\n\t<tr><td><label for=ocra2_max_challenge>')
            # SOURCE LINE 12
            __M_writer(escape(_("maximum concurrent OCRA2 challenges")))
            __M_writer(u'</label></td>\n\t\t<td><input type="text" id="ocra2_max_challenge" maxlength="4" class=integer\n\t\t\ttitle=\'')
            # SOURCE LINE 14
            __M_writer(escape(_("This is the maximum concurrent challenges per OCRA2 Token.")))
            __M_writer(u"'/></td></tr>\n\t<tr><td><label for=ocra2_challenge_timeout>")
            # SOURCE LINE 15
            __M_writer(escape(_("OCRA2 challenge timeout")))
            __M_writer(u'</label></td>\n\t\t<td><input type="text" id="ocra2_challenge_timeout" maxlength="6"\n\t\t\ttitle=\'')
            # SOURCE LINE 17
            __M_writer(escape(_("After this time a challenge can not be used anymore. Valid entries are like 1D, 2H or 5M where D=day, H=hour, M=minute.")))
            __M_writer(u"'></td></tr>\n</table>\n\n")
        # SOURCE LINE 21
        __M_writer(u'\n\n')
        # SOURCE LINE 23
        if c.scope == 'enroll.title' :
            # SOURCE LINE 24
            __M_writer(escape(_("OCRA2 - challenge/response Token")))
            __M_writer(u'\n')
        # SOURCE LINE 26
        __M_writer(u'\n')
        # SOURCE LINE 27
        if c.scope == 'enroll' :
            # SOURCE LINE 28
            __M_writer(u"<script>\n\n/*\n * 'typ'_get_enroll_params()\n *\n * this method is called, when the token  is submitted\n * - it will return a hash of parameters for admin/init call\n *\n */\n\nfunction ocra2_get_enroll_params(){\n    var url = {};\n    url['type'] = 'ocra2';\n   \turl['description'] = $('#enroll_ocra2_desc').val();\n   \turl['sharedsecret'] = 1;\n\turl['ocrasuite'] = $('#ocrasuite_algorithm').val();\n\n    // If we got to generate the ocra2 key, we do it here:\n    if  ( $('#ocra2_key_cb').attr('checked') ) {\n    \turl['genkey'] = 1;\n\n    } else {\n        // OTP Key\n        url['otpkey'] = $('#ocra2_key').val();\n    }\n\n    jQuery.extend(url, add_user_data());\n\n    return url;\n}\n</script>\n<p><span id='ocra2_key_intro'>\n\t")
            # SOURCE LINE 60
            __M_writer(escape(_("Please enter or copy the OCRA2 key.")))
            __M_writer(u'</span></p>\n<table>\n<tr>\n     <td><label for="ocra2_key" id=\'ocra2_key_label\'>')
            # SOURCE LINE 63
            __M_writer(escape(_("OCRA2 key")))
            __M_writer(u'</label></td>\n     <td><input type="text" name="ocra2_key" id="ocra2_key" value="" class="text ui-widget-content ui-corner-all" /></td>\n</tr>\n<tr>\n\t<td> </td>\n\t<td><input type=\'checkbox\' id=\'ocra2_key_cb\' onclick="cb_changed(\'ocra2_key_cb\',[\'ocra2_key\',\'ocra2_key_label\',\'ocra2_key_intro\']);">\n\t    <label for=ocra2_key_cb>')
            # SOURCE LINE 69
            __M_writer(escape(_("Generate OCRA2 key.")))
            __M_writer(u'</label></td>\n</tr>\n<tr>\n\t<td><label for="ocrasuite_algorithm">')
            # SOURCE LINE 72
            __M_writer(escape(_("Ocra suite")))
            __M_writer(u'</label></td>\n\t<td><select name="algorithm" id=\'ocrasuite_algorithm\' >\n\t        <option selected value="OCRA-1:HOTP-SHA256-8:C-QN08">SHA256 - otplen 8 digits - numeric challenge 8 digits</option>\n\t        <option value="OCRA-1:HOTP-SHA256-8:C-QN08">SHA256 - otplen 8 digits - numeric challenge 8 digits</option>\n\t        <option value="OCRA-1:HOTP-SHA256-8:C-QA64">SHA256 - otplen 8 digits - numeric challenge 64 chars</option>\n    </select></td>\n</tr>\n<tr>\n    <td><label for="enroll_ocra2_desc" id=\'enroll_ocra2_desc_label\'>')
            # SOURCE LINE 80
            __M_writer(escape(_("Description")))
            __M_writer(u'</label></td>\n    <td><input type="text" name="enroll_ocra2_desc" id="enroll_ocra2_desc" value="webGUI_generated" class="text" /></td>\n</tr>\n\n</table>\n\n')
        # SOURCE LINE 87
        __M_writer(u'\n\n\n\n')
        # SOURCE LINE 91
        if c.scope == 'selfservice.title.enroll':
            # SOURCE LINE 92
            __M_writer(escape(_("Enroll your OCRA2 Token")))
            __M_writer(u'\n')
        # SOURCE LINE 94
        __M_writer(u'\n\n')
        # SOURCE LINE 96
        if c.scope == 'selfservice.enroll':
            # SOURCE LINE 97
            __M_writer(u'<script>\n\tjQuery.extend(jQuery.validator.messages, {\n\t\trequired: "')
            # SOURCE LINE 99
            __M_writer(escape(_('required input field')))
            __M_writer(u'",\n\t\tminlength: "')
            # SOURCE LINE 100
            __M_writer(escape(_('minimum length must be greater than {0}')))
            __M_writer(u'",\n\t\tmaxlength: "')
            # SOURCE LINE 101
            __M_writer(escape(_('maximum length must be lower than {0}')))
            __M_writer(u'",\n\n\t});\n\njQuery.validator.addMethod("ocra2_secret", function(value, element, param){\n\tvar res1 = value.match(/^[a-fA-F0-9]+$/i);\n\tvar res2 = !value;\n    return  res1 || res2 ;\n}, \'')
            # SOURCE LINE 109
            __M_writer(escape(_("Please enter a valid init secret. It may only contain numbers and the letters A-F.")))
            __M_writer(u"'  );\n\n$('#form_enroll_ocra2').validate({\n\tdebug: true,\n    rules: {\n        ocra2_secret: {\n            minlength: 40,\n            maxlength: 64,\n            number: false,\n            ocra2_secret: true,\n\t\t\trequired: function() {\n            \tvar res = $('#ocra2_key_cb2').attr('checked') === 'undefined';\n            return res;\n        }\n        }\n    }\n});\n\nfunction self_ocra2_get_param()\n{\n\tvar urlparam = {};\n\tvar typ = 'ocra2';\n\n    if  ( $('#ocra2_key_cb2').attr('checked') ) {\n    \turlparam['genkey'] = 1;\n    } else {\n        // OTP Key\n        urlparam['otpkey'] = $('#ocra2_secret').val();\n    }\n\n\turlparam['type'] \t= typ;\n\turlparam['description'] = $('#ocra2_desc').val();\n\turlparam['sharedsecret'] = '1';\n\treturn urlparam;\n}\n\nfunction self_ocra2_clear()\n{\n\t$('#ocra2_secret').val('');\n\n}\nfunction self_ocra2_submit(){\n\n\tvar ret = false;\n\tvar params =  self_ocra2_get_param();\n\n\tif  ( $('#ocra2_key_cb2').attr('checked') === undefined && $('#form_enroll_ocra2').valid() === false) {\n\t\talert('")
            # SOURCE LINE 156
            __M_writer(escape(_("Form data not valid.")))
            __M_writer(u'\');\n\t} else {\n\t\tenroll_token( params );\n\t\t$("#ocra2_key_cb2").prop("checked", false);\n\t\tcb_changed(\'ocra2_key_cb2\',[\'ocra2_secret\',\'ocra2_key_label2\']);\n\t\tret = true;\n\t}\n\treturn ret;\n\n};\n\nfunction self_ocra2_enroll_details(data) {\n\treturn;\n};\n\n</script>\n<h1>')
            # SOURCE LINE 172
            __M_writer(escape(_("Enroll your OCRA2 Token")))
            __M_writer(u'</h1>\n<div id=\'enroll_ocra2_form\'>\n\t<form class="cmxform" id=\'form_enroll_ocra2\'>\n\t<fieldset>\n\t\t<table><tr>\n\t\t\t<td><label id=\'ocra2_key_label2\' for=\'ocra2_secret\'>')
            # SOURCE LINE 177
            __M_writer(escape(_("Enter seed for the new OCRA2 token:")))
            __M_writer(u'</label></td>\n\t\t\t<td><input id=\'ocra2_secret\' name=\'ocra2_secret\' class="required ui-widget-content ui-corner-all" min="40" maxlength=\'64\'/></td>\n\t\t</tr><tr>\n\t\t\t<td><label for=\'ocra2_key_cb\'>')
            # SOURCE LINE 180
            __M_writer(escape(_("Generate OCRA2 seed")+':'))
            __M_writer(u'</label></td>\n\t\t\t<td><input type=\'checkbox\' name=\'ocra2_key_cb2\' id=\'ocra2_key_cb2\' onclick="cb_changed(\'ocra2_key_cb2\',[\'ocra2_secret\',\'ocra2_key_label2\']);"></td>\n\t\t</tr><tr>\n\t\t\t<td><label id=\'ocra2_desc_label2\' for=\'ocra2_desc\'>')
            # SOURCE LINE 183
            __M_writer(escape(_("Token description")))
            __M_writer(u'</label></td>\n\t\t\t<td><input id=\'ocra2_desc\' name=\'ocra2_desc\' class="ui-widget-content ui-corner-all" value=\'self enrolled\'/></td>\n\t\t</tr>\n        </table>\n\t    <button class=\'action-button\' id=\'button_enroll_ocra2\'\n\t    \t    onclick="self_ocra2_submit();">')
            # SOURCE LINE 188
            __M_writer(escape(_("enroll ocra2 token")))
            __M_writer(u'</button>\n    </fieldset>\n    </form>\n</div>\n\n')
        # SOURCE LINE 194
        __M_writer(u'<!-- -->\n\n')
        # SOURCE LINE 196
        if c.scope == 'selfservice.title.activate':
            # SOURCE LINE 197
            __M_writer(escape(_("Activate your OCRA2 Token")))
            __M_writer(u'\n')
        # SOURCE LINE 199
        __M_writer(u'\n\n')
        # SOURCE LINE 201
        if c.scope == 'selfservice.activate':
            # SOURCE LINE 202
            __M_writer(u'<h1>')
            __M_writer(escape(_("Activate your OCRA2 Token")))
            __M_writer(u'</h1>\n\n<div id=\'oathtokenform2\'>\n\t<form class="cmxform" name=\'myForm\'>\n\t\t<table>\n\t\t<p id=oath_info>\n\t\t<tr><td>')
            # SOURCE LINE 208
            __M_writer(escape(_("Your OCRA2 Token :")))
            __M_writer(u'      </td>\n\t\t    <td> <input type=\'text\' class=\'selectedToken\' class="text ui-widget-content ui-corner-all" disabled\n\t\t    \tvalue=\'\' id=\'serial2\' onchange="resetOcraForm()"/></td></tr>\n\t\t<tr><td><label for=activationcode2>')
            # SOURCE LINE 211
            __M_writer(escape(_("1. Enter the activation code :")))
            __M_writer(u'</label> </td>\n\t\t    <td><input type=\'text\' class="text ui-widget-content ui-corner-all" value=\'\' id=\'activationcode2\'/></td>\n\t\t        <input type=\'hidden\' value=\'')
            # SOURCE LINE 213
            __M_writer(escape(_("Failed to enroll token!")))
            __M_writer(u'\' id=\'ocra2_activate_fail\'/>\n\t\t    <td><div id=\'qr2_activate\'>\n\t\t\t    <button class=\'action-button\' id=\'button_provisionOcra2\' onclick="provisionOcra2(); return false;">\n\t\t\t\t')
            # SOURCE LINE 216
            __M_writer(escape(_("activate your OCRA2 Token")))
            __M_writer(u'\n\t\t\t\t</button>\n\t\t\t\t</div>\n\t\t\t</td>\n\t\t\t</tr>\n\t\t<tr><td><div id=\'ocra2_qr_code\'></div></td></tr>\n\t\t</table>\n\t</form>\n\t<form class="cmxform" name=\'myForm2\'>\n\t\t<table>\n\t\t<tr><td><div id=\'qr2_confirm1\'><label for=ocra2_check>')
            # SOURCE LINE 226
            __M_writer(escape(_("2. Enter your confirmation code:")))
            __M_writer(u'\n\t\t\t\t</label></div> </td>\n\t\t    <td><div id=\'qr2_confirm2\'>\n\t\t        <input type=\'hidden\' class="text ui-widget-content ui-corner-all" id=\'transactionid2\' value=\'\' />\n\t\t        <input type=\'hidden\' value=\'')
            # SOURCE LINE 230
            __M_writer(escape(_("OCRA rollout for token %s completed!")))
            __M_writer(u"' \t\t\tid='ocra2_finish_ok'  />\n\t\t        <input type='hidden' value='")
            # SOURCE LINE 231
            __M_writer(escape(_("OCRA token rollout failed! Please retry")))
            __M_writer(u'\' \t\tid=\'ocra2_finish_fail\'/>\n\t\t    \t<input type=\'text\' class="text ui-widget-content ui-corner-all"              \t\tid=\'ocra2_check\' value=\'\' />\n\t\t    \t</div>\n\t\t    </td>\n\t\t\t<td>\n\t\t\t\t<div id=\'qr2_finish\' >\n\t\t\t    <button class=\'action-button\' id=\'button_finishOcra2\' onclick="finishOcra2(); return false;">\n\t\t\t\t')
            # SOURCE LINE 238
            __M_writer(escape(_("finish your OCRA2 Token")))
            __M_writer(u'\n\t\t\t\t</button>\n\t\t\t\t</div>\n\t\t\t</td>\n\t\t\t</tr>\n\t\t</div>\n\t\t<tr><td><div id=\'qr2_completed\'></div></td></tr>\n\t\t</table>\n\t</form>\n</div>\n\n\n<script>\n\n\nfunction provisionOcra2() {\n\tshow_waiting();\n\tvar acode = $(\'#activationcode2\').val();\n\tvar serial = $(\'#serial2\').val();\n\tvar activation_fail = $(\'#ocra2_activate_fail\').val();\n\tvar genkey = 1;\n\n\tvar params = {\n\t\t\'type\' : \'ocra2\',\n\t\t\'serial\' : serial,\n\t\t\'genkey\' : 1,\n\t\t\'activationcode\' : acode,\n\t\t\'session\' : get_selfservice_session()\n\t};\n\n\t$.post("/selfservice/useractivateocratoken", params, function(data, textStatus, XMLHttpRequest) {\n\t\thide_waiting();\n\n\t\tif (data.result.status == true) {\n\t\t\tif (data.result.value.activate == true) {\n\t\t\t\t// The token was successfully initialized and we will display the url\n\t\t\t\tshowTokenlist();\n\t\t\t\t// console_log(data.result.value)\n\t\t\t\tvar img = data.result.value.ocratoken.img;\n\t\t\t\tvar url = data.result.value.ocratoken.url;\n\t\t\t\tvar trans = data.result.value.ocratoken.transaction;\n\t\t\t\t$(\'#ocra2_link\').attr("href", url);\n\t\t\t\t$(\'#ocra2_qr_code\').html(img);\n\t\t\t\t$(\'#qr2_activate\').hide();\n\t\t\t\t//$(\'#activationcode\').attr("disabled","disabled");\n\t\t\t\t$(\'#transactionid2\').attr("value", trans);\n\t\t\t\t$(\'#qr2_finish\').show();\n\t\t\t\t$(\'#qr2_confirm1\').show();\n\t\t\t\t$(\'#qr2_confirm2\').show();\n\t\t\t}\n\t\t} else {\n\t\t\talert(activation_fail + " \\n" + data.result.error.message);\n\t\t}\n\t});\n}\n\n\nfunction finishOcra2() {\n\tshow_waiting();\n\tvar trans = $(\'#transactionid2\').val();\n\tvar serial = $(\'#serial2\').val();\n\tvar ocra_check = $(\'#ocra2_check\').val();\n\tvar ocra_finish_ok = $(\'#ocra2_finish_ok\').val();\n\tvar ocra_finish_fail = $(\'#ocra2_finish_fail\').val();\n\n\t$.post("/selfservice/userfinshocra2token", {\n\t\t\'type\' : \'ocra2\',\n\t\t\'serial\' : serial,\n\t\t\'transactionid\' : trans,\n\t\t\'pass\' : ocra_check,\n\t\t\'from\' : \'finishOcra2\',\n\t\t\'session\' : get_selfservice_session()\n\t}, function(data, textStatus, XMLHttpRequest) {\n\t\thide_waiting();\n\n\t\t//console_log(data.result)\n\n\t\tif (data.result.status == true) {\n\t\t\t// The token was successfully initialized and we will display the url\n\t\t\t// if not (false) display an ocra_finish_fail message for retry\n\t\t\tshowTokenlist();\n\t\t\tif (data.result.value.result == false) {\n\t\t\t\talert(ocra_finish_fail);\n\t\t\t} else {\n\t\t\t\talert(String.sprintf(ocra_finish_ok, serial));\n\t\t\t\t$(\'#qr2_completed\').show();\n\t\t\t\t$(\'#qr2_finish\').hide();\n\t\t\t\t//$(\'#ocra_check\').attr("disabled","disabled");\n\t\t\t\t$(\'#ocra2_qr_code\').html(\'<div/>\');\n\t\t\t\t$(\'#qr2_completed\').html(String.sprintf(ocra_finish_ok, serial));\n\t\t\t}\n\t\t} else {\n\t\t\talert("Failed to enroll token!\\n" + data.result.error.message);\n\t\t}\n\t});\n\n}\n\n\n\n\t$(\'#qr2_finish\').hide();\n\t$(\'#qr2_completed\').hide();\n\t$(\'#qr2_confirm1\').hide();\n\t$(\'#qr2_confirm2\').hide();\n\t$(\'#ocra2_check\').removeAttr("disabled");\n\t$(\'#activationcode2\').removeAttr("disabled");\n</script>\n\n\n\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


