from agentic_reliability_framework.core.governance.intents import (
    ProvisionResourceIntent,
    GrantAccessIntent,
    DeployConfigurationIntent,
    ResourceType,
    PermissionLevel,
)
from app.models.infrastructure_intents import (
    ProvisionResourceRequest,
    GrantAccessRequest,
    DeployConfigurationRequest,
)

def to_oss_intent(api_request):
    if api_request.intent_type == "provision_resource":
        return ProvisionResourceIntent(
            resource_type=ResourceType(api_request.resource_type),
            region=api_request.region,
            size=api_request.size,
            configuration=api_request.configuration,
            environment=api_request.environment,
            requester=api_request.requester,
            provenance=api_request.provenance,
        )
    elif api_request.intent_type == "grant_access":
        return GrantAccessIntent(
            principal=api_request.principal,
            permission_level=PermissionLevel(api_request.permission_level),
            resource_scope=api_request.resource_scope,
            justification=api_request.justification,
            requester=api_request.requester,
            provenance=api_request.provenance,
        )
    elif api_request.intent_type == "deploy_config":
        return DeployConfigurationIntent(
            service_name=api_request.service_name,
            change_scope=api_request.change_scope,
            deployment_target=api_request.deployment_target,
            risk_level_hint=api_request.risk_level_hint,
            configuration=api_request.configuration,
            requester=api_request.requester,
            provenance=api_request.provenance,
        )
    else:
        raise ValueError(f"Unknown intent type: {api_request.intent_type}")
