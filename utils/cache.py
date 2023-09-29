from django.core.cache import cache

def set_verification_code(email, code):
    key = f'verification_code_{email}'
    cache.set(key, code, 30*60)

def get_verification_code(email):
    key = f'verification_code_{email}'
    code = cache.get(key)
    cache.delete(key)
    return code