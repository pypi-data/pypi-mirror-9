#!/usr/bin/env python3

# Copyright 2014 Louis Paternault
#
# This file is part of Jouets.
#
# Jouets is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Jouets is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Jouets.  If not, see <http://www.gnu.org/licenses/>.

"""
    TODO Update comments and documentation

    sphinx.ext.todo
    ~~~~~~~~~~~~~~~

    Allow todos to be inserted into your documentation.  Inclusion of todos can
    be switched of by a configuration variable.  The todolist directive collects
    all todos of your project and lists them along with a backlink to the
    original location.

    :copyright: Copyright 2007-2014 by the Sphinx team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

from docutils import nodes
from docutils.parsers.rst import directives

from sphinx.locale import _
from sphinx.environment import NoUri
from sphinx.util.nodes import set_source_info
from sphinx.util.compat import Directive, make_admonition

class proof_node(nodes.General, nodes.Element): pass
class proof_title_node(nodes.Part, nodes.Element): pass
class proof_title_name_node(nodes.Part, nodes.Element): pass
class proof_title_content_node(nodes.Part, nodes.Element): pass
class proof_content_node(nodes.General, nodes.Element): pass
#class todolist(nodes.General, nodes.Element): pass

HUMAN = {
        'property': "Propriété",
        'example': "Exemple",
        'theorem': "Théorème",
        'definition': "Définition",
        'proof': "Preuve",
        'conjecture': "Conjecture",
        'algorithm': "Algorithme",
        }


def create_environment_class(name):

    class Environment(Directive):
        """
        TODO A todo entry, displayed (if configured) in the form of an admonition.
        """

        has_content = True
        required_arguments = 0
        optional_arguments = 1
        final_argument_whitespace = True
        option_spec = {
                'label': directives.unchanged_required,
                }

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.name = name

        def run(self):
            env = self.state.document.settings.env
            targetid = 'index-%s' % env.new_serialno('index')
            targetnode = nodes.target('', '', ids=[targetid])

            node = proof_node('\n'.join(self.content))

            # Title
            title_node = proof_title_node()
            title_node['classes'] += ['proof-title']

            # Element type (property, definition, etc.)
            textnodes, messages = self.state.inline_text(HUMAN[self.name], self.lineno)
            title_name_node = proof_title_name_node(HUMAN[self.name], *textnodes)
            title_name_node['classes'] += ['proof-title-name']
            title_node += title_name_node
            node += messages

            # Element title (if relevant)
            if self.arguments:
                textnodes, messages = self.state.inline_text(self.arguments[0], self.lineno)
                title_content_node = proof_title_content_node(self.arguments[0], *textnodes)
                title_content_node['classes'] += ['proof-title-content']
                title_node += title_content_node
                node += messages

            node += title_node
            node['classes'] += ['proof', 'proof-type-{}'.format(self.name)]

            content = proof_content_node()
            self.state.nested_parse(self.content, self.content_offset, content)
            content['classes'] += ['proof-content']
            node += content

            set_source_info(self, node)
            return [targetnode, node]

    return Environment


def process_todos(app, doctree):
    # collect all todos in the environment
    # this is not done in the directive itself because it some transformations
    # must have already been run, e.g. substitutions
    env = app.builder.env
    if not hasattr(env, 'todo_all_todos'):
        env.todo_all_todos = []
    for node in doctree.traverse(proof_node):
        try:
            targetnode = node.parent[node.parent.index(node) - 1]
            if not isinstance(targetnode, nodes.target):
                raise IndexError
        except IndexError:
            targetnode = None
        newnode = node.deepcopy()
        del newnode['ids']
        env.todo_all_todos.append({
            'docname': env.docname,
            'source': node.source or env.doc2path(env.docname),
            'lineno': node.line,
            'todo': newnode,
            'target': targetnode,
        })


#class TodoList(Directive):
#    """
#    A list of all todo entries.
#    """
#
#    has_content = False
#    required_arguments = 0
#    optional_arguments = 0
#    final_argument_whitespace = False
#    option_spec = {}
#
#    def run(self):
#        # Simply insert an empty todolist node which will be replaced later
#        # when process_todo_nodes is called
#        return [todolist('')]


