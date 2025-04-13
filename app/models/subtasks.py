from app import db
from datetime import datetime

class Subtask(db.Model):
    __tablename__ = 'subtasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Subtask {self.title}>'

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "completed": self.completed,
            "task_id": self.task_id,
            "created_at": self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

