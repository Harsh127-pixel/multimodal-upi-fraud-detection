#!/bin/bash
echo "Setting up repository..."
git lfs install
cp fraudguard-backend/.env.example fraudguard-backend/.env
cp fraudguard-frontend/.env.example fraudguard-frontend/.env
mkdir -p fraudguard-backend/app/models
mkdir -p fraudguard-backend/uploads
mkdir -p fraudguard-backend/ml_training/data
touch fraudguard-backend/app/models/.gitkeep
touch fraudguard-backend/uploads/.gitkeep
touch fraudguard-backend/ml_training/data/.gitkeep
echo "Setup complete! Next steps:"
echo "1. Update your .env files with actual values."
echo "2. Run docker-compose up -d in the backend folder."