def process_todo_nodes(app, doctree, fromdocname):

    # Replace all todolist nodes with a list of the collected todos.
    # Augment each todo with a backlink to the original location.
    env = app.builder.env

    if not hasattr(env, 'todo_all_todos'):
        env.todo_all_todos = []

    for node in doctree.traverse(todolist):

        content = []

        for todo_info in env.todo_all_todos:
            para = nodes.paragraph(classes=['todo-source'])
            description = _('(The <<original entry>> is located in '
                            ' %s, line %d.)') % \
                          (todo_info['source'], todo_info['lineno'])
            desc1 = description[:description.find('<<')]
            desc2 = description[description.find('>>')+2:]
            para += nodes.Text(desc1, desc1)

            # Create a reference
            newnode = nodes.reference('', '', internal=True)
            innernode = nodes.emphasis(_('original entry'), _('original entry'))
            try:
                newnode['refuri'] = app.builder.get_relative_uri(
                    fromdocname, todo_info['docname'])
                newnode['refuri'] += '#' + todo_info['target']['refid']
            except NoUri:
                # ignore if no URI can be determined, e.g. for LaTeX output
                pass
            newnode.append(innernode)
            para += newnode
            para += nodes.Text(desc2, desc2)

            # (Recursively) resolve references in the todo content
            todo_entry = todo_info['todo']
            env.resolve_references(todo_entry, todo_info['docname'],
                                   app.builder)

            # Insert into the todolist
            content.append(todo_entry)
            content.append(para)

        node.replace_self(content)


def purge_todos(app, env, docname):
    if not hasattr(env, 'todo_all_todos'):
        return
    env.todo_all_todos = [todo for todo in env.todo_all_todos
                          if todo['docname'] != docname]


def visit_proof_node(self, node):
    self.body.append(self.starttag(node, 'div'))
def depart_proof_node(self, node):
    self.body.append('</div>')

def visit_proof_title_node(self, node):
    self.body.append(self.starttag(node, 'div'))
def depart_proof_title_node(self, node):
    self.body.append('</div>')

def visit_proof_title_name_node(self, node):
    self.body.append(self.starttag(node, 'span'))
def depart_proof_title_name_node(self, node):
    self.body.append('</span>')

def visit_proof_title_content_node(self, node):
    self.body.append(self.starttag(node, 'span'))
    self.body.append("(")
def depart_proof_title_content_node(self, node):
    self.body.append(")")
    self.body.append('</span>')

def visit_proof_content_node(self, node):
    self.body.append(self.starttag(node, 'div'))
def depart_proof_content_node(self, node):
    self.body.append('</div>')

def setup(app):
    app.add_javascript('proof.js')
    app.add_stylesheet('proof.css')

    #app.add_node(todolist)
    app.add_node(proof_node,
                 html=(visit_proof_node, depart_proof_node),
                 )
    app.add_node(proof_title_node,
                 html=(visit_proof_title_node, depart_proof_title_node),
                 )
    app.add_node(proof_title_name_node,
                 html=(visit_proof_title_name_node, depart_proof_title_name_node),
                 )
    app.add_node(proof_title_content_node,
                 html=(visit_proof_title_content_node, depart_proof_title_content_node),
                 )
    app.add_node(proof_content_node,
                 html=(visit_proof_content_node, depart_proof_content_node),
                 )

    app.add_directive('proof:property', create_environment_class("property"))
    app.add_directive('proof:example', create_environment_class("example"))
    app.add_directive('proof:theorem', create_environment_class("theorem"))
    app.add_directive('proof:definition', create_environment_class("definition"))
    app.add_directive('proof:proof', create_environment_class("proof"))
    app.add_directive('proof:conjecture', create_environment_class("conjecture"))
    app.add_directive('proof:algorithm', create_environment_class("algorithm"))
    #app.add_directive('todolist', TodoList)
    app.connect('doctree-read', process_todos)
    #app.connect('doctree-resolved', process_todo_nodes)
    app.connect('env-purge-doc', purge_todos)

