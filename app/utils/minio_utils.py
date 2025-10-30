from datetime import timedelta
from app.extensions import minio_client

MINIO_BUCKET = "gofood-images"

def upload_to_minio(vendor_name, file_bytes, filename, content_type):
    """
    Upload file bytes to MinIO and return its object name.
    """
    object_name = f"{vendor_name}/{filename}"
    minio_client.put_object(
        bucket_name=MINIO_BUCKET,
        object_name=object_name,
        data=file_bytes,
        length=len(file_bytes),
        content_type=content_type,
    )
    return object_name


def get_minio_file_url(vendor_name, filename, expires=timedelta(hours=1)):
    """
    Return a presigned MinIO URL for an object.
    """
    object_name = f"{vendor_name}/{filename}"
    return minio_client.presigned_get_object(MINIO_BUCKET, object_name, expires=expires)

