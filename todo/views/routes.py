from flask import Blueprint, jsonify, request
from sqlalchemy import select
from todo.models import db
from todo.models.todo import Todo
from datetime import datetime, timedelta
 
api = Blueprint('api', __name__, url_prefix='/api/v1') 

TEST_ITEM = {
    "id": 1,
    "title": "Watch CSSE6400 Lecture",
    "description": "Watch the CSSE6400 lecture on ECHO360 for week 1",
    "completed": True,
    "deadline_at": "2023-02-27T00:00:00",
    "created_at": "2023-02-20T00:00:00",
    "updated_at": "2023-02-20T00:00:00"
}
 
@api.route('/health') 
def health():
    """Return a status of 'ok' if the server is running and listening to request"""
    return jsonify({"status": "ok"})


@api.route('/todos', methods=['GET'])
def get_todos():
    todos = Todo.query.all()
    result = []

    session = db.session
    q = select(Todo)
    if request.args.get("completed") == 'true':
        q = q.where(Todo.completed == True)
    elif request.args.get("completed") == 'false':
        q = q.where(Todo.completed == False)
    
    if request.args.get("window"):
        future_date = (datetime.now() + timedelta(days=int(request.args.get("window")))).isoformat()
        q = q.where(Todo.deadline_at < future_date)
     
    todos = session.scalars(q).all()
    
    for todo in todos:
        result.append(todo.to_dict())
    return jsonify(result)

@api.route('/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    """Return the details of a todo item"""
    todo = Todo.query.get(todo_id)
    if todo is None:
        return jsonify({'error': 'Todo not found'}), 404
    return jsonify(todo.to_dict())

@api.route('/todos', methods=['POST'])
def create_todo():
    """Create a new todo item and return the created item"""
    for key in request.json:
        if key not in {'title', 'description', 'completed', 'deadline_at', 'id'}:
            return jsonify({'error': 'invalid json'}), 400

    if 'title' not in request.json: 
        return jsonify({'error': 'No title given'}), 400
    
    todo = Todo(
        title=request.json.get('title'),
        description=request.json.get('description'),
        completed=request.json.get('completed'
        , False),
    )
    
    if 'deadline_at' in request.json:
        todo.deadline_at = datetime.fromisoformat(request.json.get('deadline_at'))
    
    # Adds a new record to the database or will update an existing record.
    db.session.add(todo)
    
    # Commits the changes to the database.
    # This must be called for the changes to be saved.
    db.session.commit()
    return jsonify(todo.to_dict()), 201

@api.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    """Update a todo item and return the updated item"""
    todo = Todo.query.get(todo_id)
    if todo is None:
        return jsonify({'error': 'Todo not found'}), 404
    
     # check title given
    if request.json.get('title') == None:
        return jsonify({'error': 'Todo requires title'}), 400
    
    if todo_id != todo.id:
        return jsonify({'error': 'Todo id changed'}), 400
    
    todo.title = request.json.get('title', todo.title)
    todo.description = request.json.get('description', todo.description)
    todo.completed = request.json.get('completed', todo.completed)
    if 'deadline_at' in request.json: 
        todo.deadline_at = datetime.fromisoformat(request.json.get('deadline_at', todo.deadline_at))
    db.session.commit()
    return jsonify(todo.to_dict())

@api.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    """Delete a todo item and return the deleted item"""
    todo = Todo.query.get(todo_id)
    if todo is None:
        return jsonify({}), 200
    db.session.delete(todo)
    db.session.commit()
    return jsonify(todo.to_dict()), 200
 
