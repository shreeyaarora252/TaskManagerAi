from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.task import Task, PriorityLevel
from app.models.user import User
from app.utils.helpers import categorize_task
from datetime import datetime

tasks_bp = Blueprint('tasks', __name__)

# Add a new task (POST) - requires authentication
@tasks_bp.route('/', methods=['POST'])
@jwt_required()
def create_task():
    # Get current user from JWT token
    current_user_id = get_jwt_identity()
    data = request.get_json()

    title = data.get('title')
    description = data.get('description')
    priority = data.get('priority', 'MEDIUM').upper()

    if priority not in ['LOW', 'MEDIUM', 'HIGH']:
        return jsonify({"error": "Invalid priority level"}), 400

    if not title or not description:
        return jsonify({'error': 'Missing title or description'}), 400

    category = categorize_task(title, description)

    new_task = Task(
        user_id=current_user_id,  # Use user_id from JWT token
        title=title,
        description=description,
        completed=False,
        category=category,
        priority=PriorityLevel[priority]
    )

    db.session.add(new_task)
    db.session.commit()

    return jsonify({'message': 'Task created successfully'}), 201

# Get all tasks (GET) - requires authentication
@tasks_bp.route('/get', methods=['GET'])
@jwt_required()
def get_tasks():
    
    current_user_id = get_jwt_identity()
    priority_filter = request.args.get('priority', '').upper()
    sort_order = request.args.get('sort', '').lower()

    query = Task.query.filter_by(user_id=current_user_id)  # Filter tasks by user_id from JWT token

    if priority_filter:
        try:
            query = query.filter(Task.priority == PriorityLevel[priority_filter])
        except KeyError:
            return jsonify({'error': 'Invalid priority filter'}), 400

    if sort_order == 'asc':
        query = query.order_by(Task.priority.asc())
    elif sort_order == 'desc':
        query = query.order_by(Task.priority.desc())

    tasks = query.all()

    tasks_list = [{
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'created_at': task.created_at.strftime("%Y-%m-%d %H:%M:%S") if task.created_at else None,
        'completed': task.completed,
        'category': task.category,
        'priority': task.priority.name if task.priority else None
    } for task in tasks]

    return jsonify({'tasks': tasks_list}), 200

# View a single task by ID or search by keyword - requires authentication
@tasks_bp.route('/tasks/<task_id>', methods=['GET'])
@jwt_required()
def get_task_or_search(task_id):
    current_user = int(get_jwt_identity())

    if task_id == "search":
        query = request.args.get('q', '').strip().lower()

        if not query:
            return jsonify({'error': 'Search query is required'}), 400

        matching_tasks = Task.query.filter(
            Task.user_id == current_user['user_id'],  # Ensure task belongs to the authenticated user
            (Task.title.ilike(f'%{query}%')) | (Task.description.ilike(f'%{query}%'))
        ).all()

        results = [{
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'created_at': task.created_at.strftime('%Y-%m-%d %H:%M:%S') if task.created_at else None,
            'completed': task.completed,
            'category': task.category,
            'priority': task.priority.name if task.priority else None
        } for task in matching_tasks]

        return jsonify({'results': results}), 200

    else:
        try:
            task_id = int(task_id)
        except ValueError:
            return jsonify({'error': 'Invalid task ID'}), 400

        task = Task.query.get(task_id)
        if not task or task.user_id != current_user['user_id']: 
            return jsonify({'message': 'Task not found or not authorized.'}), 404

        return jsonify({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'created_at': task.created_at.strftime('%Y-%m-%d %H:%M:%S') if task.created_at else None,
            'completed': task.completed,
            'category': task.category,
            'priority': task.priority.name if task.priority else None
        }), 200

# Update a task (PUT) - requires authentication
@tasks_bp.route('/tasks/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    current_user = get_jwt_identity()

    task = Task.query.get(task_id)
    if not task or task.user_id != current_user['user_id']:  # Ensure task belongs to the authenticated user
        return jsonify({'message': 'Task not found or not authorized.'}), 404

    data = request.json
    task.title = data.get('title', task.title)
    task.description = data.get('description', task.description)

    # Handle completed flag and timestamp
    if data.get('completed') and not task.completed:
        task.completed = True
        task.completed_at = datetime.utcnow()
    elif data.get('completed') is False and task.completed:
        task.completed = False
        task.completed_at = None

    # Handle priority update
    priority = data.get('priority')
    if priority:
        priority = priority.upper()
        if priority in PriorityLevel.__members__:
            task.priority = PriorityLevel[priority]
        else:
            return jsonify({"error": "Invalid priority value"}), 400

    db.session.commit()

    return jsonify({
        'message': 'Task updated successfully!',
        'task': {
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'completed': task.completed,
            'created_at': task.created_at.strftime('%Y-%m-%d %H:%M:%S') if task.created_at else None,
            'category': task.category,
            'priority': task.priority.name if task.priority else None
        }
    }), 200

# Delete a task (DELETE) - requires authentication
@tasks_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    current_user = get_jwt_identity()

    task = Task.query.get(task_id)
    if not task or task.user_id != current_user['user_id']:  # Ensure task belongs to the authenticated user
        return jsonify({'message': 'Task not found or not authorized.'}), 404

    db.session.delete(task)
    db.session.commit()

    return jsonify({'message': 'Task deleted successfully!'}), 200

# Productivity (Analytics) - requires authentication
@tasks_bp.route('/analytics', methods=['GET'])
@jwt_required()
def get_analytics():
    current_user = get_jwt_identity()

    tasks = Task.query.filter_by(user_id=current_user['user_id']).all()

    if not tasks:
        return jsonify({"message": "No tasks found for this user."}), 404

    total_tasks = len(tasks)
    completed_tasks = sum(1 for task in tasks if task.completed)
    completion_rate = round((completed_tasks / total_tasks) * 100, 2) if total_tasks else 0

    # Breakdown by category
    category_count = {}
    for task in tasks:
        category = task.category or "Uncategorized"
        category_count[category] = category_count.get(category, 0) + 1

    # Breakdown by priority
    priority_count = {'LOW': 0, 'MEDIUM': 0, 'HIGH': 0}
    for task in tasks:
        if task.priority:
            priority_count[task.priority.name] += 1

    # Tasks completed per day (for last 7 days)
    from datetime import datetime, timedelta
    today = datetime.today()
    past_week = [today - timedelta(days=i) for i in range(6, -1, -1)]
    completed_per_day = {day.strftime('%Y-%m-%d'): 0 for day in past_week}

    for task in tasks:
        if task.completed and task.completed_at:
            completed_day = task.completed_at.date().strftime('%Y-%m-%d')
            if completed_day in completed_per_day:
                completed_per_day[completed_day] += 1

    return jsonify({
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "completion_rate": completion_rate,
        "category_count": category_count,
        "priority_count": priority_count,
        "completed_per_day": completed_per_day
    })
