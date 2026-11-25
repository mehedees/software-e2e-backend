from pydantic import BaseModel

# These models have comments instead of docstrings on purpose: Pydantic copies a
# model's docstring into the OpenAPI schema `description`, which would publish
# these developer notes in `/docs`.


# `data` payload for endpoints with nothing to return: serializes to `{}`.
class DataEmpty(BaseModel):
    pass


# Success envelope (2xx): `{"data": ...}`.
#
# Success and error bodies never share fields; the HTTP status tells the
# client which one it got. Clients decode `APIResponse[T]` on 2xx and
# `APIErrorResponse` otherwise, so `data` is never null on the success path
# and there is no `code`/`message` dead weight (the status already says OK,
# and UI copy belongs to the client).
#
# Set `T` to the endpoint's payload type; the return annotation drives
# validation, serialization and OpenAPI.
#
#     class UserOut(BaseModel):
#         id: int
#         name: str
#
# a. Single object:
#
#     @router.get("/users/{user_id}")
#     async def get_user(user_id: int) -> APIResponse[UserOut]:
#         return APIResponse(data=UserOut(id=user_id, name="Ada"))
#     # -> {"data": {"id": 1, "name": "Ada"}}
#
# b. List:
#
#     @router.get("/users")
#     async def list_users() -> APIResponse[list[UserOut]]:
#         return APIResponse(data=[UserOut(id=1, name="Ada")])
#     # -> {"data": [{"id": 1, "name": "Ada"}]}
#
# c. Created (non-200 status): set `status_code` on the route:
#
#     @router.post("/users", status_code=status.HTTP_201_CREATED)
#     async def create_user(body: UserIn) -> APIResponse[UserOut]:
#         return APIResponse(data=await users.create(body))
#     # -> 201 {"data": {"id": 2, ...}}
#
# d. No payload (delete, action endpoints): use `APIResponse[DataEmpty]` so
#    `data` is still a non-null object. Don't use 204: an empty body breaks
#    clients that decode every 2xx as `{"data": ...}`. Return something
#    meaningful instead (e.g. the deleted id) when the client can use it.
#
#     @router.delete("/users/{user_id}")
#     async def delete_user(user_id: int) -> APIResponse[DataEmpty]:
#         await users.delete(user_id)
#         return APIResponse(data=DataEmpty())
#     # -> 200 {"data": {}}
#
# e. Paginated list: wrap items and paging info in a generic model:
#
#     class Page[I](BaseModel):
#         items: list[I]
#         total: int
#         page: int
#         size: int
#
#     @router.get("/users")
#     async def list_users(page: int = 1, size: int = 20) -> APIResponse[Page[UserOut]]:
#         items, total = await users.list(page=page, size=size)
#         return APIResponse(data=Page(items=items, total=total, page=page, size=size))
#     # -> {"data": {"items": [...], "total": 42, "page": 1, "size": 20}}
#
# f. Plain value: `T` can be any type Pydantic understands:
#
#     @router.get("/users/count")
#     async def count_users() -> APIResponse[int]:
#         return APIResponse(data=await users.count())
#     # -> {"data": 42}
#
# g. Named response schema: subclass a parametrized `APIResponse` to reuse
#    it across routes and get a clean OpenAPI schema name (`UserResponse`
#    instead of `APIResponse_UserOut_`):
#
#     class UserResponse(APIResponse[UserOut]):
#         pass
#
#     @router.get("/users/{user_id}")
#     async def get_user(user_id: int) -> UserResponse:
#         return UserResponse(data=UserOut(id=user_id, name="Ada"))
#
# Errors: raise `APIException` (see `APIErrorResponse`).
class APIResponse[T](BaseModel):
    data: T


# One problem with a request, usually tied to a single input field.
#
# Used for 422 validation errors (built automatically by the
# `RequestValidationError` handler) and for your own business-rule errors:
#
#     ErrorDetail(field="body.email", message="Email already taken", code="duplicate")
#     ErrorDetail(message="Account is locked")  # not tied to a field
class ErrorDetail(BaseModel):
    field: str | None = None  # dotted location, e.g. "body.email", "query.page"
    message: str
    code: str | None = None  # machine-readable code, e.g. "missing", "duplicate"


# Error envelope (4xx/5xx): `{"code", "message", "errors"}`.
#
# Every error the API returns has this shape, including validation errors,
# unknown routes / wrong methods and unhandled exceptions (see
# `core.bootstrap.exception_handlers`). All keys are always present and
# `errors` is always a list (empty if there are no details).
#
# Clients should branch on `code` (and localize their own copy);
# `message` is a human-readable fallback.
#
# 1. Raise `APIException` from an endpoint:
#
#     raise APIException(status_code=404, code="NOT_FOUND", message="User not found")
#     # -> 404 {"code": "NOT_FOUND", "message": "User not found", "errors": []}
#
#     raise APIException(
#         status_code=409,
#         code="CONFLICT",
#         message="Could not create user",
#         errors=[ErrorDetail(field="body.email", message="Email already taken")],
#     )
#     # -> 409 {"code": "CONFLICT", "message": "Could not create user",
#     #         "errors": [{"field": "body.email", "message": "Email already taken", "code": null}]}
#
# 2. Request validation (422): nothing to do in endpoints; returned as:
#
#     {
#         "code": "VALIDATION_ERROR",
#         "message": "Invalid request",
#         "errors": [
#             {"field": "body.email", "message": "Field required", "code": "missing"}
#         ]
#     }
#
# 3. `HTTPException` (incl. routing 404/405): `code` is the status name,
#    e.g. `{"code": "METHOD_NOT_ALLOWED", "message": "Method Not Allowed", "errors": []}`.
#
# 4. Unhandled exception: 500 `{"code": "INTERNAL_ERROR", "message":
#    "Internal Server Error", "errors": []}`; details are logged, not sent.
#
# OpenAPI: routes registered through `core.router.APIRouter` get a 422 with
# this model automatically (see `core.router`). Declare other error statuses
# per route:
#
#     @router.post("/users", responses={409: {"model": APIErrorResponse}})
class APIErrorResponse(BaseModel):
    code: str
    message: str
    errors: list[ErrorDetail] = []


class InternalServerError(APIErrorResponse):
    code: str = "INTERNAL_ERROR"
    message: str = "Internal Server Error"


# Errors generated from firewalls
class FirewallError(BaseModel):
    supportID: str  # noqa
