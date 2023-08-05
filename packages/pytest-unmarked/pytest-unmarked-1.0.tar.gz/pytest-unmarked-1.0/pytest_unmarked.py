from _pytest.mark import matchmark
import pytest
import py


def pytest_addoption(parser):
    group = parser.getgroup('Unmarked', 'Unmarked')
    group._addoption('--unmarked',
                     action="store_true", dest="unmarked", default=False,
                     help="Run unmarked tests.")


def pytest_collection_modifyitems(items, config):
    if (not pytest.config.option.unmarked):
        return

    matchexpr = ''
    for line in config.getini("markers"):
        names, rest = line.split(":", 1)
        if '(' in names:
            paren = names.find("(")
            names = names[:paren]
        matchexpr = matchexpr + names + ' or '

    matchexpr = matchexpr[:-4]
    if not matchexpr:
        return

    remaining = []
    deselected = []
    for colitem in items:
        if matchexpr:
            if matchmark(colitem, matchexpr):
                deselected.append(colitem)
                continue
        remaining.append(colitem)

    if deselected:
        config.hook.pytest_deselected(items=list(set(deselected) - set(remaining)))
        items[:] = remaining
