# app/api.py

from flask_restful import Resource, reqparse
from app.models import Task
from app import db

class TaskListAPI(Resource):
    def get(self):
        tasks = Task.query.all()
        return [
            {
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'status': task.status,
                'priority': task.priority
            } for task in tasks
        ], 200

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('title', required=True, help="Title cannot be blank")
        parser.add_argument('description')
        parser.add_argument('status', default='To Do')
        parser.add_argument('priority', default='Medium')
        args = parser.parse_args()

        task = Task(
            title=args['title'],
            description=args['description'],
            status=args['status'],
            priority=args['priority'],
            user_id=1  # 示例，需根据实际情况设置
        )
        db.session.add(task)
        db.session.commit()
        return {'message': 'Task created', 'task': {'id': task.id, 'title': task.title}}, 201

class TaskAPI(Resource):
    def get(self, task_id):
        task = Task.query.get_or_404(task_id)
        return {
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'status': task.status,
            'priority': task.priority
        }, 200

    def put(self, task_id):
        task = Task.query.get_or_404(task_id)
        parser = reqparse.RequestParser()
        parser.add_argument('title')
        parser.add_argument('description')
        parser.add_argument('status')
        parser.add_argument('priority')
        args = parser.parse_args()

        if args['title']:
            task.title = args['title']
        if args['description']:
            task.description = args['description']
        if args['status']:
            task.status = args['status']
        if args['priority']:
            task.priority = args['priority']

        db.session.commit()
        return {'message': 'Task updated'}, 200

    def delete(self, task_id):
        task = Task.query.get_or_404(task_id)
        db.session.delete(task)
        db.session.commit()
        return {'message': 'Task deleted'}, 200