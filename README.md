# Rag - mvp

## Requirements

- Python 3.9 or later
- [uv](https://docs.astral.sh/uv/) (Python package installer)

## Installation

### Install the required packages

```bash
$ uv venv
$ source .venv/bin/activate
$ uv sync
```

### Setup the environment variables

```bash
$ cp .env.example .env
```
Then set your environment variables in the `.env` file. Like `OPENAI_API_KEY` value.

## Run Docker Compose Services, later would move tp make file

```bash
$ cd docker
$ cp .env.example .env
```

- update `.env` with your credentials



```bash
$ cd docker
$ sudo docker compose up -d
```

## Run the FastAPI server localy

```bash
$ uv -- uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

## POSTMAN Collection

Download the POSTMAN collection from 
