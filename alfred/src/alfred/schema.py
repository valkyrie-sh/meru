from pydantic import (
    BaseModel,
)


class UpdateNixConfigRequest(BaseModel):
    nix_config: str
    file: str


class GetNixConfigRequest(BaseModel):
    config_type: str = "nix-darwin"
    file: str = "flake.nix"


class NixConfigPromptInput(BaseModel):
    config_type: str
