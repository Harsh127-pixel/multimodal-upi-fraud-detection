#!/bin/bash
echo "Setting up local project for a new team member..."
git lfs install
cp fraudguard-backend/.env.example fraudguard-backend/.env
cp fraudguard-frontend/.env.example fraudguard-frontend/.env
mkdir -p fraudguard-backend/app/models
mkdir -p fraudguard-backend/uploads
mkdir -p fraudguard-backend/ml_training/data
touch fraudguard-backend/app/models/.gitkeep
touch fraudguard-backend/uploads/.gitkeep
touch fraudguard-backend/ml_training/data/.gitkeep
echo "Setup complete. Configure your .env files and run docker compose up -d"
