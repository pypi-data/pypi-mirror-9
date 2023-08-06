# -*- coding: utf-8 -*-
#  Copyright 2014 Yassu 0320
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import os.path
from subprocess import Popen, PIPE
from shutil import rmtree
from errno import ENOENT
from tempfile import NamedTemporaryFile, mkdtemp
from blockdiag import plugins
from blockdiag.utils import unquote
from blockdiag.utils.images import get_image_size
from blockdiag.utils.logging import warning


X_PADDING, Y_PADDING = 10, 10

LATEX_SOURCE = r'''
\documentclass[12pt]{article}
\usepackage[utf8x]{inputenc}
%(preamble)s
%(usepackage)s
\pagestyle{empty}
\begin{document}
%(content)s
\end{document}
'''

tex_images = []


def get_latex_source(content, stylepackage, preamble):
    if stylepackage is not None:
        usepackage = '\\usepackage{%s}\n' % stylepackage
    else:
        usepackage = ''

    if preamble is None:
        preamble = ''

    return LATEX_SOURCE % {'content': content.strip(),
                           'preamble': preamble,
                           'usepackage': usepackage}


def create_tex_image(content, stylepackage, preamble, content_id):
    try:
        tmpdir = mkdtemp()

        # create source .tex file
        source = NamedTemporaryFile(mode='w+b', suffix='.tex',
                                    dir=tmpdir, delete=False)
        latex_source = get_latex_source(content, stylepackage, preamble)
        source.write(latex_source.encode('utf-8'))
        source.close()

        # execute latex
        try:
            # `-no-shell-escape` blocks to invoke any commands
            args = ['latex', '--interaction=nonstopmode',
                    '-no-shell-escape', source.name]
            latex = Popen(args, stdout=PIPE, stderr=PIPE, cwd=tmpdir)
            stdout, _ = latex.communicate()
            if latex.returncode != 0:
                warning("raise TeX Exception:\n\n%s" %
                        stdout.decode('utf-8'))
                return None
        except Exception as exc:
            if isinstance(exc, OSError) and exc.errno == ENOENT:
                error = 'latex command not found'
            else:
                error = exc

            warning("Fail to convert TeX: %s (reason: %s)" %
                    (content, error))
            return None

        # execute dvipng
        try:
            dvifile = source.name.replace('.tex', '.dvi')
            output = NamedTemporaryFile(suffix='.png')
            args = ['dvipng', '-gamma', '1.5',
                    '-D', '110', '-T', 'tight',
                    '-bg', 'Transparent', '-z0', dvifile,
                    '-o', output.name]
            dvipng = Popen(args, stdout=PIPE, stderr=PIPE, cwd=tmpdir)
            stdout, _ = dvipng.communicate()
            if latex.returncode != 0:
                warning("raise dvipng Exception:\n\n%s" %
                        stdout.decode('utf-8'))
                return None
        except Exception as exc:
            output.close()
            if isinstance(exc, OSError) and exc.errno == ENOENT:
                error = 'dvipng command not found'
            else:
                error = exc

            warning("Fail to convert TeX: (reason: %s) with node labeled %s" %
                    (error, content_id))
            return None

        return output
    finally:
        rmtree(tmpdir)


class TexImagePlugin(plugins.NodeHandler):
    def __init__(self, diagram, **kwargs):
        super(TexImagePlugin, self).__init__(diagram, **kwargs)
        self.stylepackage = None

        stylefile = kwargs.get('style')
        if stylefile:
            basedir = os.path.dirname(os.path.abspath(self.config.input))
            stylepath = os.path.join(basedir, stylefile)
            if os.path.exists(stylepath):
                # stylename exists on relative path from source file
                self.stylepackage = os.path.splitext(stylepath)[0]
            else:
                warning('stylefile not found: %s' % stylefile)

        self.preamble = kwargs.get('preamble')

    def on_created(self, node):
        node.resizable = False

    def on_attr_changing(self, node, attr):
        value = unquote(attr.value)

        if attr.name == 'background':
            return self.on_background_changing(node, value)
        elif attr.name == 'resizable':
            return self.on_resizable_changing(node, value)
        elif attr.name == 'label':
            return self.on_label_changing(node, value)
        else:
            return True

    def on_label_changing(self, node, value):
        if not value.startswith('tex://'):
            return False

        if getattr(node, 'uses_tex_image', False):
            warning('tex has already been specified: %s' % value)
            return False

        value = value.split('://', 1)[1]
        node.label = ""
        return self.set_tex_image_to_background(node, value)

    def on_resizable_changing(self, node, value):
        if value.lower() not in ('true', 'false'):
            warning('%s is not boolean value. ignored.' % value)

        if value.lower() == 'true':
            node.resizable = True
        else:
            node.resizable = False

        return False

    def on_build_finished(self, node):
        uses_tex_image = getattr(node, 'uses_tex_image', False)
        if uses_tex_image is not None and node.background is not None and node.resizable is True:
            node.width, node.height = get_image_size(node.background.name)
            node.width += 2 * X_PADDING     # top and bottom
            node.height += 2 * Y_PADDING    # left and right

    def set_tex_image_to_background(self, node, value):
        content = value
        image = create_tex_image(content, self.stylepackage,
                                 self.preamble, node.id)
        if image is not None:
            tex_images.append(image)
            node.background = image
            node.uses_tex_image = True
        else:
            node.background = None

        return False


def on_cleanup():
    for image in tex_images[:]:
        image.close()
        tex_images.remove(image)


def setup(self, diagram, **kwargs):
    plugins.install_node_handler(TexImagePlugin(diagram, **kwargs))
    plugins.install_general_handler('cleanup', on_cleanup)
