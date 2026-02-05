# How to Add New Models to MayaGen

MayaGen uses a flexible plugin system based on ComfyUI workflows. Adding a new model is a 3-step process.

## Step 1: Download the Model
**Where to find models:**
- [Hugging Face](https://huggingface.co/models?pipeline_tag=text-to-image) (Official weights)
- [Civitai](https://civitai.com/) (Community fine-tunes)

**Action:**
Download `.safetensors` files to your server's `ComfyUI/models/checkpoints/` folder.

---

## Step 2: Create a Workflow JSON
You don't need to write code for the model logic. You just need a ComfyUI "recording".

1.  Open ComfyUI in your browser.
2.  Load the checkpoint you downloaded.
3.  Set up your graph (Prompt -> Sampler -> Save Image).
4.  **Important:** Enable "Enable Dev Mode Options" in ComfyUI settings (gear icon).
5.  Click **"Save (API Format)"** button.
6.  Save the file as `workflow_yourmodelname.json` in `mayagen-be/workflows/`.

**Rules for API JSON:**
- Ensure the input text node is named/ID'd correctly if you want dynamic prompts (our code automatically finds the `text` field if you use standard nodes).
- Ensure `seed` is randomized by our backend (our code handles `KSampler` seed inputs).

---

## Step 3: Register in Config

**1. Backend Registration (`mayagen-be/app/core/config.py`)**
Add your key to the `WORKFLOWS` dictionary:

```python
WORKFLOWS = {
    "sd15": WORKFLOWS_DIR / "workflow_sd15.json",
    "lcm": WORKFLOWS_DIR / "workflow_lcm.json",
    "your_new_model": WORKFLOWS_DIR / "workflow_yourmodelname.json" # <--- ADD THIS
}
```

**2. Frontend Registration (`mayagen-fe/src/app/page.tsx`)**
Add/Update the dropdown option in the UI:

```tsx
<SelectContent>
    <SelectItem value="sd15">Stable Diffusion 1.5</SelectItem>
    <SelectItem value="lcm">LCM Dreamshaper</SelectItem>
    <SelectItem value="your_new_model">My Cool New Model</SelectItem> {/* <--- ADD THIS */}
</SelectContent>
```

---

## Step 4: Restart
Restart the backend (`uv run run_server.py`) and frontend (`npm run dev`) to see your changes!
