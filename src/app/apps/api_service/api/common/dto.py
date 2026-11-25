from pydantic import BaseModel


class ReadyStatusResponseData(BaseModel):
    status: str = "ready"
