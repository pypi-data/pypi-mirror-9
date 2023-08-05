# -*- coding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 9
_modified_time = 1422216484.935358
_enable_loop = True
_template_filename = '/usr/lib/python2.7/dist-packages/privacyidea/lib/tokens/sshkeytoken.mako'
_template_uri = '/sshkeytoken.mako'
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
            __M_writer(escape(_("SSH Token")))
            __M_writer(u'\n')
        # SOURCE LINE 6
        __M_writer(u'\n')
        # SOURCE LINE 7
        if c.scope == 'enroll' :
            # SOURCE LINE 8
            __M_writer(u'\n<script>\n/*\n * \'typ\'_get_enroll_params()\n *\n * this method is called, when the token  is submitted\n * - it will return a hash of parameters for admin/init call\n *\n */\n\nfunction sshkey_get_enroll_params(){\n    var params = {};\n    params[\'type\'] = \'sshkey\';\n    //params[\'serial\'] = create_serial(\'SSHK\');\n    params[\'otpkey\'] \t= $(\'#ssh_key\').val();\n\tparams[\'description\'] =  $(\'#enroll_ssh_desc\').val();\n\n\tjQuery.extend(params, add_user_data());\n\n    return params;\n}\n\nfunction sshkey_changed() {\n    // Change the ssh key description\n    var pubkey = $(\'#ssh_key\').val();\n    var re = new RegExp("==\\\\s*(.*)");\n    var m = re.exec(pubkey);\n    var s = "";\n  \tif ( m ) {\n  \t\ts=m[1];\n  \t\t$(\'#enroll_ssh_desc\').val(s);\n\t}\n}\n\n</script>\n\n<p>')
            # SOURCE LINE 44
            __M_writer(escape(_("Here you can upload your public ssh key.")))
            __M_writer(u'</p>\n<table>\n<tr>\n\t<td><label for="ssh_key">')
            # SOURCE LINE 47
            __M_writer(escape(_("SSH public key")))
            __M_writer(u'</label></td>\n\t<td><textarea name="ssh_key" id="ssh_key" value="" class="text ui-widget-content ui-corner-all"\n\t\tcols="40" rows="8" onChange="sshkey_changed();"\n\t\tonKeyUp="sshkey_changed();"></textarea></td>\n</tr>\n<tr>\n    <td><label for="enroll_ssh_desc" id=\'enroll_ssh_desc_label\'>')
            # SOURCE LINE 53
            __M_writer(escape(_("Description")))
            __M_writer(u'</label></td>\n    <!-- we read the description from the ssh key --> \n    <td><input type="text" name="enroll_ssh_desc" id="enroll_ssh_desc" \n    \tvalue="webGUI imported" class="text"\n    \tsize=40 /></td>\n</tr>\n</table>\n\n\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


