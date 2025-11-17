import os
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from app.utils.file_utils import validate_image
from app.utils.jwt_utils import get_user_from_jwt
from app.database.picture import Picture
from app.extensions import Base

upload_bp = Blueprint("upload", __name__)

@upload_bp.route("/upload", methods=["POST"])
def upload_picture():
    try:
        user = get_user_from_jwt()
        user_id = user["user_id"]

        file = request.files.get("file")
        if not file:
            return jsonify({"error": "No file provided"}), 400

        # Validate file
        validate_image(file)

        # Create folder named after user (if not exists)
        user_folder = os.path.join(current_app.config["UPLOAD_FOLDER"], str(user_id))
        os.makedirs(user_folder, exist_ok=True)

        filename = secure_filename(file.filename)
        filepath = os.path.join(user_folder, filename)
        file.save(filepath)

        picture = Picture(
            user_id=user_id,
            filename=filename,
            filepath=filepath,
            mimetype=file.mimetype,
            filesize=os.path.getsize(filepath),
        )
        db.session.add(picture)
        db.session.commit()

        return jsonify({
            "success": True,
            "picture": picture.to_dict()
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400

