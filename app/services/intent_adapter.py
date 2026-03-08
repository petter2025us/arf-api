from agentic_reliability_framework.core.governance.intents import (
    ProvisionResourceIntent,
    GrantAccessIntent,
    DeployConfigurationIntent,
    ResourceType,
    PermissionLevel,
    Environment,
    ChangeScope,
)
from app.models.infrastructure_intents import (
    ProvisionResourceRequest,
    GrantAccessRequest,
    DeployConfigurationRequest,
)


def to_oss_intent(api_request):
    """
    Convert an API request model into the corresponding OSS intent object.
    """
    if api_request.intent_type == "ProvisionResourceIntent":
        return ProvisionResourceIntent(
            resource_type=ResourceType(api_request.resource_type),
            region=api_request.region,
            size=api_request.size,
            configuration=api_request.configuration,
            environment=Environment(api_request.environment),
            requester=api_request.requester,
            provenance=api_request.provenance,
            # OSS intent also expects `intent_id` and `timestamp`, which are auto‑generated.
        )
    elif api_request.intent_type == "GrantAccessIntent":
        return GrantAccessIntent(
            principal=api_request.principal,
            permission_level=PermissionLevel(api_request.permission_level),
            resource_scope=api_request.resource_scope,
            justification=api_request.justification,
            requester=api_request.requester,
            provenance=api_request.provenance,
        )
    elif api_request.intent_type == "DeployConfigurationIntent":
        return DeployConfigurationIntent(
            service_name=api_request.service_name,
            change_scope=ChangeScope(api_request.change_scope),
            deployment_target=Environment(api_request.deployment_target),
            risk_level_hint=api_request.risk_level_hint,
            configuration=api_request.configuration,
            requester=api_request.requester,
            provenance=api_request.provenance,
        )
    else:
        raise ValueError(f"Unknown intent type: {api_request.intent_type}")
