from sqlmodel import SQLModel, Field

class IDModel(SQLModel):
    id: int | None = Field(default=None, primary_key=True, index=True)
