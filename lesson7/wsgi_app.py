import functools
from dataclasses import dataclass
from typing import Callable

_routes: dict[tuple[str, str], Callable] = {}
SUCCESS_STATUS_CODES: dict[int, str] = {200: "OK"}


class HttpError(Exception):
    status_code = None
    error_message = None


class NotFoundError(HttpError):
    status_code = 404
    error_message = "Not Found"


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
def hello_world(request: Request) -> tuple[str, int]:
    return "<h1>Hello, World!</h1>", 200


def app(env, start_response):
    http_method = env["REQUEST_METHOD"]
    http_path = env["PATH_INFO"]
    query_string = env["QUERY_STRING"]

    try:
        content_length = int(env.get("CONTENT_LENGTH", 0))
    except (ValueError, TypeError):
        content_length = 0
    body = env["wsgi.input"].read(content_length).decode() if content_length > 0 else None
    request = Request(body=body, query_params=query_string)

    try:
        controller = routes_dispatcher(http_method, http_path)
        response, status_code = controller(request)
    except HttpError as exc:
        response = str(exc)
        start_response(f"{exc.status_code} {exc.error_message}", [("Content-Type", "text/html")])
    else:
        start_response(
            f"{status_code} {SUCCESS_STATUS_CODES[status_code]}", [("Content-Type", "text/html")]
        )

    return [response.encode()]
