# -*- coding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 9
_modified_time = 1422216484.839633
_enable_loop = True
_template_filename = '/usr/lib/python2.7/dist-packages/privacyidea/lib/tokens/remotetoken.mako'
_template_uri = '/remotetoken.mako'
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
            __M_writer(escape(_("Remote Token")))
            __M_writer(u'\n')
        # SOURCE LINE 7
        __M_writer(u'\n\n')
        # SOURCE LINE 9
        if c.scope == 'config' :
            # SOURCE LINE 10
            __M_writer(u'<script>\n\n/*\n * \'typ\'_get_config_val()\n *\n * this method is called, when the token config dialog is opened\n * - it contains the mapping of config entries to the form id\n * - according to the Config entries, the form entries will be filled\n *\n */\n\n\nfunction remote_get_config_val(){\n\tvar id_map = {};\n\n    id_map[\'remote.server\'] \t\t= \'sys_remote_server\';\n    id_map[\'remote.local_checkpin\'] = \'sys_remote_local_checkpin\';\n    id_map[\'remote.realm\'] \t\t\t= \'sys_remote_realm\';\n    id_map[\'remote.resConf\'] \t\t= \'sys_remote_resConf\';\n\n    // FIXME: We need to set the checkpin select box. Do not know how!\n\n\treturn id_map;\n\n}\n\n/*\n * \'typ\'_get_config_params()\n *\n * this method is called, when the token config is submitted\n * - it will return a hash of parameters for system/setConfig call\n *\n */\nfunction remote_get_config_params(){\n\tvar url_params ={};\n\n    url_params[\'remote.server\'] \t= $(\'#sys_remote_server\').val();\n    url_params[\'remote.realm\'] \t= $(\'#sys_remote_realm\').val();\n    url_params[\'remote.resConf\'] \t= $(\'#sys_remote_resConf\').val();\n    url_params[\'remote.remote_checkpin\'] \t= $(\'#sys_remote_local_checkpin\').val();\n\n\treturn url_params;\n}\n\n\njQuery.validator.addMethod("sys_remote_server", function(value, element, param){\n      return value.match(param);\n}, "')
            # SOURCE LINE 57
            __M_writer(escape(_('Please enter a valid remote server specification. It needs to be of the form http://server or https://server')))
            __M_writer(u'");\n\n\n$("#form_config_remote").validate({\n         rules: {\n            sys_remote_server: {\n                required: true,\n                number: false,\n                \tsys_remote_server: /^(http:\\/\\/|https:\\/\\/)/i\n             }\n         }\n     });\n\n</script>\n\n<form class="cmxform" id=\'form_config_remote\'>\n\t<table>\n\t<tr>\n\t<td><label for="sys_remote_server" title=\'')
            # SOURCE LINE 75
            __M_writer(escape(_("You need to enter the remote privacyIDEA server like https://remoteprivacyidea")))
            __M_writer(u"'>\n\t\t")
            # SOURCE LINE 76
            __M_writer(escape(_("REMOTE server")))
            __M_writer(u'</label></td>\n\t<td><input class="required" type="text" name="sys_remote_server" id="sys_remote_server"\n\t\tclass="text ui-widget-content ui-corner-all" value="https://localhost"/></td>\n\t</tr>\n\n\t<tr><td><label for="sys_remote_local_checkpin" title=\'')
            # SOURCE LINE 81
            __M_writer(escape(_("The PIN can either be verified on this local privacyIDEA server or forwarded to the remote server")))
            __M_writer(u"'>\n\t\t")
            # SOURCE LINE 82
            __M_writer(escape(_("check PIN")))
            __M_writer(u'</label></td>\n\t<td><select name="sys_remote_local_checkpin" id="sys_remote_local_checkpin"\n\t\ttitle=\'')
            # SOURCE LINE 84
            __M_writer(escape(_("The PIN can either be verified on this local privacyIDEA server or on the remote server")))
            __M_writer(u"'>\n\t\t\t<option value=0>")
            # SOURCE LINE 85
            __M_writer(escape(_("on REMOTE server")))
            __M_writer(u'</option>\n\t\t\t<option value=1>')
            # SOURCE LINE 86
            __M_writer(escape(_("locally")))
            __M_writer(u'</option>\n\t\t</select></td>\n\t</tr>\n\n\t<tr>\n\t<td><label for="sys_remote_realm">')
            # SOURCE LINE 91
            __M_writer(escape(_("Remote Realm")))
            __M_writer(u'</label></td>\n\t<td><input type="text" name="sys_remote_realm" id="sys_remote_realm"\n\t\tclass="text ui-widget-content ui-corner-all" /></td>\n\t</tr>\n\n\t<tr>\n\t<td><label for="sys_remote_resConf">')
            # SOURCE LINE 97
            __M_writer(escape(_("Remote Resolver")))
            __M_writer(u'</label></td>\n\t<td><input type="text" name="sys_remote_resConf" id="sys_remote_resConf"\n\t\tclass="text ui-widget-content ui-corner-all" /></td>\n\t</tr>\n\t</table>\n\n</form>\n')
        # SOURCE LINE 105
        __M_writer(u'\n\n')
        # SOURCE LINE 107
        if c.scope == 'enroll.title' :
            # SOURCE LINE 108
            __M_writer(escape(_("REMOTE token")))
            __M_writer(u'\n')
        # SOURCE LINE 110
        __M_writer(u'\n')
        # SOURCE LINE 111
        if c.scope == 'enroll' :
            # SOURCE LINE 112
            __M_writer(u'<script>\n\n/*\n * \'typ\'_get_enroll_params()\n *\n * this method is called, when the token  is submitted\n * - it will return a hash of parameters for admin/init call\n *\n */\n\nfunction remote_get_enroll_params(){\n\tvar params ={};\n\n    //params[\'serial\'] =  create_serial(\'LSRE\');\n    params[\'remote.server\'] \t\t= $(\'#remote_server\').val();\n    params[\'remote.local_checkpin\'] = $(\'#remote_local_checkpin\').val();\n    params[\'remote.serial\'] \t\t= $(\'#remote_serial\').val();\n    params[\'remote.user\'] \t\t\t= $(\'#remote_user\').val();\n    params[\'remote.realm\'] \t\t\t= $(\'#remote_realm\').val();\n    params[\'remote.resConf\'] \t\t= $(\'#remote_resconf\').val();\n    params[\'description\'] \t\t\t= "remote:" + $(\'#remote_server\').val();\n\n    jQuery.extend(params, add_user_data());\n\n\treturn params;\n}\n\n\njQuery.validator.addMethod("remote_server", function(value, element, param){\n    return value.match(param);\n}, "')
            # SOURCE LINE 142
            __M_writer(escape(_('Please enter a valid URL for the privacyIDEA server. It needs to start with http:// or https://')))
            __M_writer(u'");\n\n\n\n$("#form_enroll_token").validate({\n         rules: {\n            remote_server: {\n                required: true,\n                number: false,\n                remote_server: /^(http:\\/\\/|https:\\/\\/)/i\n             }\n         }\n     });\n\n')
            # SOURCE LINE 156

            from privacyidea.lib.config import getFromConfig
            sys_remote_server = ""
            sys_remote_realm = ""
            sys_remote_resConf = ""
            sys_checkpin_local = "selected"
            sys_checkpin_remote = ""
            
            try:
                    sys_remote_server = getFromConfig("remote.server")
                    sys_remote_realm = getFromConfig("remote.realm")
                    sys_remote_resConf = getFromConfig("remote.resConf")
                    sys_remote_local_checkpin = getFromConfig("remote.local_checkpin")
            
                    if sys_remote_local_checkpin == 0:
                            sys_checkpin_local = ""
                            sys_checkpin_remote = "selected"
            except Exception:
                    pass
            
            
            
            __M_locals_builtin_stored = __M_locals_builtin()
            __M_locals.update(__M_dict_builtin([(__M_key, __M_locals_builtin_stored[__M_key]) for __M_key in ['sys_remote_realm','sys_checkpin_local','sys_remote_resConf','sys_checkpin_remote','sys_remote_local_checkpin','sys_remote_server','getFromConfig'] if __M_key in __M_locals_builtin_stored]))
            # SOURCE LINE 176
            __M_writer(u'\n</script>\n\n<p>')
            # SOURCE LINE 179
            __M_writer(escape(_("Here you can define to which privacyIDEA Server the authentication request should be forwarded.")))
            __M_writer(u'</p>\n<p>')
            # SOURCE LINE 180
            __M_writer(escape(_("You can either forward the OTP to a remote serial number or to a remote user.")))
            __M_writer(u'</p>\n<p>')
            # SOURCE LINE 181
            __M_writer(escape(_("If you do not enter a remote serial or a remote user, the request will be forwarded to the remote user with the same username")))
            __M_writer(u'</p>\n<table><tr>\n\t<td><label for="remote_server" title=\'')
            # SOURCE LINE 183
            __M_writer(escape(_("You need to enter the server like \'https://privacyidea.my.domain\'")))
            __M_writer(u"'>\n\t\t")
            # SOURCE LINE 184
            __M_writer(escape(_("remote server")))
            __M_writer(u'</label></td>\n\t<td><input class="required" type="text" name="remote_server" id="remote_server"\n\t\tvalue="')
            # SOURCE LINE 186
            __M_writer(escape(sys_remote_server))
            __M_writer(u'" class="text ui-widget-content ui-corner-all"/></td>\n\t</tr><tr>\n\t<td><label for="remote_local_checkpin" title=\'{_("The PIN can either be verified on this local privacyIDEA server or on the remote privacyIDEA server")}\'>\n\t\t')
            # SOURCE LINE 189
            __M_writer(escape(_("check PIN")))
            __M_writer(u'</label></td>\n\t<td><select name="remote_local_checkpin" id="remote_local_checkpin"\n\t\ttitle=\'')
            # SOURCE LINE 191
            __M_writer(escape(_("The PIN can either be verified on this local privacyIDEA server or on the remote privacyIDEA server")))
            __M_writer(u"'>\n\t\t<option ")
            # SOURCE LINE 192
            __M_writer(escape(sys_checkpin_remote))
            __M_writer(u' value=0>')
            __M_writer(escape(_("remotely")))
            __M_writer(u'</option>\n\t\t<option ')
            # SOURCE LINE 193
            __M_writer(escape(sys_checkpin_local))
            __M_writer(u' value=1>')
            __M_writer(escape(_("locally")))
            __M_writer(u'</option>\n\t</select></td>\n\t</tr><tr>\n\t<td><label for="remote_serial">')
            # SOURCE LINE 196
            __M_writer(escape(_("remote serial")))
            __M_writer(u'</label></td>\n\t<td><input type="text" name="remote_serial" id="remote_serial" value="" class="text ui-widget-content ui-corner-all" /></td>\n\t</tr><tr>\n\t<td><label for="remote_user">')
            # SOURCE LINE 199
            __M_writer(escape(_("remote user")))
            __M_writer(u'</label></td>\n\t<td><input type="text" name="remote_user" id="remote_user" value="" class="text ui-widget-content ui-corner-all" /></td>\n\t</tr><tr>\n\t<td><label for="remote_realm">')
            # SOURCE LINE 202
            __M_writer(escape(_("remote user realm")))
            __M_writer(u'</label></td>\n\t<td><input type="text" name="remote_realm" id="remote_realm"\n\t\tvalue="')
            # SOURCE LINE 204
            __M_writer(escape(sys_remote_realm))
            __M_writer(u'" class="text ui-widget-content ui-corner-all" /></td>\n\t</tr><tr>\n\t<td><label for="remote_resconf">')
            # SOURCE LINE 206
            __M_writer(escape(_("remote user useridresolver")))
            __M_writer(u'</label></td>\n\t<td><input type="text" name="remote_resconf" id="remote_resconf"\n\t\tvalue="')
            # SOURCE LINE 208
            __M_writer(escape(sys_remote_resConf))
            __M_writer(u'" class="text ui-widget-content ui-corner-all" /></td>\n\t</tr></table>\n\n\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


