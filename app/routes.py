import logging

from flask import Blueprint, jsonify, request

from app import db
from app.models import Task
from app.validation import ValidationError, validate_task_payload


def _get_task_or_none(task_id):
    return db.session.get(Task, task_id)


logger = logging.getLogger(__name__)

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")


@tasks_bp.route("", methods=["POST"])
def create_task():
    data = request.get_json(silent=True)
    cleaned = validate_task_payload(data, partial=False)

    task = Task(
        title=cleaned["title"],
        description=cleaned.get("description"),
        status=cleaned.get("status", "pending"),
    )
    db.session.add(task)
    db.session.commit()

    logger.info("Created task id=%s title=%r", task.id, task.title)
    return jsonify(task.to_dict()), 201


@tasks_bp.route("", methods=["GET"])
def list_tasks():
    status_filter = request.args.get("status")
    query = Task.query

    if status_filter:
        query = query.filter_by(status=status_filter)

    tasks = query.order_by(Task.created_at.desc()).all()
    logger.info("Listed %d task(s) (status filter=%r)", len(tasks), status_filter)
    return jsonify([t.to_dict() for t in tasks]), 200


@tasks_bp.route("/<int:task_id>", methods=["GET"])
def get_task(task_id):
    task = _get_task_or_none(task_id)
    if task is None:
        logger.warning("Task id=%s not found", task_id)
        return jsonify({"error": "Task not found"}), 404

    return jsonify(task.to_dict()), 200


@tasks_bp.route("/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    task = _get_task_or_none(task_id)
    if task is None:
        logger.warning("Attempted update on missing task id=%s", task_id)
        return jsonify({"error": "Task not found"}), 404

    data = request.get_json(silent=True)
    cleaned = validate_task_payload(data, partial=True)

    if not cleaned:
        raise ValidationError("Request body must include at least one field to update.")

    for field, value in cleaned.items():
        setattr(task, field, value)

    db.session.commit()
    logger.info("Updated task id=%s fields=%s", task_id, list(cleaned.keys()))
    return jsonify(task.to_dict()), 200


@tasks_bp.route("/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = _get_task_or_none(task_id)
    if task is None:
        logger.warning("Attempted delete on missing task id=%s", task_id)
        return jsonify({"error": "Task not found"}), 404

    db.session.delete(task)
    db.session.commit()
    logger.info("Deleted task id=%s", task_id)
    return "", 204
