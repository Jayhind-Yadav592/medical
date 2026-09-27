#!/bin/bash
echo "Building Antixor MedOS for Vercel Deployment..."

# Ensure staticfiles directory exists
mkdir -p staticfiles

# Install dependencies using python3
python3 -m pip install -r requirements.txt

# Collect static files into staticfiles/
python3 manage.py collectstatic --noinput --clear

echo "Build completed successfully!"
