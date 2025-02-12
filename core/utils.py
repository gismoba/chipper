import random
import string
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from urllib.parse import urljoin


def random_string_generator(size=10, chars=string.ascii_letters + string.digits):
    return "".join(random.choice(chars) for _ in range(size))


def unique_code_generator(instance):
    new_code = random_string_generator(size=8)

    Klass = instance.__class__
    qs_exists = Klass.objects.filter(code=new_code).exists()
    if qs_exists:
        return unique_code_generator(instance)
    return new_code


def unique_password_generator(instance):
    new_password = random_string_generator(size=8)

    Klass = instance.__class__
    qs_exists = Klass.objects.filter(password=new_password).exists()
    if qs_exists:
        return unique_code_generator(instance)
    return new_password



def handle_uploaded_file(request, f):
    file_name = default_storage.save(f.name, ContentFile(f.read()))
    relative_url = default_storage.url(file_name)
    absolute_url = request.build_absolute_uri(relative_url)
    return absolute_url


def get_form_errors(form):
    error_messages = []
    for field, errors in form.errors.items():
        for error in errors:
            error_messages.append(f"{field}: {error}")
    return error_messages
