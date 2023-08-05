# -*- coding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 9
_modified_time = 1422216484.906498
_enable_loop = True
_template_filename = '/usr/lib/python2.7/dist-packages/privacyidea/lib/tokens/radiustoken.mako'
_template_uri = '/radiustoken.mako'
_source_encoding = 'utf-8'
from webhelpers.html import escape
_exports = []


def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        c = context.get('c', UNDEFINED)
        Exception = context.get('Exception', UNDEFINED)
        _ = context.get('_', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 2
        __M_writer(u'\n\n')
        # SOURCE LINE 4
        if c.scope == 'config.title' :
            # SOURCE LINE 5
            __M_writer(u' ')
            __M_writer(escape(_("RADIUS Token")))
            __M_writer(u'\n')
        # SOURCE LINE 7
        __M_writer(u'\n\n')
        # SOURCE LINE 9
        if c.scope == 'config' :
            # SOURCE LINE 10
            __M_writer(u'<script>\n\n/*\n * \'typ\'_get_config_val()\n *\n * this method is called, when the token config dialog is opened\n * - it contains the mapping of config entries to the form id\n * - according to the Config entries, the form entries will be filled\n *\n */\n\n\nfunction radius_get_config_val(){\n\tvar id_map = {};\n\n    id_map[\'radius.server\']   = \'sys_radius_server\';\n    id_map[\'radius.secret\']  = \'sys_radius_secret\';\n    id_map[\'radius.local_checkpin\'] = \'sys_radius_local_checkpin\';\n    // FIXME: We need to set the checkpin select box. Do not know how!\n\n\treturn id_map;\n\n}\n\n/*\n * \'typ\'_get_config_params()\n *\n * this method is called, when the token config is submitted\n * - it will return a hash of parameters for system/setConfig call\n *\n */\nfunction radius_get_config_params(){\n\n\tvar url_params ={};\n\n    url_params[\'radius.server\'] \t= $(\'#sys_radius_server\').val();\n    url_params[\'radius.secret\'] \t= $(\'#sys_radius_secret\').val();\n    url_params[\'radius.local_checkpin\'] \t= $(\'#sys_radius_local_checkpin\').val();\n\n\treturn url_params;\n}\n\n\njQuery.validator.addMethod("sys_radius_server", function(value, element, param){\n      return value.match(param);\n}, "')
            # SOURCE LINE 55
            __M_writer(escape(_('Please enter a valid RADIUS server specification. It needs to be of the form <name_or_ip>:<port>')))
            __M_writer(u'");\n\n\n$("#form_config_radius").validate({\n         rules: {\n            sys_radius_server: {\n                required: true,\n                number: false,\n                sys_radius_server: /^[a-z0-9.-_]*:\\d*/i\n             }\n         }\n     });\n\n</script>\n\n<form class="cmxform" id=\'form_config_radius\'>\n<fieldset>\n\t<legend>')
            # SOURCE LINE 72
            __M_writer(escape(_("RADIUS settings")))
            __M_writer(u'</legend>\n\t<table>\n\t<tr>\n\t<td><label for="sys_radius_server" title=\'')
            # SOURCE LINE 75
            __M_writer(escape(_("You need to enter the server like myradius:1812")))
            __M_writer(u"'>\n\t\t")
            # SOURCE LINE 76
            __M_writer(escape(_("RADIUS server")))
            __M_writer(u'</label></td>\n\t<td><input class="required" type="text" name="sys_radius_server" id="sys_radius_server" \n\t\tclass="text ui-widget-content ui-corner-all" value="localhost:1812"/></td>\n\t</tr>\n\n\t<tr><td><label for="sys_radius_local_checkpin" title=\'')
            # SOURCE LINE 81
            __M_writer(escape(_("The PIN can either be verified on this local privacyIDEA server or forwarded to the RADIUS server")))
            __M_writer(u"'>\n\t\t")
            # SOURCE LINE 82
            __M_writer(escape(_("check PIN")))
            __M_writer(u'</label></td>\n\t<td><select name="sys_radius_local_checkpin" id="sys_radius_local_checkpin"\n\t\ttitle=\'')
            # SOURCE LINE 84
            __M_writer(escape(_("The PIN can either be verified on this local privacyIDEA server or on the RADIUS server")))
            __M_writer(u"'>\n\t\t\t<option value=0>")
            # SOURCE LINE 85
            __M_writer(escape(_("on RADIUS server")))
            __M_writer(u'</option>\n\t\t\t<option value=1>')
            # SOURCE LINE 86
            __M_writer(escape(_("locally")))
            __M_writer(u'</option>\n\t\t</select></td>\n\t</tr><tr>\n\t<td><label for="sys_radius_secret">')
            # SOURCE LINE 89
            __M_writer(escape(_("RADIUS shared secret")))
            __M_writer(u'</label></td>\n\t<td><input type="password" name="sys_radius_secret" id="sys_radius_secret" class="text ui-widget-content ui-corner-all" /></td>\n\t</tr>\n\t</table>\n</fieldset>\n</form>\n')
        # SOURCE LINE 96
        __M_writer(u'\n\n')
        # SOURCE LINE 98
        if c.scope == 'enroll.title' :
            # SOURCE LINE 99
            __M_writer(escape(_("RADIUS token")))
            __M_writer(u'\n')
        # SOURCE LINE 101
        __M_writer(u'\n')
        # SOURCE LINE 102
        if c.scope == 'enroll' :
            # SOURCE LINE 103
            __M_writer(u'<script>\n\n/*\n * \'typ\'_get_enroll_params()\n *\n * this method is called, when the token  is submitted\n * - it will return a hash of parameters for admin/init call\n *\n */\n\nfunction radius_get_enroll_params(){\n    var params = {};\n    params[\'type\'] = \'radius\';\n\tparams[\'radius.server\'] \t\t=  $(\'#radius_server\').val();\n\tparams[\'radius.local_checkpin\'] =  $(\'#radius_local_checkpin\').val();\n\tparams[\'radius.user\'] \t\t\t=  $(\'#radius_user\').val();\n\tparams[\'radius.secret\'] \t\t=  $(\'#radius_secret\').val();\n\tparams[\'description\'] \t\t\t=  "radius:" + $(\'#radius_server\').val();\n\n\tjQuery.extend(params, add_user_data());\n    return params;\n}\n\njQuery.validator.addMethod("radius_server", function(value, element, param){\n      return value.match(param);\n}, "')
            # SOURCE LINE 128
            __M_writer(escape(_('Please enter a valid RADIUS server specification. It needs to be of the form <name_or_ip>:<port>')))
            __M_writer(u'");\n\n\n$("#form_enroll_token").validate({\n         rules: {\n            radius_server: {\n                required: true,\n                number: false,\n                radius_server: /^[a-z0-9.-_]*:\\d*/i\n             }\n         }\n     });\n\n')
            # SOURCE LINE 141

            from privacyidea.lib.config import getFromConfig
            sys_radius_server = ""
            sys_radius_secret = ""
            sys_checkpin_local = "selected"
            sys_checkpin_remote = ""
            
            try:
                    sys_radius_server = getFromConfig("radius.server")
                    sys_radius_secret = getFromConfig("radius.secret")
                    sys_radius_local_checkpin = getFromConfig("radius.local_checkpin")
            
                    if sys_radius_local_checkpin == 0:
                            sys_checkpin_local = ""
                            sys_checkpin_remote = "selected"
            except Exception:
                    pass
            
            
            
            __M_locals_builtin_stored = __M_locals_builtin()
            __M_locals.update(__M_dict_builtin([(__M_key, __M_locals_builtin_stored[__M_key]) for __M_key in ['sys_checkpin_local','getFromConfig','sys_checkpin_remote','sys_radius_secret','sys_radius_local_checkpin','sys_radius_server'] if __M_key in __M_locals_builtin_stored]))
            # SOURCE LINE 159
            __M_writer(u'\n</script>\n\n<p>')
            # SOURCE LINE 162
            __M_writer(escape(_("Here you can define, to which RADIUS server the request should be forwarded.")))
            __M_writer(u'</p>\n<p>')
            # SOURCE LINE 163
            __M_writer(escape(_("Please specify the server, the secret and the username")))
            __M_writer(u'</p>\n<table><tr>\n\t<td><label for="radius_server" title=\'')
            # SOURCE LINE 165
            __M_writer(escape(_("You need to enter the server like myradius:1812")))
            __M_writer(u"'>\n\t\t")
            # SOURCE LINE 166
            __M_writer(escape(_("RADIUS server")))
            __M_writer(u'</label></td>\n\t<td><input class="required" type="text" name="radius_server" id="radius_server" value="')
            # SOURCE LINE 167
            __M_writer(escape(sys_radius_server))
            __M_writer(u'" class="text ui-widget-content ui-corner-all"/></td>\n\t</tr><tr>\n\t<td><label for="radius_local_checkpin" title=\'')
            # SOURCE LINE 169
            __M_writer(escape(_("The PIN can either be verified on this local privacyIDEA server or forwarded to the RADIUS server")))
            __M_writer(u"'>\n\t\t")
            # SOURCE LINE 170
            __M_writer(escape(_("check PIN")))
            __M_writer(u'</label></td>\n\t<td><select name="radius_local_checkpin" id="radius_local_checkpin"\n\t\ttitle=\'')
            # SOURCE LINE 172
            __M_writer(escape(_("The PIN can either be verified on this local privacyIDEA server or on the RADIUS server")))
            __M_writer(u"'>\n\t\t\t<option ")
            # SOURCE LINE 173
            __M_writer(escape(sys_checkpin_remote))
            __M_writer(u' value=0>')
            __M_writer(escape(_("on RADIUS server")))
            __M_writer(u'</option>\n\t\t\t<option ')
            # SOURCE LINE 174
            __M_writer(escape(sys_checkpin_local))
            __M_writer(u' value=1>')
            __M_writer(escape(_("locally")))
            __M_writer(u'</option>\n\t\t</select></td>\n\t</tr><tr>\n\t<td><label for="radius_user">')
            # SOURCE LINE 177
            __M_writer(escape(_("RADIUS user")))
            __M_writer(u'</label></td>\n\t<td><input type="text" name="radius_user" id="radius_user" value="" class="text ui-widget-content ui-corner-all" /></td>\n\t</tr><tr>\n\t<td><label for="radius_secret">')
            # SOURCE LINE 180
            __M_writer(escape(_("RADIUS shared secret")))
            __M_writer(u'</label></td>\n\t<td><input type="password" name="radius_secret" id="radius_secret" value="')
            # SOURCE LINE 181
            __M_writer(escape(sys_radius_secret))
            __M_writer(u'" class="text ui-widget-content ui-corner-all" /></td>\n\t</tr></table>\n\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


