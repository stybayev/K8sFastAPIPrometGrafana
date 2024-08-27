
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

app = FastAPI(
    # title=settings.project_name,
    docs_url="/api/rating/openapi",
    openapi_url="/api/rating/openapi.json",
    default_response_class=ORJSONResponse,
)


@app.get("/")
def read_root():
    return {"Hello": "World"}
