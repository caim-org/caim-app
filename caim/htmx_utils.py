import copy

from django.http.request import HttpRequest, QueryDict
from django.http.response import HttpResponse
from django.utils.functional import wraps
from render_block import render_block_to_string


def for_htmx(
    *,
    if_hx_target: str | None = None,
    use_template: str | None = None,
    use_block: str | list[str] | None = None,
    use_block_from_params: bool = False,
):
    """
    If the request is from htmx, then render a partial page, using either:
    - the template specified in `use_template` param
    - the block/blocks specified in `use_block` param
    - the block/blocks specified in GET/POST parameter "use_block", if `use_block_from_params=True` is passed

    If the optional `if_hx_target` parameter is supplied, the
    hx-target header must match the supplied value as well in order
    for this decorator to be applied.

    Copied from https://github.com/spookylukey/django-htmx-patterns/blob/master/code/htmx_patterns/utils.py
    with some minor changes to leverage django-htmx middleware
    """
    if len([p for p in [use_block, use_template, use_block_from_params] if p]) != 1:
        raise ValueError("You must pass exactly one of 'use_template', 'use_block' or 'use_block_from_params=True'")

    def decorator(view):
        @wraps(view)
        def _view(request, *args, **kwargs):
            resp = view(request, *args, **kwargs)
            if request.htmx:
                if if_hx_target is None or request.htmx.target == if_hx_target:
                    blocks_to_use = use_block
                    if not hasattr(resp, "render"):
                        if not resp.content and any(
                            h in resp.headers
                            for h in (
                                "Hx-Trigger",
                                "Hx-Trigger-After-Swap",
                                "Hx-Trigger-After-Settle",
                                "Hx-Redirect",
                            )
                        ):
                            # This is a special case response, it doesn't need modifying:
                            return resp

                        raise ValueError("Cannot modify a response that isn't a TemplateResponse")
                    if resp.is_rendered:
                        raise ValueError("Cannot modify a response that has already been rendered")

                    if use_block_from_params:
                        use_block_from_params_val = _get_param_from_request(request, "use_block")
                        if use_block_from_params_val is not None:
                            blocks_to_use = use_block_from_params_val

                    if use_template is not None:
                        resp.template_name = use_template
                    elif blocks_to_use is not None:
                        if not isinstance(blocks_to_use, list):
                            blocks_to_use = [blocks_to_use]

                        rendered_blocks = [
                            render_block_to_string(resp.template_name, b, context=resp.context_data, request=request)
                            for b in blocks_to_use
                        ]
                        # Create new simple HttpResponse as replacement
                        resp = HttpResponse(
                            content="".join(rendered_blocks),
                            status=resp.status_code,
                            headers=resp.headers,
                        )

            return resp

        return _view

    return decorator
