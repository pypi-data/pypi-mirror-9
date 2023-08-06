from django.conf import settings

CODE_GENERATOR = getattr(settings, 'SWANSON_CODE_GENERATOR', 'swanson.codegen.CodeGen')
