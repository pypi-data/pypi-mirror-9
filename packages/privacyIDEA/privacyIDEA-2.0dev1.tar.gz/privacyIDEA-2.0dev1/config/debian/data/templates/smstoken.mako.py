# -*- coding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 9
_modified_time = 1422216484.870112
_enable_loop = True
_template_filename = '/usr/lib/python2.7/dist-packages/privacyidea/lib/tokens/smstoken.mako'
_template_uri = '/smstoken.mako'
_source_encoding = 'utf-8'
from webhelpers.html import escape
_exports = []


# SOURCE LINE 204

from privacyidea.lib.user import getUserPhone



from privacyidea.lib.user import getUserPhone


def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        len = context.get('len', UNDEFINED)
        c = context.get('c', UNDEFINED)
        Exception = context.get('Exception', UNDEFINED)
        _ = context.get('_', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 2
        __M_writer(u'\n\n')
        # SOURCE LINE 4
        if c.scope == 'config.title' :
            # SOURCE LINE 5
            __M_writer(escape(_("SMS OTP Token")))
            __M_writer(u'\n')
        # SOURCE LINE 7
        __M_writer(u'\n\n')
        # SOURCE LINE 9
        if c.scope == 'config' :
            # SOURCE LINE 10
            __M_writer(u'<!-- #################### SMS Provider ################### -->\n<script>\n/*\n * \'typ\'_get_config_val()\n *\n * this method is called, when the token config dialog is opened\n * - it contains the mapping of config entries to the form id\n * - according to the Config entries, the form entries will be filled\n *\n */\nfunction sms_get_config_val(){\n\tvar ret = {};\n\tret[\'SMSProvider\'] \t\t\t= \'c_sms_provider\';\n\tret[\'SMSProviderConfig\'] \t= \'c_sms_provider_config\';\n\tret[\'SMSProviderTimeout\'] \t= \'c_sms_timeout\';\n\tret[\'SMSBlockingTimeout\'] \t= \'c_sms_blocking\';\n\t\n\treturn ret;\n\n}\n/*\n * \'typ\'_get_config_params()\n *\n * this method is called, when the token config is submitted\n * - it will return a hash of parameters for system/setConfig call\n *\n */\nfunction sms_get_config_params(){\n\tvar ret = {};\n\tret[\'SMSProvider\'] \t\t\t= $(\'#c_sms_provider\').val();\n\tret[\'SMSProviderConfig\'] \t= $(\'#c_sms_provider_config\').val();\n\tret[\'SMSProviderConfig.type\'] = \'password\';\n\tret[\'SMSProviderTimeout\'] \t= $(\'#c_sms_timeout\').val();\n\tret[\'SMSBlockingTimeout\'] \t= $(\'#c_sms_blocking\').val();\n\treturn ret;\n}\n\n\nvar\tsipgate_text = \'{ "USERNAME" : "...",\\n')
            # SOURCE LINE 49
            __M_writer(u'"PASSWORD" : "..." }\';\n\nvar\tclickatel_text = \'{ "URL" : "http://api.clickatell.com/http/sendmsg",\\n')
            # SOURCE LINE 52
            __M_writer(u'"PARAMETER" : {\\n')
            # SOURCE LINE 53
            __M_writer(u'"user":"YOU", \\n')
            # SOURCE LINE 54
            __M_writer(u'"password":"YOUR PASSWORD", \\n')
            # SOURCE LINE 55
            __M_writer(u'"api_id":"YOUR API ID"\\n')
            # SOURCE LINE 56
            __M_writer(u'},\\n')
            # SOURCE LINE 57
            __M_writer(u'"SMS_TEXT_KEY":"text",\\n')
            # SOURCE LINE 58
            __M_writer(u'"SMS_PHONENUMBER_KEY":"to",\\n')
            # SOURCE LINE 59
            __M_writer(u'"HTTP_Method":"GET",\\n')
            # SOURCE LINE 60
            __M_writer(u'"RETURN_SUCCESS" : "ID"\\n')
            # SOURCE LINE 61
            __M_writer(u'}\';\n\n$(document).ready(function () {\n\t$(\'#sms_preset_clickatel\').hide();\n\t$(\'#sms_preset_sipgate\').hide();\n\t$(\'#sms_preset_clickatel\').click(function(event){\n\t\t$(\'#c_sms_provider_config\').html(clickatel_text);\n\t\treturn false;\n\t});\n\t$(\'#sms_preset_sipgate\').click(function(event){\n\t\t$(\'#c_sms_provider_config\').html(sipgate_text);\n\t\treturn false;\n\t});\n    $("#form_smsconfig").validate();\n    \tavailableProviders=["privacyidea.smsprovider.HttpSMSProvider.HttpSMSProvider",\n\t\t\t\t\t\t"privacyidea.smsprovider.DeviceSMSProvider.DeviceSMSProvider",\n\t\t\t\t\t\t"privacyidea.smsprovider.SmtpSMSProvider.SmtpSMSProvider",\n\t\t\t\t\t\t"privacyidea.smsprovider.SipgateSMSProvider.SipgateSMSProvider",];\n\t\n\t$( "#c_sms_provider" )\n\t// don\'t navigate away from the field on tab when selecting an item\n\t.bind( "keydown", function( event ) {\n\t\tif ( event.keyCode === $.ui.keyCode.TAB &&\n\t\t\t\t$( this ).data( "autocomplete" ).menu.active ) {\n\t\t\tevent.preventDefault();\n\t}\n\t})\n\t.autocomplete({\n\t\tminLength: 0,\n\t\tsource: function( request, response ) {\n\t\t\t// delegate back to autocomplete, but extract the last term\n\t\t\tresponse( $.ui.autocomplete.filter(\n\t\t\t\tavailableProviders, extractLast( request.term ) ) );\n\t\t},\n\t\tfocus: function() {\n\t\t\t// prevent value inserted on focus\n\t\t\treturn false;\n\t\t},\n\t\tselect: function( event, ui ) {\n\t\t\t// We can only set one single entry in the provider field\n\t\t\tthis.value = ui.item.value;\n\t\t\t// Which entry was entered? So we display preset buttons\n\t\t\t$(\'#sms_preset_clickatel\').hide();\n\t\t\t$(\'#sms_preset_sipgate\').hide();\n\t\t\tif (this.value.match(/HttpSMSProvider/)) {\n\t\t\t\t$(\'#sms_preset_clickatel\').show();\n\t\t\t}\n\t\t\tif (this.value.match(/SipgateSMSProvider/)) {\n\t\t\t\t$(\'#sms_preset_sipgate\').show();\n\t\t\t}\n\t\t\treturn false;\n\t\t}\n\t});\n});\n\n</script>\n\n<form class="cmxform" id="form_smsconfig"><fieldset>\n<legend>')
            # SOURCE LINE 119
            __M_writer(escape(_("SMS Provider Config")))
            __M_writer(u" <a href='")
            __M_writer(escape(c.help_url))
            __M_writer(u'/configuration/tokenconfig/sms.html\' target="_blank">\n\t<img src="/images/help32.png" width="24"\n\ttitle="')
            # SOURCE LINE 121
            __M_writer(escape(_('Open help on SMS OTP token')))
            __M_writer(u'">  \n\t</a>\n\t</legend>\n<table>\n<tr>\n\t<td><label for="c_sms_provider">')
            # SOURCE LINE 126
            __M_writer(escape(_("SMS Provider")))
            __M_writer(u'</label>: </td>\n\t<td><input type="text" name="sms_provider" class="required"  id="c_sms_provider" size="37" maxlength="80"></td>\n</tr><tr>\n\t<td><label for=\'c_sms_provider_config\'>')
            # SOURCE LINE 129
            __M_writer(escape(_("SMS Provider Config")))
            __M_writer(u'</label>: </td>\n\t<td><textarea name="sms_provider_config" class="required"  id="c_sms_provider_config" cols=\'35\' rows=\'6\' maxlength="400">{}</textarea></td>\n</tr><tr>\n\t<td><label for=\'c_sms_timeout\'>')
            # SOURCE LINE 132
            __M_writer(escape(_("SMS Timeout")))
            __M_writer(u'</label>: </td>\n\t<td><input type="text" name="sms_timeout" class="required"  id="c_sms_timeout" size="5" maxlength="5"></td>\n</tr><tr>\n\t<td><label for=\'c_sms_blocking\'>')
            # SOURCE LINE 135
            __M_writer(escape(_("Time between SMS (sec.)")))
            __M_writer(u'</label>: </td>\n\t<td><input type="text" name="sms_blocking" class="required"  id="c_sms_blocking" size="5" maxlength="5" value"30"></td>\n</tr></table>\n\n</fieldset></form>\n<button id=\'sms_preset_clickatel\'>\n\t')
            # SOURCE LINE 141
            __M_writer(escape(_("preset Clickatel")))
            __M_writer(u"</button>\n<button id='sms_preset_sipgate'>\n\t")
            # SOURCE LINE 143
            __M_writer(escape(_("preset Sipgate")))
            __M_writer(u'</button>\n\n')
        # SOURCE LINE 146
        __M_writer(u'\n\n')
        # SOURCE LINE 148
        if c.scope == 'enroll.title' :
            # SOURCE LINE 149
            __M_writer(escape(_("SMS OTP")))
            __M_writer(u'\n')
        # SOURCE LINE 151
        __M_writer(u'\n')
        # SOURCE LINE 152
        if c.scope == 'enroll' :
            # SOURCE LINE 153
            __M_writer(u'<script>\n\nfunction sms_enroll_setup_defaults(config){\n\t// in case we enroll sms otp, we get the mobile number of the user\n\tmobiles = get_selected_mobile();\n\t$(\'#sms_phone\').val($.trim(mobiles[0]));\n}\n\n/*\n * \'typ\'_get_enroll_params()\n *\n * this method is called, when the token  is submitted\n * - it will return a hash of parameters for admin/init call\n *\n */\nfunction sms_get_enroll_params(){\n    var params = {};\n\n\tparams[\'phone\'] \t\t= \'sms\';\n    // phone number\n    params[\'phone\'] \t\t= $(\'#sms_phone\').val();\n    params[\'description\'] \t=  $(\'#sms_phone\').val() + " " + $(\'#enroll_sms_desc\').val();\n    //params[\'serial\'] \t\t= create_serial(\'LSSM\');\n\n    jQuery.extend(params, add_user_data());\n\n    return params;\n}\n</script>\n\n<p>')
            # SOURCE LINE 183
            __M_writer(escape(_("Please enter the mobile phone number for the SMS token")))
            __M_writer(u'</p>\n<table><tr>\n\t<td><label for="sms_phone">')
            # SOURCE LINE 185
            __M_writer(escape(_("phone number")))
            __M_writer(u'</label></td>\n\t<td><input type="text" name="sms_phone" id="sms_phone" value="" class="text ui-widget-content ui-corner-all"></td>\n</tr><tr>\n    <td><label for="enroll_sms_desc" id=\'enroll_sms_desc_label\'>')
            # SOURCE LINE 188
            __M_writer(escape(_("Description")))
            __M_writer(u'</label></td>\n    <td><input type="text" name="enroll_sms_desc" id="enroll_sms_desc" value="webGUI_generated" class="text" /></td>\n</tr>\n</table>\n\n')
        # SOURCE LINE 194
        __M_writer(u'\n\n\n')
        # SOURCE LINE 197
        if c.scope == 'selfservice.title.enroll':
            # SOURCE LINE 198
            __M_writer(escape(_("Register SMS")))
            __M_writer(u'\n')
        # SOURCE LINE 200
        __M_writer(u'\n\n')
        # SOURCE LINE 202
        if c.scope == 'selfservice.enroll':
            # SOURCE LINE 203
            __M_writer(u'\n')
            # SOURCE LINE 206
            __M_writer(u'\n')
            # SOURCE LINE 207

            try:
                    phonenumber = getUserPhone(c.authUser, 'mobile')
                    if phonenumber == None or len(phonenumber) == 0:
                             phonenumber = ''
            except Exception as e:
                    phonenumber = ''
            
            
            __M_locals_builtin_stored = __M_locals_builtin()
            __M_locals.update(__M_dict_builtin([(__M_key, __M_locals_builtin_stored[__M_key]) for __M_key in ['e','phonenumber'] if __M_key in __M_locals_builtin_stored]))
            # SOURCE LINE 214
            __M_writer(u'\n\n<script>\n\tjQuery.extend(jQuery.validator.messages, {\n\t\trequired:  "')
            # SOURCE LINE 218
            __M_writer(escape(_('required input field')))
            __M_writer(u'",\n\t\tminlength: "')
            # SOURCE LINE 219
            __M_writer(escape(_('minimum length must be greater than 10')))
            __M_writer(u'",\n\t});\n\n\tjQuery.validator.addMethod("phone", function(value, element, param){\n        return value.match(/^[+0-9\\/\\ ]+$/i);\n    }, \'')
            # SOURCE LINE 224
            __M_writer(escape(_("Please enter a valid phone number. It may only contain numbers and + or /.")))
            __M_writer(u'\' );\n\n\t$(\'#form_register_sms\').validate({\n        rules: {\n            sms_mobilephone: {\n                required: true,\n                minlength: 10,\n                number: false,\n                phone: true\n            }\n        }\n\t});\n\nfunction self_sms_get_param()\n{\n\tvar urlparam = {};\n\tvar mobilephone = $(\'#sms_mobilephone\').val();\n\n\n\turlparam[\'type\'] \t\t= \'sms\';\n\turlparam[\'phone\']\t\t= mobilephone;\n\turlparam[\'description\'] = mobilephone + \'_\' + $("#sms_self_desc").val();\n\n\treturn urlparam;\n}\n\nfunction self_sms_clear()\n{\n\treturn true;\n}\nfunction self_sms_submit(){\n\n\tvar ret = false;\n\n\tif ($(\'#form_register_sms\').valid()) {\n\t\tvar params =  self_sms_get_param();\n\t\tenroll_token( params );\n\t\t//self_sms_clear();\n\t\tret = true;\n\t} else {\n\t\talert(\'')
            # SOURCE LINE 264
            __M_writer(escape(_("Form data not valid.")))
            __M_writer(u"');\n\t}\n\treturn ret;\n}\n\n</script>\n\n<h1>")
            # SOURCE LINE 271
            __M_writer(escape(_("Register your SMS OTP Token / mobileTAN")))
            __M_writer(u'</h1>\n<div id=\'register_sms_form\'>\n\t<form class="cmxform" id=\'form_register_sms\'>\n\t<fieldset>\n\t\t<table>\n\t\t<tr>\n\t\t<td><label for=\'sms_mobilephone\'>')
            # SOURCE LINE 277
            __M_writer(escape(_("Your mobile phone number")))
            __M_writer(u'</label></td>\n\t\t<td><input id=\'sms_mobilephone\'\n\t\t\t\t\tname=\'sms_mobilephone\'\n\t\t\t\t\tclass="required ui-widget-content ui-corner-all"\n\t\t\t\t\tvalue=\'')
            # SOURCE LINE 281
            __M_writer(escape(phonenumber))
            __M_writer(u'\'/>\n\t\t</td>\n\t\t</tr>\n\t\t<tr>\n\t\t    <td><label for="sms_self_desc" id=\'sms_self_desc_label\'>')
            # SOURCE LINE 285
            __M_writer(escape(_("Description")))
            __M_writer(u'</label></td>\n\t\t    <td><input type="text" name="sms_self_desc" id="sms_self_desc" value="self_registered"; class="text" /></td>\n\t\t</tr>\n        </table>\n        <button class=\'action-button\' id=\'button_register_sms\' onclick="self_sms_submit();">')
            # SOURCE LINE 289
            __M_writer(escape(_("register SMS Token")))
            __M_writer(u'</button>\n    </fieldset>\n    </form>\n</div>\n')
        # SOURCE LINE 294
        __M_writer(u'\n\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


