# Imports
import uvicorn
from fastapi import FastAPI, status
from db import models
from db.db import engine
from routes import users_route, entries_route, admin_routes, manager_routes
from auth import user_authentication, admin_authentication, manager_authentication
from fastapi_pagination import add_pagination

# App Initialization
app = FastAPI()

# Wrap the app  for pagination support
add_pagination(app)


# Health Check
@app.get("/", tags=["Health Check"])
def health_check():
    return {"status": status.HTTP_200_OK, "message": "Server is up and running!"}


# Add routers
app.include_router(users_route.router)
app.include_router(entries_route.router)
app.include_router(admin_routes.router)
app.include_router(manager_routes.router)

# Login Routes
app.include_router(user_authentication.router)
app.include_router(admin_authentication.router)
app.include_router(manager_authentication.router)

# Mount the model to create the database
models.Base.metadata.create_all(engine)

# Command to run the program
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
