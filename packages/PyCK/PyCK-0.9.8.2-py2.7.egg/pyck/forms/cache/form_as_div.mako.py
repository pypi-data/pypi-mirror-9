# -*- coding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 10
_modified_time = 1407878701.64686
_enable_loop = True
_template_filename = '/MyWork/Projects/PyCK/pyck/forms/templates/form_as_div.mako'
_template_uri = 'form_as_div.mako'
_source_encoding = 'utf-8'
_exports = []


def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        form = context.get('form', UNDEFINED)
        __M_writer = context.writer()
        if form._use_csrf_protection:
            __M_writer('<input type="hidden" name="csrf_token" value="')
            __M_writer(str(form._csrf_token))
            __M_writer('" />\n')
        if '_csrf' in form.errors:
            __M_writer('<div class="danger">')
            __M_writer(str(form.errors['_csrf'][0]))
            __M_writer('</div><br />\n')
        for field in form:

            field_errors = ''
            if field.errors:
                field_errors = '<span class="danger">'
                for e in field.errors:
                    field_errors += e + ', '
                
                field_errors = field_errors[:-2] + '</span>'
            
            
            __M_locals_builtin_stored = __M_locals_builtin()
            __M_locals.update(__M_dict_builtin([(__M_key, __M_locals_builtin_stored[__M_key]) for __M_key in ['field_errors','e'] if __M_key in __M_locals_builtin_stored]))
            __M_writer('\n\n<div class="form-group">\n    <div class="col-sm-3">\n    ')
            __M_writer(str(field.label))
            __M_writer('    \n    </div>\n    \n    <div class="col-sm-9">\n      ')
            __M_writer(str(field(class_="form-control")))
            __M_writer('\n    </div>\n</div>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


"""
__M_BEGIN_METADATA
{"source_encoding": "utf-8", "line_map": {"42": 17, "43": 21, "44": 21, "45": 25, "46": 25, "15": 0, "52": 46, "21": 2, "22": 3, "23": 3, "24": 3, "25": 5, "26": 6, "27": 6, "28": 6, "29": 8, "30": 9}, "uri": "form_as_div.mako", "filename": "/MyWork/Projects/PyCK/pyck/forms/templates/form_as_div.mako"}
__M_END_METADATA
"""
