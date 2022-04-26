from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sys
from sqlalchemy.orm import backref
from settings import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://{}:{}@{}/{}".format(DB_USER, DB_PASSWORD, 'localhost:5432', DB_NAME)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#=================================================================================
                            # THE DATABASE MODELS
#=================================================================================

class Todo(db.Model):
  __tablename__ = 'todos'
  id = db.Column(db.Integer, primary_key=True)
  description = db.Column(db.String(), nullable=False)
  completed = db.Column(db.Boolean, nullable=False, default=False)
  list_id = db.Column(db.Integer, db.ForeignKey('todolists.id'), nullable=False)

  def __repr__(self):
    return 'Todo {} {} list {}'.format(self.id, self.description, self.list_id)

class Todolist(db.Model):
  __tablename__ = 'todolists'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, nullable=False)
  completed = db.Column(db.Boolean, nullable=False, default=False)
  todos = db.relationship('Todo', backref='list', lazy=True, cascade='all, delete-orphan')

  def __repr__(self):
    return 'Todolist {} {}'.format(self.id, self.name)

#db.create_all()
#=================================================================================
                               #THE CONTROLLERS
#=================================================================================

@app.route('/todos/<todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
  try:
    Todo.query.filter_by(id=todo_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return jsonify({ 'success': True })

@app.route('/todolists/<todolist_id>', methods=['DELETE'])
def delete_todolist(todolist_id):
  try:
    Todo.query.filter_by(list_id=todolist_id).delete()
    Todolist.query.filter_by(id=todolist_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return jsonify({'success': True})

# note: more conventionally, we would write a
# POST endpoint to /todos for the create endpoint:
# @app.route('/todos', method=['POST'])
@app.route('/todos/create', methods=['POST'])
def create_todo():
  error = False
  body = {}
  try:
    description = request.get_json()['description']
    list_id = request.get_json()['list_id']
    todo = Todo(description=description, completed=False, list_id=list_id)
    db.session.add(todo)
    db.session.commit()
    body['id'] = todo.id
    body['completed'] = todo.completed
    body['description'] = todo.description
    body['list_id'] = todo.list_id
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    abort (400)
  else:
    return jsonify(body)

@app.route('/todolists/create', methods=['POST'])
def create_todolist():
  error = False
  body = {}
  try:
    name = request.get_json()['name']
    todolist = Todolist(name=name, completed=False)
    print(todolist)
    db.session.add(todolist)
    db.session.commit()
    body['id'] = todolist.id
    body['completed'] = todolist.completed
    body['name'] = todolist.name
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    abort (400)
  else:
    return jsonify(body)
  

@app.route('/todos/<todo_id>/set-completed', methods=['POST'])
def set_completed_todo(todo_id):
  try:
    completed = request.get_json()['completed']
    print('completed', completed)
    todo = Todo.query.get(todo_id)
    todo.completed = completed
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('index'))

@app.route('/todolists/<todolist_id>/set-completed', methods=['POST'])
def set_completed_todolist(todolist_id):
  try:
    completed = request.get_json()['completed']
    print('completed', completed)
    todolist = Todolist.query.get(todolist_id)
    todolist.completed = completed
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('index'))


@app.route('/lists/<list_id>')
def get_list_todos(list_id):
  return render_template('index.html', 
  lists = Todolist.query.order_by('id').all(),
  active_list = Todolist.query.get(list_id),
  todos = Todo.query.filter_by(list_id=list_id).order_by('id').all())

@app.route('/')
def index():
  return redirect(url_for('get_list_todos', list_id=1))
