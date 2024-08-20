import functools
from dataclasses import dataclass
from typing import Callable

_routes: dict[tuple[str, str], Callable] = {}


class HttpError(Exception):
    status_code = None


class NotFoundError(HttpError):
    status_code = 404


@dataclass
class Request:
    body: dict | None
    query_params: dict | None


def register_route(method: str, path: str) -> Callable:
    def decorator(func) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            return result

        global _routes
        _routes[(method, path)] = wrapper
        return wrapper

    return decorator


def routes_dispatcher(method: str, path: str) -> Callable:
    controller = _routes.get((method, path))
    if not controller:
        raise NotFoundError(f"Url <b>{path}</b> is not found")
    return controller


@register_route("GET", path="/")
async def hello_world(request: Request) -> tuple[str, int]:
    return "<h1>Hello, World!</h1>", 200


async def app(scope, receive, send):
    if scope["type"] != "http":
        return

    http_method = scope["method"]
    http_path = scope["path"]
    query_string = scope["query_string"].decode() or None
    data = await receive()
    body = data["body"].decode() or None
    request = Request(body=body, query_params=query_string)

    try:
        controller = routes_dispatcher(http_method, http_path)
        response, status_code = await controller(request)
    except HttpError as exc:
        response = str(exc)
        status_code = exc.status_code

    await send(
        {
            "type": "http.response.start",
            "status": status_code,
            "headers": [
                [b"content-type", b"text/html"],
            ],
        }
    )
    await send(
        {
            "type": "http.response.body",
            "body": response.encode(),
        }
    )
