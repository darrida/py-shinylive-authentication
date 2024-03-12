# wrapper around pyfetch that matches pyodide.http.pyfetch
import copy
import json
import logging
import re
import shutil
from dataclasses import dataclass
from io import BytesIO
from typing import Literal

import httpx


@dataclass
class FetchResponse:
    headers: dict
    url: str
    ok: bool
    redirected: bool
    status: int
    # type: str
    status_text: str
    body_used: bool
    do_not_use_body: bytes

    # unit-tested
    async def string(self) -> str:
        return await self._text()

    async def text(self) -> str:
        return await self._text()

    # unit-tested
    async def _text(self) -> str:
        return self.do_not_use_body.decode()

    async def buffer(self):
        logging.warning("`httpx_http.FetchResponse.buffer()` is not yet implimented for non-pyodide version")

    # unit-tested
    async def bytes(self) -> bytes:
        return bytes(self.do_not_use_body)

    # unit-tested
    async def json(self) -> dict:
        return json.loads(self.do_not_use_body)

    async def memoryview(self):
        logging.warning("`httpx_http.FetchResponse.memoryview()` is not yet implimented for non-pyodide version")

    async def unpack_archive(self, extract_dir: str, format: Literal["zip", "tar", "gztar", "bztar", "xztar"]):
        # treat data as an archive and unpack into target directory
        with BytesIO(self.bytes()) as file_buffer:
            shutil.unpack_archive(file_buffer, extract_dir=extract_dir, format=format)
        # shutil.unpack_archive(self.do_not_use_body, extract_dir=extract_dir, format=format)

    def raise_for_status(self):
        if self.status >= 400:
            raise OSError(
                f"Request failed due to local issue. Status code: {self.status}. Status text: {self.status_text}"
            )

    def clone(self) -> "FetchResponse":
        return copy.copy(self, deepcopy=True)


class http:
    @staticmethod
    async def pyfetch(
        url: str, 
        headers: dict,
        method: Literal["GET", "POST", "PUT", "DELETE", "PATCH"] = "GET",
        credentials: Literal["omit", "same-origin", "include"] = None,
        body: str = None,
        redirect: bool = True,
    ) -> FetchResponse:

        if credentials:
            logging.warning(
                "`credentials` parameter doesn't do anything when running outside of browser. "
                "Separate testing required."
            )

        request_arguments = {
            "method": method, 
            "url": url, 
            "headers": headers, 
            "follow_redirects": redirect,
            "content": body
        }

        async with httpx.AsyncClient() as client:
            r = await client.request(**request_arguments)

        ok = True if r.status_code >= 100 and r.status_code < 400 else False
        redirected = True if r.status_code >= 300 and r.status_code < 400 else False

        return FetchResponse(
            headers=r.headers,
            url=r.url,
            redirected=redirected,
            status=r.status_code,
            status_text=str(r.status_code),
            do_not_use_body=r.content,
            ok=ok,
            body_used=False
            # type=None
        )