from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal, List, Any, Dict
from enum import Enum

from agentic_reliability_framework.core.governance.intents import (
    ResourceType,
    PermissionLevel,
    Environment,
    ChangeScope,
)

class BaseIntentRequest(BaseModel):
    environment: Environment
    estimated_cost: Optional[float] = Field(None, ge=0)
    policy_violations: List[str] = Field(default_factory=list)
    requester: str = Field(...)
    provenance: Dict[str, Any] = Field(default_factory=dict)

class ProvisionResourceRequest(BaseIntentRequest):
    intent_type: Literal["provision_resource"] = "provision_resource"
    resource_type: ResourceType
    region: str
    size: str
    configuration: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("region")
    def validate_region(cls, v):
        return v

class GrantAccessRequest(BaseIntentRequest):
    intent_type: Literal["grant_access"] = "grant_access"
    principal: str
    permission_level: PermissionLevel
    resource_scope: str
    justification: Optional[str] = None

    @field_validator("resource_scope")
    def validate_resource_scope(cls, v):
        if not v.startswith("/"):
            raise ValueError("Resource scope must start with '/'")
        return v

class DeployConfigurationRequest(BaseIntentRequest):
    intent_type: Literal["deploy_config"] = "deploy_config"
    service_name: str
    change_scope: ChangeScope
    deployment_target: Environment
    risk_level_hint: Optional[float] = Field(None, ge=0, le=1)
    configuration: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("service_name")
    def validate_service_name(cls, v):
        if len(v) < 3:
            raise ValueError("Service name must be at least 3 characters")
        return v

InfrastructureIntentRequest = ProvisionResourceRequest | GrantAccessRequest | DeployConfigurationRequest
