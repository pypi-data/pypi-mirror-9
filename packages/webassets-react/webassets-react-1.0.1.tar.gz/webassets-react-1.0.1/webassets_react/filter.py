from webassets.filter import Filter
from react.jsx import JSXTransformer


class React(Filter):
    name = 'react'

    def output(self, _in, out, **kw):
        content = _in.read()
        transformer = JSXTransformer()
        js = transformer.transform_string(content)
        out.write(js)


