import os

from supabase import Client, create_client


class SupabaseStorageClient:
    def __init__(self) -> None:
        self._client: Client = create_client(
            os.environ["SUPABASE_URL"],
            os.environ["SUPABASE_KEY"],
        )
        self._bucket = os.environ["SUPABASE_BUCKET"]

    def upload(
        self, file_path: str, file_data: bytes, content_type: str
    ) -> str:
        """Upload file, return its public URL."""
        self._client.storage.from_(self._bucket).upload(
            path=file_path,
            file=file_data,
            file_options={"content-type": content_type},
        )
        return self._client.storage.from_(self._bucket).get_public_url(
            file_path
        )

    def delete_by_url(self, public_url: str) -> None:
        """Delete a file given its public URL.

        Extracts the storage path from the URL and removes it from the bucket.
        """
        # URL format: .../storage/v1/object/public/<bucket>/<path>
        marker = f"/object/public/{self._bucket}/"
        if marker in public_url:
            file_path = public_url.split(marker, 1)[1]
            self._client.storage.from_(self._bucket).remove([file_path])
