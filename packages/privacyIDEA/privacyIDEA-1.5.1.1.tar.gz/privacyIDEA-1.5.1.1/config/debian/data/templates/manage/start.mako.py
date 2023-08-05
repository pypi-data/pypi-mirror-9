# -*- coding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 9
_modified_time = 1422216484.944568
_enable_loop = True
_template_filename = '/usr/lib/python2.7/dist-packages/privacyidea/templates/manage/start.mako'
_template_uri = '/manage/start.mako'
_source_encoding = 'utf-8'
from webhelpers.html import escape
_exports = ['sidebar']


def _mako_get_namespace(context, name):
    try:
        return context.namespaces[(__name__, name)]
    except KeyError:
        _mako_generate_namespaces(context)
        return context.namespaces[(__name__, name)]
def _mako_generate_namespaces(context):
    pass
def _mako_inherit(template, context):
    _mako_generate_namespaces(context)
    return runtime._inherit_from(context, u'manage-base.mako', _template_uri)
def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        _ = context.get('_', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 2
        __M_writer(u'\n\n\n\n')
        # SOURCE LINE 43
        __M_writer(u'\n\n\n<div id="main">\n\n<div class=info_box id=info_box>\n<span id=info_text>\n</span>\n<button id=button_info_text>OK</button>\n</div>\n<script>\n\t$(\'#info_box\').hide();\n\t$("#button_info_text").button("enable");\n\t$(\'#button_info_text\').click(function(){\n\t\t$(\'#info_box\').hide(\'blind\',{},500);\n\t});\n</script>\n\n<div id="tabs">\n\t<ul>\n\t\t<li><a href="/manage/tokenview" onclick="view_clicked(\'tokenview\');"><span>')
        # SOURCE LINE 63
        __M_writer(escape(_("Token View")))
        __M_writer(u'</span></a></li>\n\t\t<li><a href="/manage/userview" onclick="view_clicked(\'userview\');"><span>')
        # SOURCE LINE 64
        __M_writer(escape(_("User View")))
        __M_writer(u'</span></a></li>\n\t\t<li><a href="/manage/policies" onclick="view_clicked(\'policies\');"><span>')
        # SOURCE LINE 65
        __M_writer(escape(_("Policies")))
        __M_writer(u'</span></a></li>\n\t\t<li><a href="/manage/machines" onclick="view_clicked(\'machines\');"><span>')
        # SOURCE LINE 66
        __M_writer(escape(_("Machines")))
        __M_writer(u'</span></a></li>\n\t\t<li><a href="/manage/audittrail" onclick="view_clicked(\'audit\');"><span>')
        # SOURCE LINE 67
        __M_writer(escape(_("Audit Trail")))
        __M_writer(u'</span></a></li>\n\t</ul>\n</div>\n\n<!--\n\n<div id="logAccordionResizer" style="padding:10px; width:97%; height:120px;" class="ui-widget-content">\n<div id="logAccordion" class="ui-accordion">\n<h3 class=""ui-accordion-header"><a href="#">Log</a></h3>\n\t<div id="logText">\n\t</div>\n</div>\n<span class="ui-icon ui-icon-grip-dotted-horizontal" style="margin:2px auto;"></span>\n</div>\n-->\n\n<div id=\'errorDiv\'></div>\n<div id=\'successDiv\'></div>\n\n</div>  <!-- end of main-->\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_sidebar(context):
    __M_caller = context.caller_stack._push_frame()
    try:
        _ = context.get('_', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 6
        __M_writer(u'\n    <div id="realms">\n    ')
        # SOURCE LINE 8
        __M_writer(escape(_("Realms")))
        __M_writer(u': <select id=realm></select>\n    </div>\n    \n    <fieldset>\n    <legend id="selected_tokens_header">')
        # SOURCE LINE 12
        __M_writer(escape(_("selected tokens")))
        __M_writer(u'</legend>\n    <div id="selected_tokens"></div>\n    <button class=\'action-button\' id=\'button_unselect\'>\n    ')
        # SOURCE LINE 15
        __M_writer(escape(_("clear token selection")))
        __M_writer(u'\n    </button>\n    </fieldset>\n    \n    <span id="selected_users_header">')
        # SOURCE LINE 19
        __M_writer(escape(_("selected users")))
        __M_writer(u'</span>\n    <div id="selected_users"></div>\n    \n    <span id="selected_machine_header">')
        # SOURCE LINE 22
        __M_writer(escape(_("selected machine")))
        __M_writer(u'</span>\n    <div id="selected_machine"></div>\n    \n\t<div class=button_bar_token id=button_bar_token>\n    <button class=\'action-button\' id=\'button_enroll\'>')
        # SOURCE LINE 26
        __M_writer(escape(_("enroll")))
        __M_writer(u"</button>\n   \n    <button class='action-button' id='button_assign'>")
        # SOURCE LINE 28
        __M_writer(escape(_("assign")))
        __M_writer(u"</button>\n\n    <button class='action-button' id='button_unassign'>")
        # SOURCE LINE 30
        __M_writer(escape(_("unassign")))
        __M_writer(u"</button>\n\n    <button class='action-button' id='button_enable'>")
        # SOURCE LINE 32
        __M_writer(escape(_("enable")))
        __M_writer(u"</button>\n\n    <button class='action-button' id='button_disable'>")
        # SOURCE LINE 34
        __M_writer(escape(_("disable")))
        __M_writer(u"</button>\n\n    <button class='action-button' id='button_setpin'>")
        # SOURCE LINE 36
        __M_writer(escape(_("set PIN")))
        __M_writer(u"</button>\n\n    <button class='action-button' id='button_resetcounter'>")
        # SOURCE LINE 38
        __M_writer(escape(_("Reset failcounter")))
        __M_writer(u"</button>\n\n    <button class='action-button' id='button_delete'>")
        # SOURCE LINE 40
        __M_writer(escape(_("delete")))
        __M_writer(u'</button>\n\t</div>\n\t\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


