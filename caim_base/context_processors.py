from django.conf import settings

# These variables are always inserted into all page templates
def global_template_variables(request):
    return {
        "isProduction": settings.PRODUCTION,
    }
