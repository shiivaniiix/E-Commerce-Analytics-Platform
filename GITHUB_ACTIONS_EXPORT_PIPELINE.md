# GitHub Actions Export Pipeline

This workflow automatically exports ecommerce data from PostgreSQL as CSV files and uploads them to AWS S3.

## Workflow File

- `.github/workflows/export_pipeline.yml`

## What it does

- Triggers on `push` to `main`
- Also supports manual execution with `workflow_dispatch`
- Sets up Python 3.12
- Installs dependencies from `backend/requirements.txt`
- Runs the export pipeline script at `backend/export_data.py`
- Uses GitHub Secrets for database and AWS credentials

## Required GitHub Secrets

Create the following repository secrets in GitHub:

- `PG_HOST` — PostgreSQL hostname or endpoint
- `PG_PORT` — PostgreSQL port (usually `5432`)
- `PG_DATABASE` — Database name
- `PG_USER` — Database username
- `PG_PASSWORD` — Database password
- `AWS_ACCESS_KEY_ID` — AWS access key ID
- `AWS_SECRET_ACCESS_KEY` — AWS secret access key
- `AWS_S3_BUCKET` — S3 bucket name for export files
- `AWS_S3_REGION` — S3 region (for example, `us-east-1`)
- `AWS_S3_PREFIX` — Optional S3 prefix/folder path (for example, `ecommerce_exports`)

### How to add secrets

1. In your GitHub repository, go to `Settings` > `Secrets and variables` > `Actions`.
2. Click `New repository secret`.
3. Add the secret name and value.
4. Save each secret.

## Environment variables used by workflow

The workflow passes the following environment variables into the export process:

- `DATABASE_URL` — built from PostgreSQL secrets
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_S3_BUCKET`
- `AWS_S3_REGION`
- `AWS_S3_PREFIX`
- `EXPORT_FOLDER` — local export folder inside the runner

## Project Folder Structure for Export Pipeline

```
backend/
  app/
    export/
      __init__.py
      export_pipeline.py
      logging_config.py
      postgres_utils.py
      s3_utils.py
  export_data.py
  requirements.txt
  .env.example
.github/
  workflows/
    export_pipeline.yml
GITHUB_ACTIONS_EXPORT_PIPELINE.md
```

### Important backend paths

- `backend/export_data.py` — main runner for the export pipeline
- `backend/app/export/export_pipeline.py` — core export logic
- `backend/app/export/postgres_utils.py` — PostgreSQL engine setup
- `backend/app/export/s3_utils.py` — AWS S3 upload helper
- `backend/app/export/logging_config.py` — export pipeline logging
- `backend/requirements.txt` — Python dependencies for the pipeline

## Notes

- The workflow installs dependencies from `backend/requirements.txt` so the export pipeline runs in the same environment as the backend.
- The pipeline uses `DATABASE_URL` and AWS credentials from GitHub Secrets.
- Local CSV output is written to `exports/` inside the runner and then uploaded to S3.
- No database credentials are stored in source control.
