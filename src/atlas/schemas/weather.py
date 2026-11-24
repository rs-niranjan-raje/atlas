"""The arguments the model must send when it asks us to call get_weather."""

from pydantic import BaseModel

from atlas.schemas.common import NotBlankStr


class WeatherArgs(BaseModel):
    """Arguments for get_weather. The model's request is untrusted, so we validate it."""

    city: NotBlankStr
