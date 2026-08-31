from uuid import UUID

from pydantic import BaseModel, EmailStr

from app.models.user import UserStatus


class UserResponse(BaseModel):
    uuid: UUID
    first_name: str
    last_name: str
    email: EmailStr
    status: UserStatus

    model_config = {
        "from_attributes": True
    }