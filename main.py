from flask import Flask, abort, request
from pathlib import Path
from models import db, Board, User, Task
from werkzeug.security import generate_password_hash, check_password_hash
from uuid import uuid4
from flask_cors import CORS
from flasgger import Swagger

app = Flask(__name__)
swagger = Swagger(app)
CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
db.init_app(app)

if not Path('project.db').is_file():
    with app.app_context():
        db.create_all()


def require_authorization():
    token: str = request.headers.get('Authorization', '').split()[1]
    users = db.session.execute(db.select(User)).scalars()
    for user in users:
        if user.id == token:
            return user
    abort(401, description='Authorization failed')


@app.post('/api/signup')
def handle_signup() -> dict:
    """Получить токен
    ---
    responses:
      200:
        description: Токен успешно получен
    """
    user_id = uuid4().hex
    db.session.add(User(id=user_id))
    db.session.commit()
    return {'token': user_id}


@app.get('/api/boards')
def handle_boards():
    """Получить список всех досок
    ---
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        default: Bearer
    responses:
      200:
        description: Список всех досок
        schema:
            type:
                array
            items:
                type: object
                properties:
                    id:
                        type: integer
                    name:
                        type: string
                    user_id:
                        type: string
                    # tasks:
                    #     type: array
                    #     items:
                    #         type: object
                    #         properties:
                    #             id:
                    #                 type: string
                    #             title:
                    #                 type: string
                    #             description:
                    #                 type: string
                    #             status:
                    #                 type: string
                    #             board_id:
                    #                 type: integer
                    #             board_user_id:
                    #                 type: string
                    #                 description: id
      401:
        description: Неправильный токен
    """
    user = require_authorization()
    return [board.as_json(without_tasks=True) for board in user.boards]

@app.get('/api/boards/<int:board_id>')
def handle_board(board_id):
    """Получить доску с задачами
    ---
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        default: Bearer
      - name: board_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Доска с задачами
        schema:
            type: object
            properties:
                id:
                    type: integer
                name:
                    type: string
                user_id:
                    type: string
                tasks:
                    type: array
                    items:
                        type: object
                        properties:
                            id:
                                type: string
                            title:
                                type: string
                            description:
                                type: string
                            status:
                                type: string
                            board_id:
                                type: integer
                            board_user_id:
                                type: string
                                description: id
      401:
        description: Неправильный токен
      404:
        description: Доски не существует
    """
    user = require_authorization()
    board = db.get_or_404(Board, {'id': board_id, 'user_id': user.id})
    return board.as_json()

@app.post('/api/boards/create')
def handle_create_board():
    """Создать новую доску
    ---
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        default: Bearer
      - name: name
        in: body
        type: object
        schema:
            properties:
                name:
                    type: string
        required: true
    responses:
      200:
        description: созданная доска
        schema:
            type: object
            properties:
                id:
                    type: integer
                name:
                    type: string
                user_id:
                    type: string
                tasks:
                    type: array
                    items:
                        type: object
                        properties:
                            id:
                                type: string
                            title:
                                type: string
                            description:
                                type: string
                            status:
                                type: string
                            board_id:
                                type: integer
                            board_user_id:
                                type: string
                                description: id
      401:
        description: Неправильный токен
      400:
        description: Если доска с таким именем уже есть
    """
    name = request.get_json().get('name', '')
    user = require_authorization()
    if not name or name in [board.name for board in user.boards]:
        abort(400)
    board = Board(
        name=name,
        user_id=user.id,
        id=max([board.id for board in user.boards]) + 1 if [board.id for board in user.boards] else 1
    )
    db.session.add(board)
    db.session.commit()
    return board.as_json()


@app.post('/api/boards/<int:board_id>/edit')
def handle_edit_board(board_id):
    """Изменить существующую доску
    ---
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        default: Bearer
      - name: body
        in: body
        type: object
        schema:
            properties:
                name:
                    type: string
        required: true
      - name: board_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: измененная доска
        schema:
            type: object
            properties:
                id:
                    type: integer
                name:
                    type: string
                user_id:
                    type: string
                tasks:
                    type: array
                    items:
                        type: object
                        properties:
                            id:
                                type: string
                            title:
                                type: string
                            description:
                                type: string
                            status:
                                type: string
                            board_id:
                                type: integer
                            board_user_id:
                                type: string
                                description: id
      401:
        description: Неправильный токен
      400:
        description: Если имя доски пустое или совпадает с предыдущим
      404:
        description: Если доски не существует
    """
    user = require_authorization()
    name = request.get_json().get('name', '')
    board = db.get_or_404(Board, {'id': board_id, 'user_id': user.id})
    if not name or name == board.name:
        abort(400, description='Name is not provided or empty or repeating')
    board.name = name
    db.session.commit()
    return board.as_json()


