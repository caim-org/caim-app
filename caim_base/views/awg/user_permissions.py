from typing import Any, Dict, List, Optional
from django.core.exceptions import PermissionDenied

from caim_base.models.awg import Awg


def check_awg_user_permissions_update_context(
    request,
    awg: Awg,
    required_permissions: Optional[List[str]],
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    context = context if context is not None else {}
    current_user_permissions = awg.get_permissions_for_user(request.user)

    if required_permissions is not None:
        for perm in required_permissions:
            if not perm in current_user_permissions:
                raise PermissionDenied("User does not have all required permissions")

    if "currentUserPermissions" in context.keys():
        if context["currentUserPermissions"] != current_user_permissions:
            raise KeyError(
                "currentUserPermissions is already assigned, and is different to what was queried!"
            )
    else:
        context["currentUserPermissions"] = current_user_permissions
    return context
