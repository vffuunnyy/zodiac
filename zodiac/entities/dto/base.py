from pydantic import BaseModel

def to_camel_case(string: str) -> str:
    parts = string.split('_')
    return parts[0] + ''.join(word.capitalize() for word in parts[1:])


class BaseDto(BaseModel):
    class Config:
        alias_generator = to_camel_case
        populate_by_name = True