import uvicorn
from config import get_config


"""
Application is run from the root of the project directory with `python3 app/main.py`
`"create_app:app"` is the module passed to uvicorn, to keep live reload ability and path import structure
for the application.
"""

if __name__ == "__main__":
    conf = get_config()
    uvicorn.run(
        "create_app:app",
        host=conf.HOST,
        port=conf.PORT,
        debug=(conf.API_ENV != "PRODUCTION"),
        reload=(conf.API_ENV != "PRODUCTION"),
        access_log=False,  # disabled in favor of logging middleware
    )
