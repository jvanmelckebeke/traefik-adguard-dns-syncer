from typing import List
import os

from pydantic import Field, root_validator, model_validator

from models.base import BaseSchema

class ConfiguredServer(BaseSchema):
    name: str = Field(description="the server name")
    ip: str = Field(description="the server ip")

class AdguardConfiguration(BaseSchema):
    address: str = Field(description="the adguard url")
    username: str = Field(description="the adguard username, optionally start with env/ to read from environment")
    password: str = Field(description="the adguard password, optionally start with env/ to read from environment")

    @model_validator(mode='before')
    @classmethod
    def resolve_env_variables(cls, values):
        for key in ['username', 'password']:
            if key in values and values[key].startswith("env/"):
                env_var = values[key][4:]  # Remove the "env/" prefix
                if env_var in os.environ:
                    values[key] = os.getenv(env_var)
                else:
                    raise ValueError(f"Environment variable {env_var} not found")
        return values



class Configuration(BaseSchema):
    adguard: AdguardConfiguration

    servers: List[ConfiguredServer]

