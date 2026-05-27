import os

JWT_SECRET = os.getenv("JWT_SECRET", "change-this-secret-in-production-please")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60 * 24  # 24 hours
