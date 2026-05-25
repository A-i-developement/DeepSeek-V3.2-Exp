FROM pytorch/pytorch:2.2.1-cuda12.1-cudnn8-runtime

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy local inference code to container
COPY inference /app/inference

# Install python requirements
RUN pip install --no-cache-dir -r /app/inference/requirements.txt

# Run generation script interactively by default
ENTRYPOINT ["python", "inference/generate.py"]
CMD ["--interactive"]
