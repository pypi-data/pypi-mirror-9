# -*- coding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 9
_modified_time = 1422216555.35042
_enable_loop = True
_template_filename = '/usr/lib/python2.7/dist-packages/privacyidea/templates/manage/userview.mako'
_template_uri = '/manage/userview.mako'
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
        __M_writer(u'<div style="float:right">\n<a href=\'')
        # SOURCE LINE 3
        __M_writer(escape(c.help_url))
        __M_writer(u'/userview/index.html\' target="_blank">\n\t<img alt="(?)" width=24\n\tsrc="/images/help32.png"  \n\ttitle=\'')
        # SOURCE LINE 6
        __M_writer(escape(_("help on userview")))
        __M_writer(u'\'>\n</a>\n</div>\n\n<table id="user_table" class="flexme2" style="display:none"></table>\n   \n<script type="text/javascript"> \n\nview_user();\n\n</script>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


