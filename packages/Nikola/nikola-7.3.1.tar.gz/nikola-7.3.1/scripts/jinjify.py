#!/usr/bin/env python
import io
import glob
import sys
import os
import re
import json
import shutil

import colorama
import jinja2

dumb_replacements = [
    ["{% if any(post.is_mathjax for post in posts) %}", '{% if posts|selectattr("is_mathjax")|list %}'],
    ["json.dumps(title)", "title|tojson"],
    ["{{ parent.extra_head() }}", "{{ super() }}"],
    ["prefix='\\", "prefix='"],
    ["og: http://ogp.me/ns# \\", "og: http://ogp.me/ns#"],
    ["article: http://ogp.me/ns/article# \\", "article: http://ogp.me/ns/article#"],
    ["fb: http://ogp.me/ns/fb# \\", "fb: http://ogp.me/ns/fb#"],
    ['dir="rtl" \\', 'dir="rtl"']
]

dumber_replacements = [
    ['<%! import json %>\n\n', ''],
    ["<html\n\\", "<html\n"],
    ["\n'\\\n", "\n'\n"],
    ["{% endif %}\n\\", "{% endif %}\n"]
]


def jinjify(in_theme, out_theme):
    """Convert in_theme into a jinja version and put it in out_theme"""

    in_templates_path = os.path.join(in_theme, "templates")
    out_templates_path = os.path.join(out_theme, "templates")
    try:
        os.makedirs(out_templates_path)
    except:
        pass
    lookup = jinja2.Environment()
    lookup.filters['tojson'] = json.dumps
    lookup.loader = jinja2.FileSystemLoader([out_templates_path], encoding='utf-8')
    for template in glob.glob(os.path.join(in_templates_path, "*.tmpl")):
        out_template = os.path.join(out_templates_path, os.path.basename(template))
        with io.open(template, "r", encoding="utf-8") as inf:
            data = mako2jinja(inf)

        lines = []
        for line in data.splitlines():
            for repl in dumb_replacements:
                line = line.replace(*repl)
            lines.append(line)
        data = '\n'.join(lines)

        for repl in dumber_replacements:
            data = data.replace(*repl)

        with io.open(out_template, "w+", encoding="utf-8") as outf:
            outf.write(data + '\n')

        # Syntax check output
        source, filename = lookup.loader.get_source(lookup, os.path.basename(template))[:2]
        try:
            lookup.parse(source)
        except Exception as e:
            error("Syntax error in {0}:{1}".format(out_template, e.lineno))

    parent = os.path.basename(in_theme.rstrip('/'))
    child = os.path.basename(out_theme.rstrip('/'))
    mappings = {
        'base-jinja': 'base',
        'bootstrap-jinja': 'base-jinja',
        'bootstrap3-jinja': 'bootstrap-jinja',
    }

    if child in mappings:
        parent = mappings[child]

    with open(os.path.join(out_theme, "parent"), "wb+") as outf:
        outf.write(parent + '\n')

    with open(os.path.join(out_theme, "engine"), "wb+") as outf:
        outf.write("jinja\n")

    # Copy assets
    # shutil.rmtree(os.path.join(out_theme, "assets"))
    # shutil.copytree(os.path.join(in_theme, "assets"), os.path.join(out_theme, "assets"))

    # Copy bundles
    # shutil.copy(os.path.join(in_theme, "bundles"), os.path.join(out_theme, "bundles"))

    # Copy README
    if os.path.isfile(os.path.join(in_theme, "README.md")):
        shutil.copy(os.path.join(in_theme, "README.md"), os.path.join(out_theme, "README.md"))


def error(msg):
    print(colorama.Fore.RED + "ERROR:" + msg)


