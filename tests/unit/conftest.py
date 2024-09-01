pytest_plugins = [
    'tests.unit.fixtures.base_async',
    'tests.unit.fixtures.mock_minio',
    'tests.unit.fixtures.mock_db',
    'tests.unit.fixtures.file_service',
    'tests.unit.fixtures.auth_service',
    'tests.unit.fixtures.mock_redis',
    'tests.unit.fixtures.auth_role_service',
    'tests.unit.fixtures.rating_review_service',
]
