# -*- coding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 9
_modified_time = 1422216484.89673
_enable_loop = True
_template_filename = '/usr/lib/python2.7/dist-packages/privacyidea/lib/tokens/totptoken.mako'
_template_uri = '/totptoken.mako'
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
            __M_writer(escape(_("TOTP Token Settings")))
            __M_writer(u'\n')
        # SOURCE LINE 7
        __M_writer(u'\n\n')
        # SOURCE LINE 9
        if c.scope == 'config' :
            # SOURCE LINE 10
            __M_writer(u"<script>\n\n/*\n * 'typ'_get_config_val()\n *\n * this method is called, when the token config dialog is opened\n * - it contains the mapping of config entries to the form id\n * - according to the Config entries, the form entries will be filled\n *\n */\n\n\nfunction totp_get_config_val(){\n\tvar id_map = {};\n\n    id_map['totp.timeStep']   = 'totp_timeStep';\n    id_map['totp.timeShift']  = 'totp_timeShift';\n    id_map['totp.timeWindow'] = 'totp_timeWindow';\n\n\treturn id_map;\n\n}\n\n/*\n * 'typ'_get_config_params()\n *\n * this method is called, when the token config is submitted\n * - it will return a hash of parameters for system/setConfig call\n *\n */\nfunction totp_get_config_params(){\n\n\tvar url_params ={};\n\n    url_params['totp.timeShift'] \t= $('#totp_timeShift').val();\n    url_params['totp.timeStep'] \t= $('#totp_timeStep').val();\n    url_params['totp.timeWindow'] \t= $('#totp_timeWindow').val();\n\n\treturn url_params;\n}\n\n</script>\n\n<fieldset>\n\t<legend>")
            # SOURCE LINE 54
            __M_writer(escape(_("TOTP settings")))
            __M_writer(u"</legend>\n\t<table>\n\t\t<tr><td><label for='totp_timeStep'> ")
            # SOURCE LINE 56
            __M_writer(escape(_("TOTP time Step")))
            __M_writer(u': </label></td>\n\t\t<td><input type="text" name="tot_timeStep" class="required"  id="totp_timeStep" size="2" maxlength="2"\n\t\t\ttitle=\'')
            # SOURCE LINE 58
            __M_writer(escape(_("This is the time step for time based tokens. Usually this is 30 or 60.")))
            __M_writer(u"'> sec</td></tr>\n\t\t<tr><td><label for='totp_timeShift'> ")
            # SOURCE LINE 59
            __M_writer(escape(_("TOTP time Shift")))
            __M_writer(u': </label></td>\n\t\t<td><input type="text" name="totp_timeShift" class="required"  id="totp_timeShift" size="5" maxlength="5"\n\t\t\ttitle=\'')
            # SOURCE LINE 61
            __M_writer(escape(_("This is the default time shift of the server. This should be 0.")))
            __M_writer(u"'> sec</td></tr>\n\t\t<tr><td><label for='totp_timeWindow'> ")
            # SOURCE LINE 62
            __M_writer(escape(_("TOTP time window")))
            __M_writer(u': </label></td>\n\t\t<td><input type="text" name="totp_timeWindow" class="required"  id="totp_timeWindow" size="5" maxlength="5"\n\t\t\ttitle=\'')
            # SOURCE LINE 64
            __M_writer(escape(_("This is the time privacyIDEA will calculate before and after the current time. A reasonable value is 300.")))
            __M_writer(u"'> sec</td></tr>\n\t</table>\n</fieldset>\n\n")
        # SOURCE LINE 69
        __M_writer(u'\n\n')
        # SOURCE LINE 71
        if c.scope == 'enroll.title' :
            # SOURCE LINE 72
            __M_writer(escape(_("HMAC time based")))
            __M_writer(u'\n')
        # SOURCE LINE 74
        __M_writer(u'\n')
        # SOURCE LINE 75
        if c.scope == 'enroll' :
            # SOURCE LINE 76
            __M_writer(u'<script>\n\n/*\n * \'typ\'_enroll_setup_defaults()\n *\n * this method is called when the gui becomes visible,\n * and gets the privacyidea config as a parameter, so that the\n * gui could be prepared with the server defaults\n *\n *\n */\nfunction totp_enroll_setup_defaults(config){\n\tfor (var key in config) {\n\t\tif (key == "totp.timeStep")\n\t\t{\n\t\t\t$totp_timeStep = config["totp.timeStep"];\n\t\t\t$(\'#totp_timestep\').val($totp_timeStep);\n\t\t}\n\t}\n\t$(\'#totp_key\').val(\'\');\n}\n/*\n * \'typ\'_get_enroll_params()\n *\n * this method is called, when the token  is submitted\n * - it will return a hash of parameters for admin/init call\n *\n */\nfunction totp_get_enroll_params(){\n    var params = {};\n    params[\'type\'] = \'totp\';\n   \tparams[\'description\'] = $(\'#enroll_totp_desc\').val();\n\n    if  ( $(\'#totp_key_cb\').attr(\'checked\') ) {\n\t\tparams[\'genkey\']\t= 1;\n\t\tparams[\'hashlib\']\t= \'sha1\';\n\t\tparams[\'otplen\']\t= 6;\n    } else {\n        // OTP Key\n    \tparams[\'otpkey\'] \t= $(\'#totp_key\').val();\n    }\n    params[\'timeStep\'] \t= $(\'#totp_timestep\').val();\n\n\tjQuery.extend(params, add_user_data());\n\n    return params;\n}\n</script>\n<p>')
            # SOURCE LINE 124
            __M_writer(escape(_("Please enter or copy the HMAC key.")))
            __M_writer(u'</p>\n<table><tr>\n<td><label for="totp_key" id=\'totp_key_label\'>')
            # SOURCE LINE 126
            __M_writer(escape(_("HMAC key")))
            __M_writer(u'</label></td>\n<td><input type="text" name="totp_key" id="totp_key" value="" class="text ui-widget-content ui-corner-all" /></td>\n</tr>\n<tr><td> </td><td><input type=\'checkbox\' id=\'totp_key_cb\' onclick="cb_changed(\'totp_key_cb\',[\'totp_key\',\'totp_key_label\',\'totp_key_intro\']);">\n<label for=totp_key_cb>')
            # SOURCE LINE 130
            __M_writer(escape(_("Generate HMAC key.")))
            __M_writer(u"</label></td>\n</tr>\n\n<tr>\n<td><label for='totp_timestep'>")
            # SOURCE LINE 134
            __M_writer(escape(_("timeStep")))
            __M_writer(u"</label></td>\n<td>\n\t<select id='totp_timestep'>\n\t<option value='60' >60 ")
            # SOURCE LINE 137
            __M_writer(escape(_("seconds")))
            __M_writer(u"</option>\n\t<option value='30' >30 ")
            # SOURCE LINE 138
            __M_writer(escape(_("seconds")))
            __M_writer(u'</option>\n\t</select></td>\n</tr>\n<tr>\n    <td><label for="enroll_totp_desc" id=\'enroll_totp_desc_label\'>')
            # SOURCE LINE 142
            __M_writer(escape(_("Description")))
            __M_writer(u'</label></td>\n    <td><input type="text" name="enroll_totp_desc" id="enroll_totp_desc" value="webGUI_generated" class="text" /></td>\n</tr>\n</table>\n\n')
        # SOURCE LINE 148
        __M_writer(u'\n\n')
        # SOURCE LINE 150
        if c.scope == 'selfservice.title.enroll':
            # SOURCE LINE 151
            __M_writer(escape(_("Register totp")))
            __M_writer(u'\n')
        # SOURCE LINE 153
        __M_writer(u'\n\n')
        # SOURCE LINE 155
        if c.scope == 'selfservice.enroll':
            # SOURCE LINE 156
            __M_writer(u'<script>\n\tjQuery.extend(jQuery.validator.messages, {\n\t\trequired:  "')
            # SOURCE LINE 158
            __M_writer(escape(_('required input field')))
            __M_writer(u'",\n\t\tminlength: "')
            # SOURCE LINE 159
            __M_writer(escape(_('minimum length must be greater than {0}')))
            __M_writer(u'",\n\t\tmaxlength: "')
            # SOURCE LINE 160
            __M_writer(escape(_('maximum length must be lower than {0}')))
            __M_writer(u'",\n\t\trange: \'')
            # SOURCE LINE 161
            __M_writer(escape(_("Please enter a valid init secret. It may only contain numbers and the letters A-F.")))
            __M_writer(u'\',\n\t});\n\njQuery.validator.addMethod("totp_secret", function(value, element, param){\n\tvar res1 = value.match(/^[a-fA-F0-9]+$/i);\n\tvar res2 = !value;\n    return  res1 || res2 ;\n}, \'')
            # SOURCE LINE 168
            __M_writer(escape(_("Please enter a valid init secret. It may only contain numbers and the letters A-F.")))
            __M_writer(u'\' );\n\n$(\'#form_enroll_totp\').validate({\n\tdebug: true,\n    rules: {\n        totp_secret: {\n            minlength: 40,\n            maxlength: 64,\n            number: false,\n            totp_secret: true,\n\t\t\trequired: function() {\n            \tvar res = $(\'#totp_key_cb2\').attr(\'checked\') === \'undefined\';\n            return res;\n        }\n        }\n    }\n});\n\nfunction self_totp_get_param()\n{\n\tvar urlparam = {};\n\tvar typ = \'totp\';\n\n    if  ( $(\'#totp_key_cb2\').attr(\'checked\') ) {\n    \turlparam[\'genkey\'] = 1;\n    } else {\n        // OTP Key\n        urlparam[\'otpkey\'] = $(\'#totp_secret\').val();\n    }\n\n\turlparam[\'type\'] \t= typ;\n\turlparam[\'hashlib\'] = $(\'#totp_hashlib\').val();\n\turlparam[\'otplen\'] \t= 6;\n\turlparam[\'timestep\'] \t= $(\'#totp_timestep\').val();\n\turlparam[\'description\'] = $("#totp_self_desc").val();\n\n\treturn urlparam;\n}\n\nfunction self_totp_clear()\n{\n\t$(\'#totp_secret\').val(\'\');\n\n}\nfunction self_totp_submit(){\n\n\tvar ret = false;\n\tvar params =  self_totp_get_param();\n\n\tif  ( $(\'#totp_key_cb2\').attr(\'checked\') === undefined && $(\'#form_enroll_totp\').valid() === false) {\n\t\talert(\'')
            # SOURCE LINE 218
            __M_writer(escape(_("Form data not valid.")))
            __M_writer(u'\');\n\t} else {\n\t\tenroll_token( params );\n\t\t$("#totp_key_cb2").prop("checked", false);\n\t\tcb_changed(\'totp_key_cb2\',[\'totp_secret\',\'totp_key_label2\']);\n\t\tret = true;\n\t}\n\treturn ret;\n\n}\n</script>\n<h1>')
            # SOURCE LINE 229
            __M_writer(escape(_("Enroll your TOTP Token")))
            __M_writer(u'</h1>\n<div id=\'enroll_totp_form\'>\n\t<form class="cmxform" id=\'form_enroll_totp\'>\n\t<fieldset>\n\t\t<table><tr>\n\t\t\t<td><label for=\'totp_key_cb\'>')
            # SOURCE LINE 234
            __M_writer(escape(_("Generate HMAC key")))
            __M_writer(u'</label></td>\n\t\t\t<td><input type=\'checkbox\' name=\'totp_key_cb2\' id=\'totp_key_cb2\' onclick="cb_changed(\'totp_key_cb2\',[\'totp_secret\',\'totp_key_label2\']);"></td>\n\t\t</tr><tr>\n\t\t\t<td><label id=\'totp_key_label2\' for=\'totp_secret\'>')
            # SOURCE LINE 237
            __M_writer(escape(_("Seed for HOTP token")))
            __M_writer(u'</label></td>\n\t\t\t<td><input id=\'totp_secret\' name=\'totp_secret\' class="required ui-widget-content ui-corner-all" min="40" maxlength=\'64\'/></td>\n\t\t</tr>\n')
            # SOURCE LINE 240
            if c.totp_hashlib == 1:
                # SOURCE LINE 241
                __M_writer(u"\t\t\t<input type=hidden id='totp_hashlib' value='sha1'>\n")
            # SOURCE LINE 243
            if c.totp_hashlib == 2:
                # SOURCE LINE 244
                __M_writer(u"\t\t\t<input type=hidden id='totp_hashlib' value='sha256'>\n")
            # SOURCE LINE 246
            if c.totp_hashlib == -1:
                # SOURCE LINE 247
                __M_writer(u"\t\t<tr>\n\t\t<td><label for='totp_hashlib'>")
                # SOURCE LINE 248
                __M_writer(escape(_("hashlib")))
                __M_writer(u"</label></td>\n\t\t<td><select id='totp_hashlib'>\n\t\t\t<option value='sha1' selected>sha1</option>\n\t\t\t<option value='sha256'>sha256</option>\n\t\t\t</select></td>\n\t\t</tr>\n")
            # SOURCE LINE 255
            __M_writer(u'\n')
            # SOURCE LINE 256
            if c.totp_timestep == -1:
                # SOURCE LINE 257
                __M_writer(u"\t\t\t<tr>\n\t\t\t<td><label for='totp_timestep'>")
                # SOURCE LINE 258
                __M_writer(escape(_("timeStep")))
                __M_writer(u"</label></td>\n\t\t\t<td><select id='totp_timestep'>\n\t\t\t\t<option value='30' selected>30 ")
                # SOURCE LINE 260
                __M_writer(escape(_("seconds")))
                __M_writer(u"</option>\n\t\t\t\t<option value='60'>60 ")
                # SOURCE LINE 261
                __M_writer(escape(_("seconds")))
                __M_writer(u'</option>\n\t\t\t\t</select></td>\n\t\t\t</tr>\n')
                # SOURCE LINE 264
            else:
                # SOURCE LINE 265
                __M_writer(u"\t\t\t<input type='hidden' id='totp_timestep' value='")
                __M_writer(escape(c.totp_timestep))
                __M_writer(u"'>\n")
            # SOURCE LINE 267
            __M_writer(u'\t\t<tr>\n\t\t    <td><label for="totp_self_desc" id=\'totp_self_desc_label\'>')
            # SOURCE LINE 268
            __M_writer(escape(_("Description")))
            __M_writer(u'</label></td>\n\t\t    <td><input type="text" name="totp_self_desc" id="totp_self_desc" value="self enrolled" class="text" /></td>\n\t\t</tr>\n        </table>\n\t    <button class=\'action-button\' id=\'button_enroll_totp\'\n\t    \t    onclick="self_totp_submit();">')
            # SOURCE LINE 273
            __M_writer(escape(_("enroll TOTP Token")))
            __M_writer(u'</button>\n\n    </fieldset>\n    </form>\n</div>\n\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


