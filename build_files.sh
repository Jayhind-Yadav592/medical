#!/bin/bash
echo "Building Antixor MedOS for Vercel Deployment..."
python3.11 -m pip install -r requirements.txt
python3.11 manage.py collectstatic --noinput --clear
echo "Build completed successfully!"
