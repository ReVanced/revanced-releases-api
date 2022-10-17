from fastapi import APIRouter, Request, Response

router = APIRouter()

@router.head('/ping', status_code=204, tags=['Ping'])
async def ping(request: Request, response: Response) -> None:
    """Check if the API is running.

    Returns:
        None
    """
    return None
