from fastapi import APIRouter, Request, Response, status
from fastapi.responses import RedirectResponse

router = APIRouter()

@router.get("/", response_class=RedirectResponse,
         status_code=status.HTTP_301_MOVED_PERMANENTLY, tags=['Root'])
async def root(request: Request, response: Response) -> RedirectResponse:
    """Brings up API documentation

    Returns:
        None: Redirects to /docs
    """
    return RedirectResponse(url="/docs")
