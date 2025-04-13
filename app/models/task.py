from app import db
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Enum as SQLAlchemyEnum, text

class PriorityLevel(PyEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed = db.Column(db.Boolean, default=False)
    category = db.Column(db.String(50), nullable=True)
    
    # Priority enum with default value as string for SQLite compatibility
    priority = db.Column(
        SQLAlchemyEnum(PriorityLevel, name="prioritylevel"),
        nullable=False,
        server_default=text("'MEDIUM'")
    )

    # Relationships
    owner = db.relationship('User', back_populates='tasks')
    subtasks = db.relationship('Subtask', backref='task', lazy=True)

    def __repr__(self):
        return f'<Task {self.title}>'
    

    

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "completed": self.completed,
            "user_id": self.user_id,
            "created_at": self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            "category": self.category,
            "priority": self.priority.value if self.priority else None
        }
