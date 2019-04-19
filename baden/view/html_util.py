from contextlib import contextmanager


@contextmanager
def div(code_list, params=""):
    code_list.append('<div {}>\n'.format(params))
    yield
    code_list.append('</div>\n')


@contextmanager
def table(code_list, params=""):
    code_list.append('<table {}>\n'.format(params))
    yield
    code_list.append('</table>\n')


@contextmanager
def thead(code_list, params=""):
    code_list.append('<thead {}>\n'.format(params))
    yield
    code_list.append('</thead>\n')


@contextmanager
def tbody(code_list, params=""):
    code_list.append('<tbody {}>\n'.format(params))
    yield
    code_list.append('</tbody>\n')


@contextmanager
def tr(code_list, params=""):
    code_list.append('<tr {}>\n'.format(params))
    yield
    code_list.append('</tr>\n')


@contextmanager
def th(code_list, scope, params=""):
    code_list.append('<th scope="{}" {}>'.format(scope, params))
    yield
    code_list.append('</th>')


@contextmanager
def td(code_list, params=""):
    code_list.append('<td {}>'.format(params))
    yield
    code_list.append('</td>')
