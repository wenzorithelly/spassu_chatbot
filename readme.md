#reference repository for AWS ECR-> ECS deployment

#alembic commands 
docker compose run --rm web alembic revision --autogenerate -m "description" 

docker compose run --rm web alembic upgrade head



# Setup Instructions

### Create Virtual Environment
To create a virtual environment, run the following command:


#alembic commands 

docker compose run --rm spassu_chatbot alembic init alembic

docker compose run --rm spassu_chatbot alembic revision --autogenerate -m "description" 

docker compose run --rm spassu_chatbot alembic upgrade head




```bash
python -m venv .venv
```



### Activate Environment
Activate the virtual environment using the appropriate command for your operating system:

- **Windows:**
  ```bash
  source ./.venv/Scripts/activate
  ```

- **macOS/Linux:**
  ```bash
  source ./.venv/bin/activate
  ```
