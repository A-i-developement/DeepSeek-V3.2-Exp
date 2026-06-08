import os
import json
import argparse
from typing import List

import torch
import torch.distributed as dist
from transformers import AutoTokenizer
from safetensors.torch import load_model

from model import Transformer, ModelArgs
from utils import dist_print

MIN_TEMPERATURE = 1e-5
SYNC_INTERVAL = 16

def sample(logits, temperature: float = 1.0):
    logits = logits / max(temperature, MIN_TEMPERATURE)
    probs = torch.softmax(logits, dim=-1, dtype=torch.float32)
    return probs.div_(torch.empty_like(probs).exponential_(1)).argmax(dim=-1)

@torch.inference_mode()
def generate(
    model: Transformer,
    prompt_tokens: List[List[int]],
    max_new_tokens: int,
    eos_id: int,
    temperature: float = 1.0
) -> List[List[int]]:
    prompt_lens = [len(t) for t in prompt_tokens]
    if max(prompt_lens) > model.max_seq_len:
        raise ValueError(f"Prompt length exceeds model maximum sequence length (max_seq_len={model.max_seq_len})")
    total_len = min(model.max_seq_len, max_new_tokens + max(prompt_lens))
    tokens = torch.full((len(prompt_tokens), total_len), -1, dtype=torch.long, device="cuda")
    for i, t in enumerate(prompt_tokens):
        tokens[i, :len(t)] = torch.tensor(t, dtype=torch.long, device="cuda")
    prev_pos = 0
    finished = torch.tensor([False] * len(prompt_tokens), device="cuda")
    prompt_mask = tokens != -1
    min_prompt_len = min(prompt_lens)
    for cur_pos in range(min_prompt_len, total_len):
        logits = model.forward(tokens[:, prev_pos:cur_pos], prev_pos)
        if temperature > 0:
            next_token = sample(logits, temperature)
        else:
            next_token = logits.argmax(dim=-1)
        next_token = torch.where(prompt_mask[:, cur_pos], tokens[:, cur_pos], next_token)
        tokens[:, cur_pos] = next_token
        finished |= torch.logical_and(~prompt_mask[:, cur_pos], next_token == eos_id)
        prev_pos = cur_pos
        if cur_pos % SYNC_INTERVAL == 0 and finished.all():
            break

    tokens_cpu = tokens.to("cpu")
    completion_tokens = []
    for i, toks in enumerate(tokens_cpu):
        toks = toks.tolist()[prompt_lens[i]:prompt_lens[i]+max_new_tokens]
        if eos_id in toks:
            toks = toks[:toks.index(eos_id)]
        completion_tokens.append(toks)
    return completion_tokens

def main(args: argparse.Namespace) -> None:
    world_size = int(os.getenv("WORLD_SIZE", "1"))
    rank = int(os.getenv("RANK", "0"))
    local_rank = int(os.getenv("LOCAL_RANK", "0"))
    if world_size > 1:
        dist.init_process_group("nccl")
    torch.cuda.set_device(local_rank)
    torch.set_default_dtype(torch.bfloat16)
    torch.set_num_threads(8)
    torch.manual_seed(33377335)
    with open(args.config) as f:
        model_args = ModelArgs(**json.load(f))
    dist_print(model_args)
    with torch.device("cuda"):
        model = Transformer(model_args)
    tokenizer = AutoTokenizer.from_pretrained(args.ckpt_path)
    dist_print("load model")
    load_model(model, os.path.join(args.ckpt_path, f"model{rank}-mp{world_size}.safetensors"))
    dist_print("I'm DeepSeek 👋")

    if args.interactive:
        messages = []
        while True:
            try:
                if world_size == 1:
                    prompt = input(">>> ")
                elif rank == 0:
                    try:
                        prompt = input(">>> ")
                    except (EOFError, KeyboardInterrupt):
                        prompt = "/exit"
                    objects = [prompt]
                    dist.broadcast_object_list(objects, 0)
                else:
                    objects = [None]
                    dist.broadcast_object_list(objects, 0)
                    prompt = objects[0]
            except (EOFError, KeyboardInterrupt):
                prompt = "/exit"
            if prompt == "/exit":
                break
            elif prompt == "/clear":
                messages.clear()
                continue
            user_msg = {"role": "user", "content": prompt}
            messages.append(user_msg)
            prompt_tokens = tokenizer.apply_chat_template(messages, add_generation_prompt=True)
            completion_tokens = generate(model, [prompt_tokens], args.max_new_tokens, tokenizer.eos_token_id, args.temperature)
            completion = tokenizer.decode(completion_tokens[0], skip_special_tokens=True)
            dist_print(completion)
            messages.append({"role": "assistant", "content": completion})
    else:
        with open(args.input_file) as f:
            prompts = f.read().split("\n\n")
        if len(prompts) > model_args.max_batch_size:
            raise ValueError(
                f"Number of prompts exceeds maximum batch size ({model_args.max_batch_size})"
            )
        prompt_tokens = [tokenizer.apply_chat_template([{"role": "user", "content": prompt}], add_generation_prompt=True) for prompt in prompts]
        completion_tokens = generate(model, prompt_tokens, args.max_new_tokens, tokenizer.eos_token_id, args.temperature)
        completions = tokenizer.batch_decode(completion_tokens, skip_special_tokens=True)
        for prompt, completion in zip(prompts, completions):
            dist_print("Prompt:", prompt)
            dist_print("Completion:", completion)
            dist_print()

    if world_size > 1:
        dist.destroy_process_group()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ckpt-path", type=str, required=True)
    parser.add_argument("--config", type=str, required=True)
    parser.add_argument("--input-file", type=str, default="")
    parser.add_argument("--interactive", action="store_true")
    parser.add_argument("--max-new-tokens", type=int, default=200)
    parser.add_argument("--temperature", type=float, default=0.6)
    args = parser.parse_args()
    if not args.input_file and not args.interactive:
        parser.error("Either --input-file or --interactive must be specified")
    main(args)
