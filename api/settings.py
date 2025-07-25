from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_core.core_schema import FieldValidationInfo
from pydantic_settings import BaseSettings


class ApiSettings(BaseSettings):
    """Api settings that are set using environment variables."""

    title: str = "agent-api"
    version: str = "1.0"

    # Set to False to disable docs at /docs and /redoc
    docs_enabled: bool = True

    # Cors origin list to allow requests from.
    # This list is set using the set_cors_origin_list validator
    # which uses the runtime_env variable to set the
    # default cors origin list.
    cors_origin_list: Optional[List[str]] = Field(None, validate_default=True)

    @field_validator("cors_origin_list", mode="before")
    def set_cors_origin_list(cls, cors_origin_list, info: FieldValidationInfo):
        valid_cors = cors_origin_list or []

        # Add app.agno.com to cors to allow requests from the Agno playground.
        valid_cors.append("https://app.agno.com")
        # Add localhost to cors to allow requests from the local environment.
        valid_cors.append("http://localhost")
        # Add localhost:3000 to cors to allow requests from local Agent UI.
        valid_cors.append("http://localhost:3000")
        # Add localhost:3001 to cors to allow requests from Pepper Law frontend.
        valid_cors.append("http://localhost:3001")
        # Add localhost:8080 to cors to allow requests from Vite dev server.
        valid_cors.append("http://localhost:8080")

        return valid_cors


# Create ApiSettings object
api_settings = ApiSettings()
