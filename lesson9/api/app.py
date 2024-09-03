from fastapi import FastAPI, APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.requests import Request
from pydantic import ValidationError
from starlette.responses import JSONResponse

from cvelist.config import settings
from cvelist.exceptions import ResourceDoesNotExist
from cvelist.modules.cve.routes import cve_router
from cvelist.services.database_service import create_async_engine, make_session_class


def handle_does_not_exist_404(request: Request, exc: ResourceDoesNotExist) -> JSONResponse:
    return JSONResponse(jsonable_encoder({"message": "Resource Not Found"}), status_code=404)


def handle_validation_error(request: Request, exc: ValidationError) -> JSONResponse:
    return JSONResponse(
        jsonable_encoder({"errors": [m["msg"] for m in exc.errors()]}), status_code=400
    )


def register_routes(app_: FastAPI) -> None:
    api_router = APIRouter(prefix="/api")
    api_router.include_router(cve_router)
    app_.include_router(api_router)


def register_database_service(app_: FastAPI) -> None:
    _engine = create_async_engine(settings.db_url)
    app_.engine = _engine
    app_.async_session_cls = make_session_class(_engine)


def register_error_handlers(app_: FastAPI) -> None:
    app_.add_exception_handler(ResourceDoesNotExist, handle_does_not_exist_404)
    app_.add_exception_handler(ValidationError, handle_validation_error)


def create_app() -> FastAPI:
    app_ = FastAPI()

    register_routes(app_)
    register_database_service(app_)
    register_error_handlers(app_)

    return app_


app = create_app()
