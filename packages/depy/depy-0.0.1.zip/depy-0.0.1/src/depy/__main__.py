import re
import sys

import pydot

from argparse import ArgumentParser
from fnmatch import fnmatch
from os import path, listdir, walk
from pprint import pprint


def find(directory, pattern):
    found = []
    for root, _, files in walk(directory):
        for filename in files:
            if fnmatch(filename, pattern):
                found.append(path.join(root, filename))

    return found


def cat(filenames):
    contents = []
    for filename in filenames:
        contents.append(open(filename, 'r', encoding='utf-8').read())

    return ''.join(contents)


def read_with_project_name(imported, project_name):
    splitted = imported.split('.')
    return ('.'.join(splitted[:2])
            if imported.startswith(project_name)
            else splitted[0])


def parse_with_regexp(regexp, what, project_name):
    raw = [re.search(regexp, x).group(1) for x in what]
    no_self = {x for x in raw if not x.startswith('.')}
    return {read_with_project_name(x, project_name) for x in no_self}


def parse_froms(froms, project_name):
    return parse_with_regexp('from (.*) import', froms, project_name)


def parse_imports(imports, project_name):
    return parse_with_regexp('import (.*)', imports, project_name)


def get_dependencies(text, project_name):
    import_statements = re.findall('^(?:import|from).*$', text, re.MULTILINE)
    imports = [stmt for stmt in import_statements if stmt.startswith('import')]
    froms = [stmt for stmt in import_statements if stmt.startswith('from')]
    deps = parse_froms(froms, project_name) | parse_imports(imports,
                                                            project_name)
    return deps


def get_deps_from_module(filename, project_name):
    return get_dependencies(open(filename, 'r', encoding='utf-8').read(),
                            project_name)


def get_deps_from_package(directory, project_name):
    text = cat(find(directory, '*.py'))
    return get_dependencies(text, project_name)


def is_module(directory):
    return path.exists(path.join(directory, '__init__.py'))


def dependency_graph(directory, project_name):
    base = path.basename(directory)

    graph = {}

    for submodule in listdir(directory):
        fullpath = path.join(directory, submodule)
        if path.isdir(fullpath) and is_module(fullpath):
            module_name = base + '.' + submodule
            deps = get_deps_from_package(fullpath, project_name)
            try:
                deps.remove(module_name)
            except KeyError:
                pass
            graph[module_name] = deps
        elif fullpath.endswith('.py'):
            name, _ = path.splitext(submodule)
            module_name = base + '.' + name
            deps = get_deps_from_module(fullpath, project_name)
            graph[module_name] = deps

    return graph


def draw_graph(graph, output):
    dotgraph = pydot.Dot(graph_type='digraph')

    for node, edges in graph.items():
        dotgraph.add_node(pydot.Node(node))
        for edge in edges:
            dotgraph.add_edge(pydot.Edge(node, edge))

    dotgraph.write(output, format='png')


def main(argv):
    argparser = ArgumentParser('depy')
    argparser.add_argument('directory')
    argparser.add_argument('project_name')
    argparser.add_argument('--draw', action='store_true')
    argparser.add_argument('--output', '-o', action='store')

    args = argparser.parse_args(argv)

    graph = dependency_graph(args.directory, args.project_name)

    if args.output:
        output = args.output
    else:
        output = args.project_name + '.png'

    if args.draw:
        draw_graph(graph, output)
    else:
        pprint(graph)


def run():
    main(sys.argv[1:])


if __name__ == '__main__':
    run()
