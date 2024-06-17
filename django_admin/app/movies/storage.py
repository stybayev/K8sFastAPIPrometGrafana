import os
import requests
import uuid
from django.core.files.storage import Storage
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils.deconstruct import deconstructible
from config.settings import FILE_SERVICE_URL


@deconstructible
class CustomStorage(Storage):
    def _save(self, name, content: InMemoryUploadedFile):
        # Генерация уникального имени файла
        unique_name = f"{uuid.uuid4()}_{os.path.basename(name)}"
        r = requests.post(
            f"{FILE_SERVICE_URL}/upload/?path={unique_name}",
            files={"file": (content.name, content, content.content_type)},
        )
        response_data = r.json()
        return response_data.get("short_name")

    def url(self, name):
        return f"{FILE_SERVICE_URL}/download/{name}"

    def exists(self, name):
        return False
