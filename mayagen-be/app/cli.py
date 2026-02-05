import os
import time
import argparse
from pathlib import Path
from .core import config
from .services.comfy_client import ComfyUIProvider

def load_prompts(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

def run_batch_generation():
    parser = argparse.ArgumentParser(description="MayaGen Synthetic Data Automation")
    parser.add_argument("--model", type=str, default="lcm", choices=config.WORKFLOWS.keys(), help="Model to use (lcm, sd15, flux)")
    parser.add_argument("--input", type=str, default="prompts.txt", help="Path to prompts file")
    parser.add_argument("--output", type=str, default=config.OUTPUT_FOLDER, help="Output directory")
    args = parser.parse_args()

    print("============================================")
    print(f" MAYAGEN AUTOMATION | Model: {args.model.upper()}")
    print("============================================")

    # 1. Setup
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    provider = ComfyUIProvider(config.COMFYUI["server_address"])
    
    # Resolve Workflow
    workflow_path = config.WORKFLOWS.get(args.model)
    if not workflow_path or not workflow_path.exists():
        print(f"[Error] Workflow file not found: {workflow_path}")
        return

    # 2. Get Prompts
    prompts_file = Path(args.input)
    if not prompts_file.exists():
        # Try relative to root if not found
        prompts_file = config.BASE_DIR / args.input
        if not prompts_file.exists():
             print(f"[Error] Prompts file not found: {args.input}")
             return

    prompts = load_prompts(prompts_file)
    print(f"[System] Loaded {len(prompts)} prompts from {prompts_file.name}\n")

    # 3. Generate Loop
    for i, prompt_text in enumerate(prompts):
        print(f"\n[{i+1}/{len(prompts)}] Generating: {prompt_text[:50]}...")
        
        # Categorize based on simple keyword matching (optional logic)
        category = "uncategorized"
        # Create a safe filename
        safe_prompt = "".join([c for c in prompt_text[:30] if c.isalnum() or c in (' ', '_')]).strip().replace(" ", "_")
        timestamp = int(time.time())
        filename = f"{args.model}_{timestamp}_{safe_prompt}.png"
        
        # Subfolder logic (optional, keeping flat for script default or mimic API structure?)
        # Let's mimic API structure to keep gallery happy
        if "portrait" in prompt_text.lower(): category = "Portraits"
        elif "landscape" in prompt_text.lower(): category = "Landscapes"
        
        cat_dir = output_dir / category
        cat_dir.mkdir(exist_ok=True)
        final_path = cat_dir / filename
        
        try:
            provider.generate(prompt_text, str(final_path), width=512, height=512 if args.model == "lcm" else 512, workflow_path=workflow_path)
            print(f"   -> Saved to {category}/{filename}")
        except Exception as e:
            print(f"[Error] Generation failed: {e}")

    print("\n[System] Batch complete.")

if __name__ == "__main__":
    run_batch_generation()
