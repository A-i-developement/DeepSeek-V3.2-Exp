# DeepSeek 671B Inference Deployment Instructions

This document provides instructions on how to deploy this optimized DeepSeek 671B inference code on a GPU cloud provider using the provided Docker container. Running a model of this size requires significant VRAM, typically multiple high-end GPUs like 8x H100s or 8x A100s.

## Option 1: RunPod / Lambda Labs (Recommended for Ease of Use)

1. **Spin up a GPU Instance:**
   Go to RunPod or Lambda Labs and rent an instance with sufficient GPU memory (e.g., a node with 8x H100s or 8x A100s). Make sure you select an image with PyTorch and CUDA pre-installed.

2. **Clone the Codebase:**
   SSH into your instance (which you can do via Termius or similar apps on your phone) and clone this codebase.

   ```bash
   git clone <your-repo-url>
   cd <your-repo-name>
   ```

3. **Build the Docker Image:**
   ```bash
   docker build -t deepseek-inference .
   ```

4. **Download the Model Checkpoints:**
   Download the DeepSeek V3 model checkpoints (safetensors) and config to a local directory, e.g., `/mnt/data/deepseek-v3/`.

5. **Run the Container Interactively:**
   ```bash
   docker run --gpus all -it \
       -v /mnt/data/deepseek-v3:/model \
       deepseek-inference \
       --ckpt-path /model \
       --config /model/config_671B_v3.2.json \
       --interactive
   ```
   This will mount the model directory into the container and start the interactive prompt (`>>> `) where you can type your questions from your phone.

## Option 2: AWS EC2 (Advanced)

1. Spin up a `p5.48xlarge` (8x H100) or `p4d.24xlarge` (8x A100) instance.
2. Use the Deep Learning AMI GPU PyTorch (Ubuntu).
3. Connect via SSH.
4. Follow steps 2-5 from Option 1 to build and run the container.

## Handling Out-Of-Memory (OOM) Errors
If you run out of GPU memory, ensure that you have downloaded the correct quantized weights or are using model parallelism correctly across all available GPUs. The script will automatically detect `WORLD_SIZE` for distributed GPU setup if you run it with torchrun:

```bash
docker run --gpus all -it \
    -v /mnt/data/deepseek-v3:/model \
    --entrypoint torchrun \
    deepseek-inference \
    --nproc_per_node 8 \
    inference/generate.py \
    --ckpt-path /model \
    --config /model/config_671B_v3.2.json \
    --interactive
```
