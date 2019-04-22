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


@contextmanager
def a(code_list, url, params=""):
    code_list.append('<a href={} {}>\n'.format(url, params))
    yield
    code_list.append('</a>\n')


@contextmanager
def h(indice, code_list, params=""):
    code_list.append('<h{} {}>\n'.format(indice, params))
    yield
    code_list.append('</h{}>\n'.format(indice))


def show(page_code, dom_id):
    return page_code.replace('id="{}" style="display: none;"'.format(dom_id), 'id="{}"'.format(dom_id))


def hide(page_code, dom_id):
    return page_code.replace('id="{}"'.format(dom_id), 'id="{}" style="display: none;"'.format(dom_id))

