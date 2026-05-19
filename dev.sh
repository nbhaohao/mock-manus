docker compose up -d --wait
uvicorn app.main:app --reload --lifespan on
