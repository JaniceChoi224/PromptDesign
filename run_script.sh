#!/bin/zsh

# Activate conda environment
source ~/miniconda3/etc/profile.d/conda.sh
conda activate choick

# Start the FastAPI backend
echo "Starting FastAPI backend..."
uvicorn main:app --reload &

# Start the frontend (index.html)
echo "Starting frontend..."
python -m http.server 3000 --directory .

# Wait for both processes to end
wait