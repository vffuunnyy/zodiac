from fastapi_camelcase import CamelModel
from pydantic import ConfigDict
from pydantic.alias_generators import to_camel


class BaseDto(CamelModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )
