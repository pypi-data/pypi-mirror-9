# -*- coding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 9
_modified_time = 1422216580.949147
_enable_loop = True
_template_filename = '/usr/lib/python2.7/dist-packages/privacyidea/templates/manage/policies.mako'
_template_uri = '/manage/policies.mako'
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
        __M_writer(u'    \n\n<a id=policy_export>')
        # SOURCE LINE 4
        __M_writer(escape(_("Export policies")))
        __M_writer(u'</a>\n\n<button id=policy_import>')
        # SOURCE LINE 6
        __M_writer(escape(_("Import policies")))
        __M_writer(u"</button>\n\n<a href='")
        # SOURCE LINE 8
        __M_writer(escape(c.help_url))
        __M_writer(u'/policies/index.html\' target="_blank">\n\t<img alt="(?)" width=24\n\tsrc="/images/help32.png"  \n\ttitle=\'')
        # SOURCE LINE 11
        __M_writer(escape(_("Open help on policies")))
        __M_writer(u'\'>\n</a>\n\n<table id="policy_table" class="flexme2" style="display:none"></table>\n   \n   \n<table>\n  <tr>\n  \t<td><label for=policy_active>')
        # SOURCE LINE 19
        __M_writer(escape(_("Active")))
        __M_writer(u'</label></td>\n  \t<td><input type="checkbox" name="policy_active" id="policy_active" value="True"></td>\n  </tr>\t\n  <tr>\n  \t<td><label for=policy_name>')
        # SOURCE LINE 23
        __M_writer(escape(_("Policy name")))
        __M_writer(u'</label></td>\n  \t<td><input type="text" class="required"  id="policy_name" size="40" maxlength="80" \n  \t\ttitle=\'')
        # SOURCE LINE 25
        __M_writer(escape(_("The name of the policy")))
        __M_writer(u"'></td>\n  </tr>\n  <tr>\n\t<td><label for=policy_scope_combo>")
        # SOURCE LINE 28
        __M_writer(escape(_("Scope")))
        __M_writer(u'</label></td>\n\t<td>\n\t<select id=\'policy_scope_combo\'>\n\t<option value="_">')
        # SOURCE LINE 31
        __M_writer(escape(_("__undefined__")))
        __M_writer(u'</option>\n')
        # SOURCE LINE 32
        for scope in c.polDefs.keys():
            # SOURCE LINE 33
            __M_writer(u'\t<option value="')
            __M_writer(escape(scope))
            __M_writer(u'">')
            __M_writer(escape(scope))
            __M_writer(u'</option>\n')
        # SOURCE LINE 35
        __M_writer(u'\t</select>\n\t</td>\n  </tr>\n    <tr>\n  \t<td><label for="policy_action">')
        # SOURCE LINE 39
        __M_writer(escape(_("Action")))
        __M_writer(u'</label></td>\n  \t<td><input type="text" class="required"  id="policy_action" size="40" maxlength="200" \n  \t\ttitle=\'')
        # SOURCE LINE 41
        __M_writer(escape(_("The action that should be allowed. These are actions like: enrollSMS, enrollMOTP...The actions may be comma separated.")))
        __M_writer(u'\'>\n  \t</td><td>\n  \t\t<span id="action_info" class="help_text"> </span>\n  \t\t</td>\n  </tr>\n  <tr>\n  \t<td><label for="policy_user">')
        # SOURCE LINE 47
        __M_writer(escape(_("User")))
        __M_writer(u'</label></td>\n  \t<td><input type="text"  id="policy_user" size="40" maxlength="80" \n  \t\ttitle=\'')
        # SOURCE LINE 49
        __M_writer(escape(_("The user or usergroup the policy should apply to")))
        __M_writer(u'\'></td>\n  </tr>\n    <tr>\n  \t<td><label for="policy_realm">')
        # SOURCE LINE 52
        __M_writer(escape(_("Realm")))
        __M_writer(u'</label></td>\n  \t<td><input type="text" class="required"  id="policy_realm" size="40" maxlength="80" \n  \t\ttitle=\'')
        # SOURCE LINE 54
        __M_writer(escape(_("The realm the policy applies to")))
        __M_writer(u'\'></td>\n  </tr>\n   <tr>\n  \t<td><label for="policy_client">')
        # SOURCE LINE 57
        __M_writer(escape(_("Client")))
        __M_writer(u'</label></td>\n  \t<td><input type="text"  id="policy_client" size="40" maxlength="120" \n  \t\ttitle=\'')
        # SOURCE LINE 59
        __M_writer(escape(_("Comma separated list of client IPs and Subnets.")))
        __M_writer(u"'></td>\n  </tr>\n  <tr>\n  \t<td><label for=policy_time>")
        # SOURCE LINE 62
        __M_writer(escape(_("Time")))
        __M_writer(u'</label></td>\n  \t<td><input type="text"  id="policy_time" size="40" maxlength="80" \n  \t\ttitle=\'')
        # SOURCE LINE 64
        __M_writer(escape(_("The time on which the policy should be applied")))
        __M_writer(u"'></td>\n  </tr>\n  <tr>\n  \t<td></td><td>\n  \t<button  id=button_policy_add>")
        # SOURCE LINE 68
        __M_writer(escape(_("set policy")))
        __M_writer(u'</button>\n  \t<button  id=button_policy_delete>')
        # SOURCE LINE 69
        __M_writer(escape(_("delete policy")))
        __M_writer(u'</button>\n  \t</td>\n  </tr>\n</table> \n<script type="text/javascript"> \n\tview_policy();\n</script>\n\n\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


