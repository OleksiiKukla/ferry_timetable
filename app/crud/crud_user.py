from __future__ import annotations

from numpy.f2py.symbolic import Language
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import User
from app.schemas.user_schemas import UserCreateSchemas


class CRUDUser(CRUDBase[User, UserCreateSchemas, UserCreateSchemas]):
    async def create_user(
        self,
        new_user: UserCreateSchemas,
        db: AsyncSession,
    ) -> User:
        new_user_data = self.model(
            name=new_user.name,
            chat_id=new_user.chat_id,
            language=new_user.language,
        )
        db.add(new_user_data)
        await db.commit()
        await db.refresh(new_user_data)

        return new_user_data

    async def get_user(
        self,
        db: AsyncSession,
        chat_id: int,
        name: str,
    ) -> User:
        query = select(
            self.model.id,
            self.model.name,
            self.model.chat_id,
            self.model.language,
            self.model.created_date,
            self.model.last_request,
        ).where(
            self.model.chat_id == chat_id,
            self.model.name == name,
        )
        user = await db.execute(query)
        return user.one_or_none()

    async def get_or_create(
        self,
        new_user: UserCreateSchemas,
        db: AsyncSession,
    ) -> tuple[User, bool]:

        created = False
        user = await self.get_user(db, new_user.chat_id, new_user.name)

        if user is None:
            user = await self.create_user(new_user, db)
            created = True
        return user, created

    async def update_language(self, user: User, new_lagguage: Language, db: AsyncSession) -> User:
        query = update(self.model).where(User.id == user.id).values(language=new_lagguage).returning(self.model)

        result = await db.execute(query)
        updated_user = result.one_or_none()
        await db.commit()
        return updated_user


user_crud = CRUDUser(model=User)
