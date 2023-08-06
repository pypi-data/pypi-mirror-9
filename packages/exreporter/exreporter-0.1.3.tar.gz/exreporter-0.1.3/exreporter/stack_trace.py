# -*- coding: utf-8 -*-

import sys
import traceback


class StackTrace(object):

    def __init__(self):
        ex_type, ex_value, ex_trace = sys.exc_info()

        assert ex_type is not None,\
            'No exception occurred, cannot proceed without any exception'

        filepath, method_name, locals_data, lineno = self._get_trace_info(
            trace=ex_trace)

        self.filepath = filepath
        self.locals_data = locals_data
        self.method_name = method_name
        self.lineno = lineno
        self.exception = ex_type
        self.traceback = ex_trace
        self.exception_value = ex_value

    def _get_trace_info(self, trace):
        custom_module_data = []

        while trace:
            filepath = trace.tb_frame.f_code.co_filename
            method_name = trace.tb_frame.f_code.co_name
            locals_data = trace.tb_frame.f_locals
            lineno = trace.tb_frame.f_lineno

            if 'site-packages' not in filepath:
                custom_module_data.append(
                    {
                        'filepath': filepath,
                        'method_name': method_name,
                        'locals_data': locals_data,
                        'lineno': lineno
                    }
                )
            trace = trace.tb_next

        if custom_module_data:
            data = custom_module_data.pop(-1)
            return (data['filepath'], data['method_name'],
                    data['locals_data'], data['lineno'])
        else:
            return (filepath, method_name, locals_data, lineno)

    @property
    def stack_trace_text(self):
        return '\n'.join(traceback.format_exception(
            self.exception, self.exception_value, self.traceback))
