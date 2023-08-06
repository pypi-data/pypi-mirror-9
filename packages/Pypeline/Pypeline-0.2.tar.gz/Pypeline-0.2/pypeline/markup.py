import cgi
import re
from types import FunctionType

class Markup(object):
    
    def __init__(self, *markup_pkgs_or_fns):
        # Define markups
        self.markups = []
        for markup_pkg in markup_pkgs_or_fns:
            if type(markup_pkg) == FunctionType:
                self.add_renderer(markup_pkg)
            else:
                renderers = [r for r in dir(markup_pkg) if r.endswith('_markup')]
                for renderer in renderers:
                    func = getattr(markup_pkg, renderer)
                    self.add_renderer(func)
    
    def add_renderer(self, func):
        '''
        Add a function that is responsible for rendering a particular
        markup syntax to HTML.
        
        The function name should end in \*_markup. The
        function must return a tuple of the pattern used to match supported
        file extensions and a callback to render a string of text.
        
        The callback recieves one parameter, a Unicode string. It should
        return an HTML representation of that string. Simple callbacks can be
        lambdas, such as creole, textile, or markup.
        '''
        ext_pattern, render_fn = func()
        name = func.__name__[:-len('_markup')]
        self.markups.append(dict(name = name,
                                 ext_pattern = ext_pattern,
                                 render_fn = render_fn,
                            ))

    def render(self, filename, content=None):
        '''
        Provided a filename or a filename and content, render the
        content from a particular markup syntax to HTML. The markup
        syntax is chosen based on matching patterns (e.g., extensions)
        with the filename.
        '''
        if not content:
            with open(filename, 'r') as f:
                content = f.read()
        content = self.unicode(content)
        (proc, name) = self.renderer(filename)
        if proc:
            return self.unicode(proc(content))
        else:
            # make sure unrendered content is at least escaped
            return cgi.escape(content)

    def unicode(self, content):
        '''
        Normalize a variety of encodings into unicode.
        '''
        if type(content) == unicode:
            return content
        try:
            content.decode('ascii')
        except UnicodeDecodeError: #pragma: nocover
            # try 2 common encodings
            try:
                content = content.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    content = content.decode('latin_1')
                except UnicodeDecodeError:
                    raise Exception('The content uses an unsupported encoding.')
        return unicode(content)

    def can_render(self, filename):
        '''
        Check to see if a particular file is supported. If the file is
        supported, the name of the markup is returned. Otherwise, the
        function returns None.
        '''
        (proc, name) = self.renderer(filename)
        return name

    def renderer(self, filename):
        '''
        Search for any markups that are responsible for the provided
        filename. Returns the function used to render the file and
        the name of the markup.
        '''
        for markup in self.markups:
            if re.search(r"\.(%s)$" % markup['ext_pattern'], filename):
                return markup['render_fn'], markup['name']
        return None, None

from pypeline import markups
markup = Markup(markups)