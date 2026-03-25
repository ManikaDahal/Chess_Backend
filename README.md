---
title: Chess Backend
emoji: ♟️
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

# Chess Backend

Django backend for the Chess application, prepared for deployment on Hugging Face Spaces.

## Deployment Info
This Space is configured to run using the Docker SDK. It listens on port 7860 as required by Hugging Face.

## Environment Variables Needed
- `SECRET_KEY`
- `DATABASE_URL`
- `DEBUG` (set to `False`)
- `EMAIL_HOST`, `EMAIL_USER`, `EMAIL_PASS`, etc.
