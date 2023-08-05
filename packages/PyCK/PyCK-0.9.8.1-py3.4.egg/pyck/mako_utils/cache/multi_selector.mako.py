# -*- coding:utf8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 10
_modified_time = 1423269272.0046568
_enable_loop = True
_template_filename = '/MyWork/Projects/PyCK/pyck/mako_utils/templates/multi_selector.mako'
_template_uri = 'multi_selector.mako'
_source_encoding = 'utf8'
_exports = ['show_items']


def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        items = context.get('items', UNDEFINED)
        ignore_prefix = context.get('ignore_prefix', UNDEFINED)
        def show_items(records,fname=None,ignore_prefix=None,indent='',parent_key=None):
            return render_show_items(context._locals(__M_locals),records,fname,ignore_prefix,indent,parent_key)
        field_name = context.get('field_name', UNDEFINED)
        __M_writer = context.writer()
        __M_writer('\n\n<script type="application/x-javascript">\n    //dojo.query(\'#main2 > input[type=checkbox]:checked\')\n    \n    function toggle_selection(chkbox, target_container){\n        require([ "dijit/registry", "dojo/query"], function(registry, query){  \n            query(target_container + " input").forEach(function(node, index, arr){\n              registry.byId(node.id).set("checked", registry.byId(chkbox).checked);\n            });\n          });\n    }\n</script>\n\n')
        __M_writer(str(show_items(items, field_name, ignore_prefix, '')))
        __M_writer('\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_show_items(context,records,fname=None,ignore_prefix=None,indent='',parent_key=None):
    __M_caller = context.caller_stack._push_frame()
    try:
        isinstance = context.get('isinstance', UNDEFINED)
        dict = context.get('dict', UNDEFINED)
        def show_items(records,fname=None,ignore_prefix=None,indent='',parent_key=None):
            return render_show_items(context,records,fname,ignore_prefix,indent,parent_key)
        __M_writer = context.writer()
        __M_writer('\n    ')

        extra_css_class = ""
        table_id = ""
        if parent_key:
            extra_css_class = 'collapse'
            table_id = 'id="{}_subitems"'.format(parent_key)
        
        
        __M_writer('\n    <table class="table table-condensed table-hover table-striped ')
        __M_writer(str(extra_css_class))
        __M_writer('" ')
        __M_writer(str(table_id))
        __M_writer('>\n')
        for k, v in records.items():
            __M_writer('        ')

            if ignore_prefix is not None and k.startswith(ignore_prefix):
                continue
            
            
            __M_writer('\n        \n')
            if not isinstance(v, dict):
                __M_writer('            <tr>\n                <td colspan="2">\n')
                if indent:
                    __M_writer('                    ')
                    __M_writer(str(indent))
                    __M_writer('\n')
                __M_writer('                    <input type="checkbox" data-dojo-type="dijit/form/CheckBox" name="')
                __M_writer(str(fname))
                __M_writer('" id="" value="')
                __M_writer(str(k))
                __M_writer('" />\n                    ')
                __M_writer(str(v))
                __M_writer('\n                </td>\n            </tr>\n')
            else:
                __M_writer('            <tr>\n                <td style="width: 4%;">\n                    <input data-dojo-type="dijit/form/CheckBox" id="')
                __M_writer(str(k))
                __M_writer('_parent" type="checkbox" onclick="toggle_selection(\'')
                __M_writer(str(k))
                __M_writer("_parent', '#")
                __M_writer(str(k))
                __M_writer('_subitems\');" />\n                </td>\n                <td class="bg-info" data-toggle="collapse" data-target="#')
                __M_writer(str(k))
                __M_writer('_subitems">\n                    <b>')
                __M_writer(str(k))
                __M_writer('</b>\n                </td>\n            </tr>\n            <tr>\n                <td colspan="2">\n                    ')
                __M_writer(str(show_items(records=v, fname=fname, ignore_prefix=ignore_prefix, parent_key=k, indent=indent+'&nbsp;'*4)))
                __M_writer('\n                </td>\n            </tr>\n')
        __M_writer('    </table>\n    \n    \n')
        return ''
    finally:
        context.caller_stack._pop_frame()


"""
__M_BEGIN_METADATA
{"uri": "multi_selector.mako", "filename": "/MyWork/Projects/PyCK/pyck/mako_utils/templates/multi_selector.mako", "source_encoding": "utf8", "line_map": {"15": 0, "25": 46, "26": 60, "27": 60, "33": 1, "41": 1, "42": 2, "50": 8, "51": 9, "52": 9, "53": 9, "54": 9, "55": 10, "56": 12, "57": 12, "62": 15, "63": 17, "64": 18, "65": 20, "66": 21, "67": 21, "68": 21, "69": 23, "70": 23, "71": 23, "72": 23, "73": 23, "74": 24, "75": 24, "76": 27, "77": 28, "78": 30, "79": 30, "80": 30, "81": 30, "82": 30, "83": 30, "84": 32, "85": 32, "86": 33, "87": 33, "88": 38, "89": 38, "90": 43, "96": 90}}
__M_END_METADATA
"""
