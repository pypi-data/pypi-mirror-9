# -*- coding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 10
_modified_time = 1407862340.456977
_enable_loop = True
_template_filename = '/MyWork/Projects/PyCK/pyck/forms/templates/form_as_p.mako'
_template_uri = 'form_as_p.mako'
_source_encoding = 'utf-8'
_exports = []


def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        errors_position = context.get('errors_position', UNDEFINED)
        labels_position = context.get('labels_position', UNDEFINED)
        form = context.get('form', UNDEFINED)
        __M_writer = context.writer()
        if form._use_csrf_protection:
            __M_writer('<input type="hidden" name="csrf_token" value="')
            __M_writer(str(form._csrf_token))
            __M_writer('" />\n')
        if '_csrf' in form.errors:
            __M_writer('<div class="errors">')
            __M_writer(str(form.errors['_csrf'][0]))
            __M_writer('</div><br />\n')
        for field in form:

            field_errors = ''
            if field.errors:
                field_errors = '<span class="errors">'
                for e in field.errors:
                    field_errors += e + ', '
                
                field_errors = field_errors[:-2] + '</span>'
            
            
            __M_locals_builtin_stored = __M_locals_builtin()
            __M_locals.update(__M_dict_builtin([(__M_key, __M_locals_builtin_stored[__M_key]) for __M_key in ['field_errors','e'] if __M_key in __M_locals_builtin_stored]))
            __M_writer('\n<p>\n')
            if 'top' == labels_position:
                __M_writer(str(field.label))
                __M_writer('<br /> ')
            if field_errors and 'top'==errors_position:
                __M_writer(str(field_errors))
                __M_writer('<br /> ')
            if 'left' == labels_position:
                __M_writer(str(field.label))
                __M_writer(' ')
            if field_errors and 'left'==errors_position:
                __M_writer(str(field_errors))
                __M_writer(' ')
            __M_writer(str(field))
            __M_writer(' ')
            if 'bottom' == labels_position:
                __M_writer('<br />')
                __M_writer(str(field.label))
                __M_writer(' ')
            if field_errors and 'bottom'==errors_position:
                __M_writer('<br />')
                __M_writer(str(field_errors))
                __M_writer(' ')
            if 'right' == labels_position:
                __M_writer(str(field.label))
                __M_writer(' ')
            if field_errors and 'right'==errors_position:
                __M_writer(str(field_errors))
                __M_writer(' ')
            __M_writer('</p>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


"""
__M_BEGIN_METADATA
{"source_encoding": "utf-8", "line_map": {"15": 0, "23": 2, "24": 3, "25": 3, "26": 3, "27": 5, "28": 6, "29": 6, "30": 6, "31": 8, "32": 9, "44": 17, "45": 19, "46": 20, "47": 20, "48": 23, "49": 24, "50": 24, "51": 27, "52": 28, "53": 28, "54": 31, "55": 32, "56": 32, "57": 35, "58": 35, "59": 37, "60": 38, "61": 38, "62": 38, "63": 41, "64": 42, "65": 42, "66": 42, "67": 45, "68": 46, "69": 46, "70": 49, "71": 50, "72": 50, "73": 52, "79": 73}, "uri": "form_as_p.mako", "filename": "/MyWork/Projects/PyCK/pyck/forms/templates/form_as_p.mako"}
__M_END_METADATA
"""
