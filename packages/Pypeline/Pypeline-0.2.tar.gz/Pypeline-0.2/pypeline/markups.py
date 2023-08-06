"""
Pypeline's built-in markups; use these as examples for how to create your
own markup functions.
"""


def creole_markup():
    import creoleparser
    return r'creole', lambda s: creoleparser.text2html(s)


def markdown_markup():
    import markdown
    return r'md|mkdn?|mdown|markdown', lambda s: markdown.markdown(s, safe_mode="escape")


def textile_markup():
    import textile
    return r'textile', lambda s: textile.textile_restricted(s, lite=False, noimage=False)


def rest_markup():
    from docutils.core import publish_parts
    from docutils.writers.html4css1 import Writer
    # render JS harmless through some monkeypatching ugliness
    # in plain links
    try:
        from docutils.utils import urischemes
    except ImportError:
        from docutils import urischemes  # Older versions of docutils

    del urischemes.schemes['javascript']
    # in explicit links
    import docutils.parsers.rst.states
    orig_adjust_uri = docutils.parsers.rst.states.Inliner.adjust_uri

    def adjust_uri(self, uri):
        uri = orig_adjust_uri(self, uri)
        uri = uri.replace('javascript:', 'javascript%3A')
        return uri

    docutils.parsers.rst.states.Inliner.adjust_uri = adjust_uri
    settings = dict(
        cloak_email_addresses=True,
        file_insertion_enabled=False,
        raw_enabled=False,
        strip_comments=True,
        doctitle_xform=False,
        report_level=5,
    )

    def render(s):
        parts = publish_parts(s, writer=Writer(), settings_overrides=settings)
        if 'html_body' in parts:
            html = parts['html_body']
            return html
        return ''
    return r're?st(\.txt)?', render
