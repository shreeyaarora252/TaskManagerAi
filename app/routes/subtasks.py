from flask import Blueprint, request, jsonify
from app import db
from app.models.subtasks import Subtask
from app.models.task import Task
from flask_jwt_extended import jwt_required, get_jwt_identity

subtasks_bp = Blueprint('subtasks', __name__)

# Create a new subtask (POST)
@subtasks_bp.route('/<int:task_id>', methods=['POST'])
@jwt_required()
def create_subtask(task_id):
    current_user_id = get_jwt_identity()
    data = request.get_json()

    if not data or 'title' not in data:
        return jsonify({'error': 'Missing title in request body'}), 400

    title = data['title']

    task = Task.query.filter_by(id=task_id, user_id=current_user_id).first()
    if not task:
        return jsonify({'error': 'Task not found or unauthorized'}), 404

    new_subtask = Subtask(
        task_id=task_id,
        title=title
    )

    db.session.add(new_subtask)
    db.session.commit()

    return jsonify({'message': 'Subtask created successfully', 'subtask': new_subtask.to_dict()}), 201

# Get all subtasks for a specific task (GET)
@subtasks_bp.route('/<int:task_id>', methods=['GET'])
@jwt_required()
def get_subtasks_for_task(task_id):
    current_user_id = get_jwt_identity()
    
    task = Task.query.filter_by(id=task_id, user_id=current_user_id).first()
    if not task:
        return jsonify({'error': 'Task not found or unauthorized'}), 404

    subtasks = Subtask.query.filter_by(task_id=task_id).all()
    subtasks_list = [subtask.to_dict() for subtask in subtasks]

    return jsonify({'subtasks': subtasks_list}), 200

# Update a subtask (PUT)
@subtasks_bp.route('/<int:subtask_id>', methods=['PUT'])
@jwt_required()
def update_subtask(subtask_id):
    current_user_id = get_jwt_identity()

    subtask = Subtask.query.get(subtask_id)
    if not subtask or subtask.task.user_id != current_user_id:
        return jsonify({'error': 'Subtask not found or unauthorized'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Missing request body'}), 400

    subtask.title = data.get('title', subtask.title)
    subtask.completed = data.get('completed', subtask.completed)

    db.session.commit()

    return jsonify({
        'message': 'Subtask updated successfully',
        'subtask': subtask.to_dict()
    }), 200

# Delete a subtask (DELETE)
@subtasks_bp.route('/<int:subtask_id>', methods=['DELETE'])
@jwt_required()
def delete_subtask(subtask_id):
    current_user_id = get_jwt_identity()

    subtask = Subtask.query.get(subtask_id)
    if not subtask or subtask.task.user_id != current_user_id:
        return jsonify({'error': 'Subtask not found or unauthorized'}), 404

    db.session.delete(subtask)
    db.session.commit()

    return jsonify({'message': 'Subtask deleted successfully'}), 200
