from docutils import nodes
from sphinx.domains.python import PyXRefRole


URL_DIRECTIVES = {'url'}
PY_DIRECTIVES = {'class', 'function'}


def setup(app):
    """Install the plugin.

    :param app: Sphinx application context.
    """
    app.add_role('map', mapping_role)
    app.add_config_value('xref_mapping_dict', None, 'env')


def mapping_role(name, rawtext, text, lineno, inliner,
                 options={}, content=[]):
    # Get the dictionary set in the conf.py
    # eg.
    #     xref_mapping_dict = { 'key':  ('class', 'full.package.key'),
    #                           'key2': ('url',   'http://myurl.com') }
    map = inliner.document.settings.env.app.config.xref_mapping_dict

    # If the 'key' exists in our mapping, that map it
    if text in map:
        role_type, mapping_data = map[text]
        if is_py_directive(role_type):
            return parse_py_directive(role_type, text, mapping_data, lineno,
                                      inliner, options, content)
        elif is_url_directive(role_type):
            return parse_url_directive(text, mapping_data)
        else:  # Unsupported directive
            msg = inliner.reporter.error(
                '[sphinxmapxrefrole] - Unsupported directive {} for {}'.format(
                    role_type, text),
                line=lineno)
            prb = inliner.problematic(rawtext, rawtext, msg)
            return [prb], [msg]
    else:  # Unknown key
        msg = inliner.reporter.error(
            '[sphinxmapxrefrole] - Failed to find mapping for {}'.format(text),
            line=lineno)
        prb = inliner.problematic(rawtext, rawtext, msg)
        return [prb], [msg]


def is_py_directive(role_type):
    return role_type in PY_DIRECTIVES


def is_url_directive(role_type):
    return role_type in URL_DIRECTIVES


def parse_py_directive(role_type, text, full_package, lineno, inliner, options,
                       content):
    # Replace the text with the correct 'pretty' syntax
    new_text = '{} <{}>'.format(text, full_package)
    # Turn this in to a proper sphinx declaration
    new_rawtext = ':{}:`{}`'.format(role_type, new_text)

    # Return a python x-reference
    py_xref = PyXRefRole()
    return py_xref('py:' + role_type, new_rawtext, new_text, lineno,
                   inliner, options=options, content=content)


def parse_url_directive(target, url):
    return [nodes.reference(target, target, refuri=url)], []
