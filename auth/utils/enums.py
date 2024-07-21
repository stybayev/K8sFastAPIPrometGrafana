from enum import Enum


class AuthProvider(str, Enum):
    YANDEX = "yandex"
    GOOGLE = "google"