def mako2jinja(input_file):

    output = ''

    # TODO: OMG, this code is so horrible. Look at it; just look at it:

    macro_start = re.compile(r'(.*)<%.*def name="(.*?)".*>(.*)', re.IGNORECASE)
    macro_end = re.compile(r'(.*)</%def>(.*)', re.IGNORECASE)

    if_start = re.compile(r'(.*)% *if (.*):(.*)', re.IGNORECASE)
    if_else = re.compile(r'(.*)% *else.*:(.*)', re.IGNORECASE)
    if_elif = re.compile(r'(.*)% *elif (.*):(.*)', re.IGNORECASE)
    if_end = re.compile(r'(.*)% *endif(.*)', re.IGNORECASE)

    for_start = re.compile(r'(.*)% *for (.*):(.*)', re.IGNORECASE)
    for_end = re.compile(r'(.*)% *endfor(.*)', re.IGNORECASE)

    namespace = re.compile(r'(.*)<% *namespace name="(.*?)".* file="(.*?)".*/>(.*)', re.IGNORECASE)
    inherit = re.compile(r'(.*)<% *inherit file="(.*?)".*/>(.*)', re.IGNORECASE)

    block_single_line = re.compile(r'(.*)<% *block.*name="(.*?)".*>(.*)</% *block>(.*)', re.IGNORECASE)
    block_start = re.compile(r'(.*)<% *block.*name="(.*?)".*>(.*)', re.IGNORECASE)
    block_end = re.compile(r'(.*)</%block>(.*)', re.IGNORECASE)

    val = re.compile(r'\$\{(.*?)\}', re.IGNORECASE)
    func_len = re.compile(r'len\((.*?)\)', re.IGNORECASE)
    filter_h = re.compile(r'\|h', re.IGNORECASE)
    filter_striphtml = re.compile(r'\|striphtml', re.IGNORECASE)
    filter_u = re.compile(r'\|u', re.IGNORECASE)

    comment_single_line = re.compile(r'^.*##(.*?)$', re.IGNORECASE)

    for line in input_file:

        # Process line for repeated inline replacements
        m_val = val.search(line)
        m_func_len = func_len.search(line)
        m_filter_h = filter_h.search(line)
        m_filter_striphtml = filter_striphtml.search(line)
        m_filter_u = filter_u.search(line)

        if m_val:
            line = val.sub(r'{{ \1 }}', line)

        if m_filter_h:
            line = filter_h.sub(r'|e', line)

        if m_filter_striphtml:
            line = filter_striphtml.sub(r'|e', line)

        if m_filter_u:
            line = filter_u.sub(r'|urlencode', line)

        if m_func_len:
            line = func_len.sub(r'\1|length', line)

        # Process line for single 'whole line' replacements
        m_macro_start = macro_start.search(line)
        m_macro_end = macro_end.search(line)
        m_if_start = if_start.search(line)
        m_if_else = if_else.search(line)
        m_if_elif = if_elif.search(line)
        m_if_end = if_end.search(line)
        m_for_start = for_start.search(line)
        m_for_end = for_end.search(line)
        m_namspace = namespace.search(line)
        m_inherit = inherit.search(line)
        m_block_single_line = block_single_line.search(line)
        m_block_start = block_start.search(line)
        m_block_end = block_end.search(line)

        m_comment_single_line = comment_single_line.search(line)

        if m_comment_single_line:
            output += m_comment_single_line.expand(r'{# \1 #}') + '\n'

        elif m_macro_start:
            output += m_macro_start.expand(r'\1{% macro \2 %}\3') + '\n'
        elif m_macro_end:
            output += m_macro_end.expand(r'\1{% endmacro %}\1') + '\n'

        elif m_if_start:
            output += m_if_start.expand(r'\1{% if \2 %}\3') + '\n'
        elif m_if_else:
            output += m_if_else.expand(r'\1{% else %}\2') + '\n'
        elif m_if_elif:
            output += m_if_elif.expand(r'\1{% elif \2 %}\3') + '\n'
        elif m_if_end:
            output += m_if_end.expand(r'\1{% endif %}\2') + '\n'

        elif m_for_start:
            output += m_for_start.expand(r'\1{% for \2 %}\3') + '\n'
        elif m_for_end:
            output += m_for_end.expand(r'\1{% endfor %}\2') + '\n'

        elif m_namspace:
            output += m_namspace.expand(r"\1{% import '\3' as \2 with context %}\4") + '\n'
        elif m_inherit:
            output += m_inherit.expand(r"{% extends '\2' %}\3") + '\n'

        elif m_block_single_line:
            output += m_block_single_line.expand(r'\1{% block \2 %}\3{% endblock %}\4') + '\n'
        elif m_block_start:
            output += m_block_start.expand(r'\1{% block \2 %}\3') + '\n'
        elif m_block_end:
            output += m_block_end.expand(r'\1{% endblock %}\2') + '\n'

        else:
            # Doesn't match anything we're going to process, pass though
            output += line

    return output

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print('Performing standard conversions:')
        for m, j in (
            ('nikola/data/themes/base', 'nikola/data/themes/base-jinja'),
            ('nikola/data/themes/bootstrap', 'nikola/data/themes/bootstrap-jinja'),
            ('nikola/data/themes/bootstrap3', 'nikola/data/themes/bootstrap3-jinja')
        ):
            print('    {0} -> {1}'.format(m, j))
            jinjify(m, j)
    elif len(sys.argv) != 3:
        print('ERROR: needs input and output directory, or no arguments for default conversions.')
    else:
        jinjify(sys.argv[1], sys.argv[2])
