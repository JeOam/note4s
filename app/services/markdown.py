# -*- coding: utf-8 -*-

"""
    from mistune_contrib.highlight
    ~~~~~~~~~~~~~~~~~~~~~~~~~
    Support highlight code features for mistune.
    :copyright: (c) 2014 - 2015 by Hsiaoming Yang.
"""
import mistune
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters.html import HtmlFormatter

"""
https://github.com/lepture/mistune
https://github.com/richleland/pygments-css
https://gist.github.com/JeOam/90fd86fcdd824b06f297
"""

def block_code(text, lang, inlinestyles=False, linenos=False):
    if not lang:
        text = text.strip()
        return u'<pre><code>%s</code></pre>\n' % mistune.escape(text)

    try:
        lexer = get_lexer_by_name(lang, stripall=True)
        formatter = HtmlFormatter(
            noclasses=inlinestyles, linenos=linenos
        )
        code = highlight(text, lexer, formatter)
        if linenos:
            return '<div class="highlight-wrapper">%s</div>\n' % code
        return code
    except:
        return '<pre class="%s"><code>%s</code></pre>\n' % (
            lang, mistune.escape(text)
        )


class HighlightMixin(object):
    def block_code(self, text, lang):
        # renderer has an options
        inlinestyles = self.options.get('inlinestyles')
        linenos = self.options.get('linenos')
        return block_code(text, lang, inlinestyles, linenos)


class TocMixin(object):
    """TOC mixin for Renderer, mix this with Renderer::
        class TocRenderer(TocMixin, Renderer):
            pass
        toc = TocRenderer()
        md = mistune.Markdown(renderer=toc)
        # required in this order
        toc.reset_toc()          # initial the status
        md.parse(text)           # parse for headers
        toc.render_toc(level=3)  # render TOC HTML
    """

    def reset_toc(self):
        self.toc_tree = []
        self.toc_count = 0

    def header(self, text, level, raw=None):
        if level == 2:
            rv = '<h%d id="toc-%d">%s</h%d>\n' % (
                level, self.toc_count, text, level
            )
            self.toc_count += 1
        else:
            rv = '<h%d>%s</h%d>\n' % (
                level, text, level
            )

        self.toc_tree.append((self.toc_count, text, level, raw))
        return rv

    def render_toc(self, level=3):
        """Render TOC to HTML.
        :param level: render toc to the given level
        """
        return ''.join(self._iter_toc(level))

    def _iter_toc(self, level):
        first_level = None
        last_level = None

        yield '<ul id="table-of-content">\n'

        for toc in self.toc_tree:
            index, text, l, raw = toc

            if l > level:
                # ignore this level
                continue

            if first_level is None:
                # based on first level
                first_level = l
                last_level = l
                yield '<li><a href="#toc-%d">%s</a>' % (index, text)
            elif last_level == l:
                yield '</li>\n<li><a href="#toc-%d">%s</a>' % (index, text)
            elif last_level == l - 1:
                last_level = l
                yield '<ul>\n<li><a href="#toc-%d">%s</a>' % (index, text)
            elif last_level > l:
                # close indention
                yield '</li>'
                while last_level > l:
                    yield '</ul>\n</li>\n'
                    last_level -= 1
                yield '<li><a href="#toc-%d">%s</a>' % (index, text)

        # close tags
        yield '</li>\n'
        while last_level > first_level:
            yield '</ul>\n</li>\n'
            last_level -= 1

        yield '</ul>\n'


class HighlightRenderer(HighlightMixin, TocMixin, mistune.Renderer):
    pass

renderer = HighlightRenderer(linenos=False, inlinestyles=False)
markdown = mistune.Markdown(escape=True, renderer=renderer)
