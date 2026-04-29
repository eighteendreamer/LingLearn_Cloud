from pydantic import BaseModel, Field


class AIChatMessage(BaseModel):
    role: str = Field(min_length=1, max_length=32)
    content: str = Field(min_length=1, max_length=4000)


class AIChatCompletionRequest(BaseModel):
    messages: list[AIChatMessage] = Field(min_length=1, max_length=20)


class AIChatCompletionResponse(BaseModel):
    reply: str
    model: str
