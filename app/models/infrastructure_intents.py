from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal, List, Any, Dict
from enum import Enum

# Re‑export enums from OSS for consistency (optional, but helps validation)
from agentic_reliability_framework.core.governance.intents import (
    ResourceType,
    PermissionLevel,
    Environment,
    ChangeScope,
)


# -----------------------------------------------------------------------------
# Base Intent Request
# -----------------------------------------------------------------------------
class BaseIntentRequest(BaseModel):
    environment: Environment
    estimated_cost: Optional[float] = Field(None, ge=0, description="Estimated cost impact (if any)")
    policy_violations: List[str] = Field(default_factory=list, description="List of policy violations already known")
    requester: str = Field(..., description="User or service principal requesting the action")
    provenance: Dict[str, Any] = Field(default_factory=dict, description="Metadata about the request origin")


# -----------------------------------------------------------------------------
# ProvisionResourceIntent Request
# -----------------------------------------------------------------------------
class ProvisionResourceRequest(BaseIntentRequest):
    intent_type: Literal["ProvisionResourceIntent"] = "ProvisionResourceIntent"
    resource_type: ResourceType
    region: str
    size: str
    configuration: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("region")
    def validate_region(cls, v: str) -> str:
        # Optional: add validation logic if needed; OSS already validates internally
        return v


# -----------------------------------------------------------------------------
# GrantAccessIntent Request
# -----------------------------------------------------------------------------
class GrantAccessRequest(BaseIntentRequest):
    intent_type: Literal["GrantAccessIntent"] = "GrantAccessIntent"
    principal: str
    permission_level: PermissionLevel
    resource_scope: str
    justification: Optional[str] = None

    @field_validator("resource_scope")
    def validate_resource_scope(cls, v: str) -> str:
        if not v.startswith("/"):
            raise ValueError("Resource scope must start with '/'")
        return v


# -----------------------------------------------------------------------------
# DeployConfigurationIntent Request
# -----------------------------------------------------------------------------
class DeployConfigurationRequest(BaseIntentRequest):
    intent_type: Literal["DeployConfigurationIntent"] = "DeployConfigurationIntent"
    service_name: str
    change_scope: ChangeScope
    deployment_target: Environment
    risk_level_hint: Optional[float] = Field(None, ge=0, le=1)
    configuration: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("service_name")
    def validate_service_name(cls, v: str) -> str:
        if len(v) < 3:
            raise ValueError("Service name must be at least 3 characters")
        return v


# -----------------------------------------------------------------------------
# Union type for all intent requests (for parsing)
# -----------------------------------------------------------------------------
InfrastructureIntentRequest = ProvisionResourceRequest | GrantAccessRequest | DeployConfigurationRequest
