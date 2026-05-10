import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.crud.user import user_crud
from app.schemas.user import UserCreate, UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        409: {"description": "E-mail já cadastrado"},
    },
)
async def create_user(payload: UserCreate, db: AsyncSession = Depends(get_db)) -> UserResponse:
    existing = await user_crud.get_by_email(db, payload.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um usuário com este e-mail",
        )

    user_data = payload.model_dump()
    user_data["hashed_password"] = _hash_password(payload.password)
    del user_data["password"]

    user = await user_crud.create(db, user_data)
    return UserResponse.model_validate(user)


@router.get(
    "/",
    response_model=list[UserResponse],
    responses={
        404: {"description": "Nenhum usuário encontrado"},
    },
)
async def list_users(db: AsyncSession = Depends(get_db)) -> list[UserResponse]:
    users = await user_crud.get_all(db)
    if not users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhum usuário encontrado",
        )
    return [UserResponse.model_validate(u) for u in users]


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    responses={
        404: {"description": "Usuário não encontrado"},
    },
)
async def get_user(user_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> UserResponse:
    user = await user_crud.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado",
        )
    return UserResponse.model_validate(user)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    responses={
        404: {"description": "Usuário não encontrado"},
        409: {"description": "E-mail já em uso por outro usuário"},
    },
)
async def update_user(
    user_id: uuid.UUID,
    payload: UserUpdate,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    user = await user_crud.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado",
        )

    update_data = payload.model_dump(exclude_unset=True)

    if "password" in update_data and update_data["password"] is not None:
        update_data["hashed_password"] = _hash_password(update_data.pop("password"))
    elif "password" in update_data:
        del update_data["password"]

    if "email" in update_data and update_data["email"] is not None:
        existing = await user_crud.get_by_email(db, update_data["email"])
        if existing and existing.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Já existe um usuário com este e-mail",
            )

    updated = await user_crud.update(db, user, update_data)
    return UserResponse.model_validate(updated)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"description": "Usuário não encontrado"},
    },
)
async def delete_user(user_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> None:
    user = await user_crud.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado",
        )
    await user_crud.delete(db, user)


def _hash_password(password: str) -> str:
    import hashlib

    return hashlib.sha256(password.encode("utf-8")).hexdigest()
