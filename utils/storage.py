"""
Production Optimization TODO:

Add CloudFront CDN for faster global delivery
Implement presigned URLs for secure access
Set up S3 lifecycle policies for cost optimization
Add CloudWatch monitoring for upload failures
Implement multipart upload for files >5GB

"""

import os
import shutil
import boto3
from botocore.exceptions import ClientError
from pathlib import Path
from typing import Optional
from fastapi import UploadFile, HTTPException, status
import uuid
from mutagen.mp3 import MP3
import tempfile

# AWS Configuration
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.environ.get("AWS_REGION", "eu-north-1")
AWS_S3_BUCKET = os.environ.get("AWS_S3_BUCKET")

# validate aws config
if not all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_S3_BUCKET]):
    raise RuntimeError("aws credentials not configured. check .env file")

s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
)

UPLOAD_DIR = Path("uploads/audio")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".mp3"}


def validate_audio_file(file: UploadFile) -> None:
    """
    checking file extension is .mp3 and content type is audio/mpeg
    """
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"invalid file type. only mp3 files are allowed. got: {file_ext}",
        )

    if file.content_type not in ["audio/mpeg", "audio/mp3"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"invalid content type. expected audio/mpeg, got: {file.content_type}",
        )


def save_audio_file_local(file: UploadFile, user_id: int) -> tuple[str, int, int]:
    try:
        file_ext = Path(file.filename).suffix.lower()
        unique_filename = f"{uuid.uuid4()}{file_ext}"

        # make directory for the user
        user_dir = UPLOAD_DIR / str(user_id)
        user_dir.mkdir(parents=True, exist_ok=True)

        file_path = user_dir / unique_filename

        # save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_size = file_path.stat().st_size

        # get audio duration from mp3 metadata
        duration = None
        try:
            audio = MP3(file_path)
            duration = int(audio.info.length)
        except Exception as e:
            print(f"warning: could not extract duration: {e}")

        file_url = str(file_path)

        return file_url, duration, file_size

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"failed to save file: {str(e)}",
        )


def save_audio_file(file: UploadFile, user_id: int) -> tuple[str, int, int]:
    try:
        file_ext = Path(file.filename).suffix.lower()
        unique_filename = f"{uuid.uuid4()}{file_ext}"

        s3_key = f"users/{user_id}/audio/{unique_filename}"

        original_filename = file.filename
        try:
            # encode to ascii to replace non-ascii characters
            safe_filename = original_filename.encode("ascii", "ignore").decode("ascii")
        except Exception:
            safe_filename = "audio.mp3"

        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            temp_path = temp_file.name

            # write uploaded file to temp location
            file.file.seek(0)  # reset file pointer
            temp_file.write(file.file.read())
            temp_file.flush()

            file_size = Path(temp_path).stat().st_size

            # get audio duration from mp3 metadata
            duration = None
            try:
                audio = MP3(temp_path)
                duration = int(audio.info.length)
            except Exception as e:
                print(f"warning: could not extract duration: {e}")

            # upload to s3
            try:
                s3_client.upload_file(
                    temp_path,
                    AWS_S3_BUCKET,
                    s3_key,
                    ExtraArgs={
                        "ContentType": "audio/mpeg",
                        "ServerSideEncryption": "AES256",
                        "Metadata": {
                            "user-id": str(user_id),
                            "original-filename": safe_filename,
                        },
                    },
                )
            except ClientError as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"failed to upload to s3: {str(e)}",
                )
            finally:
                # clean up temp file
                Path(temp_path).unlink(missing_ok=True)

        s3_url = f"https://{AWS_S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"

        return s3_url, duration, file_size

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"failed to save file: {str(e)}",
        )


def delete_audio_file(file_url: str) -> None:
    try:
        if AWS_S3_BUCKET in file_url:
            s3_key = file_url.split(f"{AWS_S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/")[
                1
            ]

            s3_client.delete_object(Bucket=AWS_S3_BUCKET, Key=s3_key)

    except Exception as e:
        print(f"warning: failed to delete file {file_url}: {e}")


def generate_presigned_url(file_url: str, expiration: int = 3600) -> str:
    try:
        s3_key = file_url.split(f"{AWS_S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/")[1]

        presigned_url = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": AWS_S3_BUCKET, "Key": s3_key},
            ExpiresIn=expiration,
        )

        return presigned_url

    except Exception as e:
        print(f"error generating presigned URL: {e}")

        return file_url
