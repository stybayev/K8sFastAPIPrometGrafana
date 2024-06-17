from miniopy_async import Minio

client: Minio | None = None


def set_minio(minio_client: Minio) -> None:
    global client
    client = minio_client


def get_minio() -> Minio:
    if client is None:
        raise RuntimeError("Minio client is not initialized. Call set_minio first.")
    return client


async def close_minio() -> None:
    global client
    if client is not None:
        client = None


async def create_bucket_if_not_exists(bucket_name: str) -> None:
    minio_client = get_minio()
    found = await minio_client.bucket_exists(bucket_name)
    if not found:
        await minio_client.make_bucket(bucket_name)
