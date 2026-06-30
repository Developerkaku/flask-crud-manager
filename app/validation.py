from app.models import VALID_STATUSES


class ValidationError(Exception):
    """Raised when incoming payload data fails validation."""

    def __init__(self, message):
        super().__init__(message)
        self.message = message


def validate_task_payload(data, partial=False):
    """
    Validate a task creation/update payload.

    :param data: dict parsed from request JSON
    :param partial: if True, allows missing fields (used for PUT/PATCH-style
                     partial updates). If False, title is required (POST).
    :raises ValidationError: if validation fails
    :return: dict of cleaned fields
    """
    if data is None or not isinstance(data, dict):
        raise ValidationError("Request body must be a JSON object.")

    cleaned = {}

    if "title" in data:
        title = data.get("title")
        if not isinstance(title, str) or not title.strip():
            raise ValidationError("'title' must be a non-empty string.")
        if len(title) > 120:
            raise ValidationError("'title' must be 120 characters or fewer.")
        cleaned["title"] = title.strip()
    elif not partial:
        raise ValidationError("'title' is required.")

    if "description" in data:
        description = data.get("description")
        if description is not None and not isinstance(description, str):
            raise ValidationError("'description' must be a string or null.")
        cleaned["description"] = description

    if "status" in data:
        status = data.get("status")
        if status not in VALID_STATUSES:
            raise ValidationError(
                f"'status' must be one of {VALID_STATUSES}."
            )
        cleaned["status"] = status

    # Reject unknown fields to keep the API contract explicit
    allowed_fields = {"title", "description", "status"}
    unknown_fields = set(data.keys()) - allowed_fields
    if unknown_fields:
        raise ValidationError(
            f"Unknown field(s): {', '.join(sorted(unknown_fields))}."
        )

    return cleaned
