#!/bin/bash
set -e

# ==============================================================================
# DeepSeek V3.2 VM Deployment Script (Systemd)
#
# WARNING: DeepSeek V3.2 671B requires MASSIVE GPU resources.
# Typically, this requires 8x H100 (80GB) or similar hardware for inference.
# Ensure your VM has sufficient VRAM and the NVIDIA drivers / CUDA toolkit installed.
# ==============================================================================

APP_DIR="/opt/deepseek-v3.2"
USER="deepseek"
# Assuming the user has downloaded the HF weights to this path:
HF_CKPT_PATH="/path/to/huggingface/weights"
SAVE_PATH="${APP_DIR}/weights"
EXPERTS=256
# MP (Model Parallelism) should equal the number of GPUs you have
MP=8
CONFIG="config_671B_v3.2.json"

echo "Creating user $USER..."
id -u $USER &>/dev/null || sudo useradd -m -s /bin/bash $USER

echo "Setting up application directory at $APP_DIR..."
sudo mkdir -p $APP_DIR
# In a real deployment, you would git clone the repo here.
# For now, we assume the current directory contains the inference code.
sudo cp -r inference/* $APP_DIR/
sudo chown -R $USER:$USER $APP_DIR

echo "Installing Python dependencies..."
# Assumes modern Ubuntu/Debian with python3-pip and python3-venv installed
sudo apt-get update
sudo apt-get install -y python3-venv python3-pip
sudo -u $USER bash -c "cd $APP_DIR && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"

# Note: The model conversion step takes a long time and requires massive RAM.
# It is typically done before running the service.
# sudo -u $USER bash -c "cd $APP_DIR && source venv/bin/activate && python convert.py --hf-ckpt-path ${HF_CKPT_PATH} --save-path ${SAVE_PATH} --n-experts ${EXPERTS} --model-parallel ${MP}"

echo "Creating systemd service..."
sudo tee /etc/systemd/system/deepseek.service > /dev/null << EOL
[Unit]
Description=DeepSeek V3.2 Inference Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$APP_DIR
Environment="WORLD_SIZE=$MP"
Environment="CONFIG=$CONFIG"
# Since generate.py is interactive by default, to run as a service we must provide an input file
# Replace prompts.txt with your actual input file, or modify generate.py for an API server.
ExecStart=$APP_DIR/venv/bin/torchrun --nproc-per-node=$MP generate.py --ckpt-path $SAVE_PATH --config $CONFIG --input-file prompts.txt --max-new-tokens 200

Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOL

echo "Reloading systemd and enabling service..."
sudo systemctl daemon-reload
sudo systemctl enable deepseek.service

echo "Deployment script finished."
echo "IMPORTANT NEXT STEPS:"
echo "1. Ensure your HuggingFace weights are downloaded to $HF_CKPT_PATH"
echo "2. Run the conversion script (see comments in deploy_vm.sh)"
echo "3. Create a 'prompts.txt' file in $APP_DIR for the service to process"
echo "4. Adjust the MP (Model Parallelism) variable in the systemd service to match your GPU count"
echo "5. Start the service with: sudo systemctl start deepseek.service"
