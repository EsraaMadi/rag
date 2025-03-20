# Rag - mvp

## Requirements

- Python 3.9 or later
- [uv](https://docs.astral.sh/uv/) (Python package installer)

## Installation

### 1. Install the required packages

```bash
$ uv venv
$ source .venv/bin/activate
$ uv sync
```

### 2. Setup the environment variables

```bash
$ cp .env.example .env
```
Then set your environment variables in the `.env` file. Like `OPENAI_API_KEY` value and others.

### 3. Run Docker Compose Services, later would move tp make file

```bash
$ cd docker
$ cp .env.example .env
```
Then set your credential for postgre database.
Run docker containers:
```bash
$ sudo docker compose up -d
```

### 4.Run the FastAPI server localy

```bash
$ uv run -- uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

## POSTMAN Collection

Note: Yo can Find the POSTMAN collection for developed APIs in `assets` folder

