# -*- coding: utf-8 -*-

# Copyright © 2012-2015 Roberto Alsina and others.

# Permission is hereby granted, free of charge, to any
# person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the
# Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the
# Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice
# shall be included in all copies or substantial portions of
# the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
# OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from __future__ import unicode_literals, print_function

import sys
import os

from pygments import highlight
from pygments.lexers import get_lexer_for_filename, TextLexer
import natsort

from nikola.plugin_categories import Task
from nikola import utils


class Listings(Task):
    """Render pretty listings."""

    name = "render_listings"

    def register_output_name(self, input_folder, rel_name, rel_output_name):
        """Register proper and improper file mappings."""
        if rel_name not in self.improper_input_file_mapping:
            self.improper_input_file_mapping[rel_name] = []
        self.improper_input_file_mapping[rel_name].append(rel_output_name)
        self.proper_input_file_mapping[os.path.join(input_folder, rel_name)] = rel_output_name
        self.proper_input_file_mapping[rel_output_name] = rel_output_name

    def set_site(self, site):
        site.register_path_handler('listing', self.listing_path)

        # We need to prepare some things for the listings path handler to work.

        self.kw = {
            "default_lang": site.config["DEFAULT_LANG"],
            "listings_folders": site.config["LISTINGS_FOLDERS"],
            "output_folder": site.config["OUTPUT_FOLDER"],
            "index_file": site.config["INDEX_FILE"],
            "strip_indexes": site.config['STRIP_INDEXES'],
            "filters": site.config["FILTERS"],
        }

        # Verify that no folder in LISTINGS_FOLDERS appears twice (on output side)
        appearing_paths = set()
        for source, dest in self.kw['listings_folders'].items():
            if source in appearing_paths or dest in appearing_paths:
                problem = source if source in appearing_paths else dest
                utils.LOGGER.error("The listings input or output folder '{0}' appears in more than one entry in LISTINGS_FOLDERS, exiting.".format(problem))
                sys.exit(1)
            appearing_paths.add(source)
            appearing_paths.add(dest)

        # improper_input_file_mapping maps a relative input file (relative to
        # its corresponding input directory) to a list of the output files.
        # Since several input directories can contain files of the same name,
        # a list is needed. This is needed for compatibility to previous Nikola
        # versions, where there was no need to specify the input directory name
        # when asking for a link via site.link('listing', ...).
        self.improper_input_file_mapping = {}

        # proper_input_file_mapping maps relative input file (relative to CWD)
        # to a generated output file. Since we don't allow an input directory
        # to appear more than once in LISTINGS_FOLDERS, we can map directly to
        # a file name (and not a list of files).
        self.proper_input_file_mapping = {}

        for input_folder, output_folder in self.kw['listings_folders'].items():
            for root, dirs, files in os.walk(input_folder, followlinks=True):
                # Compute relative path; can't use os.path.relpath() here as it returns "." instead of ""
                rel_path = root[len(input_folder):]
                if rel_path[:1] == os.sep:
                    rel_path = rel_path[1:]

                for f in files + [self.kw['index_file']]:
                    rel_name = os.path.join(rel_path, f)
                    rel_output_name = os.path.join(output_folder, rel_path, f)
                    # Register file names in the mapping.
                    self.register_output_name(input_folder, rel_name, rel_output_name)

        return super(Listings, self).set_site(site)

    def gen_tasks(self):
        """Render pretty code listings."""

        # Things to ignore in listings
        ignored_extensions = (".pyc", ".pyo")

        def render_listing(in_name, out_name, input_folder, output_folder, folders=[], files=[]):
            if in_name:
                with open(in_name, 'r') as fd:
                    try:
                        lexer = get_lexer_for_filename(in_name)
                    except:
                        lexer = TextLexer()
                    code = highlight(fd.read(), lexer, utils.NikolaPygmentsHTML(in_name))
                title = os.path.basename(in_name)
            else:
                code = ''
                title = os.path.split(os.path.dirname(out_name))[1]
            crumbs = utils.get_crumbs(os.path.relpath(out_name,
                                                      self.kw['output_folder']),
                                      is_file=True)
            permalink = self.site.link(
                'listing',
                os.path.join(
                    input_folder,
                    os.path.relpath(
                        out_name[:-5],  # remove '.html'
                        os.path.join(
                            self.kw['output_folder'],
                            output_folder))))
            if self.site.config['COPY_SOURCES']:
                source_link = permalink[:-5]  # remove '.html'
            else:
                source_link = None
            context = {
                'code': code,
                'title': title,
                'crumbs': crumbs,
                'permalink': permalink,
                'lang': self.kw['default_lang'],
                'folders': natsort.natsorted(
                    folders, alg=natsort.ns.F | natsort.ns.IC),
                'files': natsort.natsorted(
                    files, alg=natsort.ns.F | natsort.ns.IC),
                'description': title,
                'source_link': source_link,
            }
            self.site.render_template('listing.tmpl', out_name, context)

        yield self.group_task()

        template_deps = self.site.template_system.template_deps('listing.tmpl')

        for input_folder, output_folder in self.kw['listings_folders'].items():
            for root, dirs, files in os.walk(input_folder, followlinks=True):
                files = [f for f in files if os.path.splitext(f)[-1] not in ignored_extensions]

                uptodate = {'c': self.site.GLOBAL_CONTEXT}

                for k, v in self.site.GLOBAL_CONTEXT['template_hooks'].items():
                    uptodate['||template_hooks|{0}||'.format(k)] = v._items

                for k in self.site._GLOBAL_CONTEXT_TRANSLATABLE:
                    uptodate[k] = self.site.GLOBAL_CONTEXT[k](self.kw['default_lang'])

                # save navigation links as dependencies
                uptodate['navigation_links'] = uptodate['c']['navigation_links'](self.kw['default_lang'])

                uptodate['kw'] = self.kw

                uptodate2 = uptodate.copy()
                uptodate2['f'] = files
                uptodate2['d'] = dirs

                # Compute relative path; can't use os.path.relpath() here as it returns "." instead of ""
                rel_path = root[len(input_folder):]
                if rel_path[:1] == os.sep:
                    rel_path = rel_path[1:]

                rel_name = os.path.join(rel_path, self.kw['index_file'])
                rel_output_name = os.path.join(output_folder, rel_path, self.kw['index_file'])

                # Render all files
                out_name = os.path.join(self.kw['output_folder'], rel_output_name)
                yield utils.apply_filters({
                    'basename': self.name,
                    'name': out_name,
                    'file_dep': template_deps,
                    'targets': [out_name],
                    'actions': [(render_listing, [None, out_name, input_folder, output_folder, dirs, files])],
                    # This is necessary to reflect changes in blog title,
                    # sidebar links, etc.
                    'uptodate': [utils.config_changed(uptodate2, 'nikola.plugins.task.listings:folder')],
                    'clean': True,
                }, self.kw["filters"])
                for f in files:
                    ext = os.path.splitext(f)[-1]
                    if ext in ignored_extensions:
                        continue
                    in_name = os.path.join(root, f)
                    # Record file names
                    rel_name = os.path.join(rel_path, f + '.html')
                    rel_output_name = os.path.join(output_folder, rel_path, f + '.html')
                    self.register_output_name(input_folder, rel_name, rel_output_name)
                    # Set up output name
                    out_name = os.path.join(self.kw['output_folder'], rel_output_name)
                    # Yield task
                    yield utils.apply_filters({
                        'basename': self.name,
                        'name': out_name,
                        'file_dep': template_deps + [in_name],
                        'targets': [out_name],
                        'actions': [(render_listing, [in_name, out_name, input_folder, output_folder])],
                        # This is necessary to reflect changes in blog title,
                        # sidebar links, etc.
                        'uptodate': [utils.config_changed(uptodate, 'nikola.plugins.task.listings:source')],
                        'clean': True,
                    }, self.kw["filters"])
                    if self.site.config['COPY_SOURCES']:
                        rel_name = os.path.join(rel_path, f)
                        rel_output_name = os.path.join(output_folder, rel_path, f)
                        self.register_output_name(input_folder, rel_name, rel_output_name)
                        out_name = os.path.join(self.kw['output_folder'], rel_output_name)
                        yield utils.apply_filters({
                            'basename': self.name,
                            'name': out_name,
                            'file_dep': [in_name],
                            'targets': [out_name],
                            'actions': [(utils.copy_file, [in_name, out_name])],
                            'clean': True,
                        }, self.kw["filters"])

    def listing_path(self, namep, lang):
        nameh = namep + '.html'
        for name in (namep, nameh):
            if name in self.proper_input_file_mapping:
                # If the name shows up in this dict, everything's fine.
                name = self.proper_input_file_mapping[name]
                break
            elif name in self.improper_input_file_mapping:
                # If the name shows up in this dict, we have to check for
                # ambiguities.
                if len(self.improper_input_file_mapping[name]) > 1:
                    utils.LOGGER.error("Using non-unique listing name '{0}', which maps to more than one listing name ({1})!".format(name, str(self.improper_input_file_mapping[name])))
                    sys.exit(1)
                if len(self.site.config['LISTINGS_FOLDERS']) > 1:
                    utils.LOGGER.notice("Using listings names in site.link() without input directory prefix while configuration's LISTINGS_FOLDERS has more than one entry.")
                name = self.improper_input_file_mapping[name][0]
                break
        else:
            utils.LOGGER.error("Unknown listing name {0}!".format(namep))
            sys.exit(1)
        if not name.endswith('/' + self.site.config["INDEX_FILE"]):
            name += '.html'
        path_parts = list(os.path.split(name))
        return [_f for _f in path_parts if _f]
