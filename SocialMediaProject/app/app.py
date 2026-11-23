
from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends

from app.schema import PostCreate, PostResponse, UserRead, UserCreate, UserUpdate
from app.db import Post, create_db_and_tables, get_async_session, User

from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import select

from app.images import imagekit

import shutil
import os
import uuid
import tempfile

from app.users import auth_backend, current_active_user, fastapi_users


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)


# ============================================================
# Authentication Routes
# ============================================================

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"]
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"]
)

app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"]
)

app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"]
)

app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"]
)


# ============================================================
# Upload Post
# ============================================================

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    caption: str = Form(""),
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    temp_file_path = None

    try:
        # ----------------------------------------------------
        # Validate file
        # ----------------------------------------------------

        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="No file selected"
            )

        if not file.content_type:
            raise HTTPException(
                status_code=400,
                detail="Could not determine file type"
            )

        # Only allow images and videos
        if not (
            file.content_type.startswith("image/")
            or file.content_type.startswith("video/")
        ):
            raise HTTPException(
                status_code=400,
                detail="Only image and video files are allowed"
            )

        # ----------------------------------------------------
        # Create temporary file
        # ----------------------------------------------------

        file_extension = os.path.splitext(file.filename)[1]

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=file_extension
        ) as temp_file:

            temp_file_path = temp_file.name

            shutil.copyfileobj(
                file.file,
                temp_file
            )

        # ----------------------------------------------------
        # Read temporary file
        # ----------------------------------------------------

        with open(temp_file_path, "rb") as f:
            file_data = f.read()

        # ----------------------------------------------------
        # Upload to ImageKit
        # ----------------------------------------------------
        #
        # Current ImageKit SDK uses:
        #
        # imagekit.files.upload(...)
        #
        # instead of the older:
        #
        # imagekit.upload_file(..., options=...)
        #
        # ----------------------------------------------------

        upload_result = imagekit.files.upload(
            file=file_data,
            file_name=file.filename,
            tags=["backend-upload"]
        )

        # ----------------------------------------------------
        # Validate ImageKit response
        # ----------------------------------------------------

        if not upload_result:
            raise HTTPException(
                status_code=500,
                detail="ImageKit upload failed"
            )

        # ----------------------------------------------------
        # Determine file type
        # ----------------------------------------------------

        file_type = (
            "video"
            if file.content_type.startswith("video/")
            else "image"
        )

        # ----------------------------------------------------
        # Create database record
        # ----------------------------------------------------

        post = Post(
            user_id=user.id,
            caption=caption,
            url=upload_result.url,
            file_type=file_type,
            file_name=upload_result.name
        )

        session.add(post)

        await session.commit()
        await session.refresh(post)

        return post

    except HTTPException:
        # Preserve HTTPException status codes
        raise

    except Exception as e:
        # Rollback database transaction if something went wrong
        await session.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}"
        )

    finally:
        # ----------------------------------------------------
        # Remove temporary file
        # ----------------------------------------------------

        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

        # Close uploaded file
        await file.close()


# ============================================================
# Get Feed
# ============================================================

@app.get("/feed")
async def get_feed(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    # --------------------------------------------------------
    # Get posts
    # --------------------------------------------------------

    result = await session.execute(
        select(Post).order_by(Post.created_at.desc())
    )

    posts = result.scalars().all()

    # --------------------------------------------------------
    # Get users
    # --------------------------------------------------------

    result = await session.execute(select(User))

    users = result.scalars().all()

    user_dict = {
        u.id: u.email
        for u in users
    }

    # --------------------------------------------------------
    # Build feed response
    # --------------------------------------------------------

    posts_data = []

    for post in posts:
        posts_data.append(
            {
                "id": str(post.id),
                "user_id": str(post.user_id),
                "caption": post.caption,
                "url": post.url,
                "file_type": post.file_type,
                "file_name": post.file_name,
                "created_at": post.created_at.isoformat(),
                "is_owner": post.user_id == user.id,
                "email": user_dict.get(
                    post.user_id,
                    "Unknown"
                )
            }
        )

    return {
        "posts": posts_data
    }


# ============================================================
# Delete Post
# ============================================================

@app.delete("/posts/{post_id}")
async def delete_post(
    post_id: str,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    try:
        # ----------------------------------------------------
        # Convert ID to UUID
        # ----------------------------------------------------

        try:
            post_uuid = uuid.UUID(post_id)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid post ID"
            )

        # ----------------------------------------------------
        # Find post
        # ----------------------------------------------------

        result = await session.execute(
            select(Post).where(Post.id == post_uuid)
        )

        post = result.scalars().first()

        if not post:
            raise HTTPException(
                status_code=404,
                detail="Post not found"
            )

        # ----------------------------------------------------
        # Verify ownership
        # ----------------------------------------------------

        if post.user_id != user.id:
            raise HTTPException(
                status_code=403,
                detail="You don't have permission to delete this post"
            )

        # ----------------------------------------------------
        # Delete post
        # ----------------------------------------------------

        await session.delete(post)
        await session.commit()

        return {
            "success": True,
            "message": "Post deleted successfully"
        }

    except HTTPException:
        raise

    except Exception as e:
        await session.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete post: {str(e)}"
        )

