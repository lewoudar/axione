import tempfile
import uuid
from pathlib import Path

import httpx

from .config import get_settings


async def get_httpx_client() -> httpx.AsyncClient:
    settings = get_settings()
    async with httpx.AsyncClient(
        follow_redirects=settings.httpx_follow_redirects,
        transport=httpx.AsyncHTTPTransport(retries=settings.httpx_number_of_retries),
    ) as client:
        yield client


def get_temporary_file() -> Path:
    tempdir = tempfile.gettempdir()
    file = Path(tempdir) / f'{uuid.uuid4()}.csv'
    file.write_text('note,INSEE,population,zip_code\n')
    yield file
    file.unlink()
