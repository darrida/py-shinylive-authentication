import json
from typing import Any, Literal, Optional, Union

from pydantic import BaseModel

# from shiny import ui


class HttpResponse(BaseModel):
    status: Union[str, int]
    data: Optional[Union[bytes, dict, str]] = None


class PyFetch(BaseModel):
    type: str
    status: Union[int, str]
    redirected: bool
    ok: bool
    data: Union[dict, str, int, bytes] = None
    response: Any

    def __str__(self):
        return f"{self.status}, {self.redirected}, {self.ok}, {self.data}, {self.type}, {self.response}"

    @staticmethod
    async def call(
        url: str, clone: bool = False, method: str = "GET", headers: dict = None, body: dict = None, 
        type_:str = "json", **kwargs
    ) -> "PyFetch":
        import pyodide  # type: ignore -> shows invalid, since it only works in when deployed as ShinyLive/pyodide/WASM

        if body:
            body = json.dumps(body)
            print(body)
        r = await pyodide.http.pyfetch(
            url,
            method=method,
            body=body,
            headers=headers,
            **kwargs
        )

        response = r.clone() if clone is True else r

        fetch = PyFetch(
            response = response,
            status = r.status,
            type = type_,
            ok = r.ok,
            redirected = r.redirected
        )
        
        # ui.notification_show(str(fetch), duration=100)

        if int(fetch.status) not in [200]:
            return fetch
            fetch.type = "string"

        if fetch.type == "json":
            fetch.data = await fetch.json()
        elif fetch.type == "string":
            fetch.data = await fetch.string()
        elif fetch.type == "bytes":
            fetch.data = await fetch.bytes()
        else:
            fetch.data = f"Response type not accounted for: {fetch.type}"
        return fetch

    async def json(self):
        return await self.response.json()

    async def string(self):
        return await self.response.string()

    async def buffer(self):
        return await self.response.bufFer()
    
    async def bytes(self):
        return await self.response.bytes()
    
    def raise_for_status(self):
        return self.response.raise_for_status()


# async def requests_download(url: str, headers: dict, method: Literal["POST", "GET", "PUT"], body: dict, **kwargs):
#     ...

# async def requests_json(url: str, headers: dict, method: Literal["POST", "GET", "PUT", "DELETE"], body: dict, **kwargs):
#     return await get_url(url=url, headers=headers, method=method, body=body, **kwargs)


# async def requests


async def get_url(
    url: str, headers: dict = None, clone: bool = False, 
    method: Literal["GET", "PUT", "POST", "DELETE"] = "GET", 
    type: Literal["string", "bytes", "json"] = "string", body: dict = None, **kwargs
) -> HttpResponse:
    """
    An async wrapper function for http requests that works in both regular Python and
    Pyodide.

    In Pyodide, it uses the pyodide.http.pyfetch() function, which is a wrapper for the
    JavaScript fetch() function. pyfetch() is asynchronous, so this whole function must
    also be async.

    In regular Python, it uses the urllib.request.urlopen() function.

    Args:
        url: The URL to download.

        type: How to parse the content. If "string", it returns the response as a
        string. If "bytes", it returns the response as a bytes object. If "json", it
        parses the reponse as JSON, then converts it to a Python object, usually a
        dictionary or list.

    Returns:
        A HttpResponse object
    """
    import sys

    if "pyodide" in sys.modules:
        response = await PyFetch.call(url=url, headers=headers, type_=type, clone=clone, method=method, body=body, **kwargs)
        return HttpResponse(status=response.status, data=response.data)
    else:
        import requests

        # print(118, headers)
        # print(119, body)

        resp = requests.request(
            method=method,
            url=url,
            headers=headers,
            json=body if type == "json" else None,
            data=body if type != "json" else None,
            allow_redirects=True
        )

        print(resp.text)
        if resp.status_code != 200:
            # type = "string"
            data = None
        else:
            if type == "json" and resp.ok:
                data = resp.json()
            elif type == "string":
                data = resp.text
            elif type == "csv":
                with open("test.csv", "wb") as f:
                    f.write(resp.text)
                data = "test.csv"
        # print(142, resp.status_code)
        # print(143, data)
        return HttpResponse(status=resp.status_code, data=data)