@app.post('/api/boards/<int:board_id>/delete')
def handle_delete_board(board_id):
    """Удалить существующую доску
    ---
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        default: Bearer
      - name: board_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: удаленная доска
        schema:
            type: object
            properties:
                id:
                    type: integer
                name:
                    type: string
                user_id:
                    type: string
                tasks:
                    type: array
                    items:
                        type: object
                        properties:
                            id:
                                type: string
                            title:
                                type: string
                            description:
                                type: string
                            status:
                                type: string
                            board_id:
                                type: integer
                            board_user_id:
                                type: string
                                description: id
      401:
        description: Неправильный токен
      404:
        description: Если доски не существует
    """
    user = require_authorization()
    board = db.get_or_404(Board, {'id': board_id, 'user_id': user.id})
    db.session.delete(board)
    db.session.commit()
    return board.as_json()


@app.post('/api/boards/<int:board_id>/tasks/create')
def handle_create_task(board_id):
    """Создать задание
    ---
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        default: Bearer
      - name: board_id
        in: path
        type: integer
        required: true
      - name: json_body
        in: body
        type: object
        required: true
        schema:
            properties:
                title:
                    type: string
                description:
                    type: string
                status:
                    type: integer
    responses:
      200:
        description: созданное задание
        schema:
            type: object
            properties:
                id:
                    type: string
                title:
                    type: string
                description:
                    type: string
                status:
                    type: string
                board_id:
                    type: integer
                board_user_id:
                    type: string
                    description: id
      401:
        description: Неправильный токен
      400:
        description: Если не задано какое-то из полей task`а
    """
    user = require_authorization()
    board = db.get_or_404(Board, {'id': board_id, 'user_id': user.id})
    title = request.get_json().get('title', '')
    description = request.get_json().get('description', '')
    status = request.get_json().get('status', '')
    if not (title and description and str(status)):
        abort(400)
    task = Task(
        title=title,
        description=description,
        status=status,
        board_id=board_id,
        id=max([tsk.id for tsk in board.tasks]) + 1 if board.tasks else 1,
        board_user_id=user.id
    )
    db.session.add(task)
    db.session.commit()
    return task.as_json()


@app.post('/api/boards/<int:board_id>/tasks/<int:task_id>/edit')
def handle_edit_task(board_id, task_id):
    """Изменить задание
    ---
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        default: Bearer
      - name: board_id
        in: path
        type: integer
        required: true
      - name: task_id
        in: path
        type: integer
        required: true
      - name: json_body
        in: body
        type: object
        required: true
        schema:
            properties:
                title:
                    type: string
                description:
                    type: string
                status:
                    type: integer
    responses:
      200:
        description: измененное задание
        schema:
            type: object
            properties:
                id:
                    type: string
                title:
                    type: string
                description:
                    type: string
                status:
                    type: string
                board_id:
                    type: integer
                board_user_id:
                    type: string
                    description: id
      401:
        description: Неправильный токен
      400:
        description: Если не задано ни одно поле task`а
      404:
        description: Если задания не существует
    """
    user = require_authorization()
    title = request.get_json().get('title', '')
    description = request.get_json().get('description', '')
    status = request.get_json().get('status', '')
    if not (title or description or status):
        abort(400)
    task = db.get_or_404(Task, {'id': task_id, 'board_id': board_id, 'board_user_id': user.id})
    if title:
        task.title = title
    if description:
        task.description = description
    if status:
        task.status = status
    db.session.commit()
    return task.as_json()


@app.post('/api/boards/<int:board_id>/tasks/<int:task_id>/delete')
def handle_delete_task(board_id, task_id):
    """Удалить задание
    ---
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        default: Bearer
      - name: board_id
        in: path
        type: integer
        required: true
      - name: task_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: удаленное задание
        schema:
            type: object
            properties:
                id:
                    type: string
                title:
                    type: string
                description:
                    type: string
                status:
                    type: string
                board_id:
                    type: integer
                board_user_id:
                    type: string
                    description: id
      401:
        description: Неправильный токен
      404:
        description: Если задания не существует
    """
    user = require_authorization()
    task = db.get_or_404(Task, {'id': task_id, 'board_id': board_id, 'board_user_id': user.id})
    db.session.delete(task)
    db.session.commit()
    return task.as_json()

if __name__ == '__main__':
    app.run(debug=True)
