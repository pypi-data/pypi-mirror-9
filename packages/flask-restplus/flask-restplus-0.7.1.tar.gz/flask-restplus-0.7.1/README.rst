==============
Flask RestPlus
==============

.. image:: https://secure.travis-ci.org/noirbizarre/flask-restplus.png
    :target: http://travis-ci.org/noirbizarre/flask-restplus
    :alt: Build status
.. image:: https://coveralls.io/repos/noirbizarre/flask-restplus/badge.png?branch=0.7.1
    :target: https://coveralls.io/r/noirbizarre/flask-restplus?branch=0.7.1
    :alt: Code coverage
.. image:: https://requires.io/github/noirbizarre/flask-restplus/requirements.png?tag=0.7.1
    :target: https://requires.io/github/noirbizarre/flask-restplus/requirements/?tag=0.7.1
    :alt: Requirements Status
.. image:: https://readthedocs.org/projects/flask-restplus/badge/?version=0.7.1
    :target: http://flask-restplus.readthedocs.org/en/0.7.1/
    :alt: Documentation status

Flask-RestPlus provide syntaxic suger, helpers and automatically generated `Swagger`_ documentation on top of `Flask-Restful`_.

Compatibility
=============

Flask-RestPlus requires Python 2.7+.


Installation
============

You can install Flask-Restplus with pip:

.. code-block:: console

    $ pip install flask-restplus

or with easy_install:

.. code-block:: console

    $ easy_install flask-restplus


Quick start
===========

With Flask-Restplus, you only import the api instance to route and document your endpoints.

.. code-block:: python

    from flask import Flask
    from flask.ext.restplus import Api, Resource, fields

    app = Flask(__name__)
    api = Api(app, version='1.0', title='Todo API',
        description='A simple TODO API extracted from the original flask-restful example',
    )

    ns = api.namespace('todos', description='TODO operations')

    TODOS = {
        'todo1': {'task': 'build an API'},
        'todo2': {'task': '?????'},
        'todo3': {'task': 'profit!'},
    }

    todo = api.model('Todo', {
        'task': fields.String(required=True, description='The task details')
    })

    listed_todo = api.model('ListedTodo', {
        'id': fields.String(required=True, description='The todo ID'),
        'todo': fields.Nested(todo, description='The Todo')
    })


    def abort_if_todo_doesnt_exist(todo_id):
        if todo_id not in TODOS:
            api.abort(404, "Todo {} doesn't exist".format(todo_id))

    parser = api.parser()
    parser.add_argument('task', type=str, required=True, help='The task details', location='form')


    @ns.route('/<string:todo_id>')
    @api.doc(responses={404: 'Todo not found'}, params={'todo_id': 'The Todo ID'})
    class Todo(Resource):
        '''Show a single todo item and lets you delete them'''
        @api.doc(description='todo_id should be in {0}'.format(', '.join(TODOS.keys())))
        @api.marshal_with(todo)
        def get(self, todo_id):
            '''Fetch a given resource'''
            abort_if_todo_doesnt_exist(todo_id)
            return TODOS[todo_id]

        @api.doc(responses={204: 'Todo deleted'})
        def delete(self, todo_id):
            '''Delete a given resource'''
            abort_if_todo_doesnt_exist(todo_id)
            del TODOS[todo_id]
            return '', 204

        @api.doc(parser=parser)
        @api.marshal_with(todo)
        def put(self, todo_id):
            '''Update a given resource'''
            args = parser.parse_args()
            task = {'task': args['task']}
            TODOS[todo_id] = task
            return task


    @ns.route('/')
    class TodoList(Resource):
        '''Shows a list of all todos, and lets you POST to add new tasks'''
        @api.marshal_list_with(listed_todo)
        def get(self):
            '''List all todos'''
            return [{'id': id, 'todo': todo} for id, todo in TODOS.items()]

        @api.doc(parser=parser)
        @api.marshal_with(todo, code=201)
        def post(self):
            '''Create a todo'''
            args = parser.parse_args()
            todo_id = 'todo%d' % (len(TODOS) + 1)
            TODOS[todo_id] = {'task': args['task']}
            return TODOS[todo_id], 201


    if __name__ == '__main__':
        app.run(debug=True)


Documentation
=============

The documentation is hosted `on Read the Docs <http://flask-restplus.readthedocs.org/en/0.7.1/>`_


.. _Swagger: http://swagger.io/
.. _Flask-Restful: http://flask-restful.readthedocs.org/en/latest/
