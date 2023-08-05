import os
from docutils import nodes
from dot_parser import parse_dot_data


def closed_dotgraphdirective(build):
    'Close the directive with the build directory'
    def DotgraphDirective(name, arguments, options, content, *args):
        graph = parse_dot_data('\n'.join(content))
        href = arguments[0]
        buildpath = build + href
        basedir = os.path.dirname(buildpath)
        if not os.path.exists(basedir):
            os.makedirs(basedir)
        graph.write_svg(buildpath)
        print("Writing graph to: {0}".format(buildpath))
        html = '<img src="{0}" class="dot-graph" />'.format(href)
        return [nodes.raw('', html, format='html')]
    DotgraphDirective.arguments = (1, 0, 1)
    DotgraphDirective.content = 1
    return DotgraphDirective
