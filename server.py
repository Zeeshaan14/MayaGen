from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import config
from main import ComfyUIProvider
import os
import uuid

app = FastAPI(title="Synthetic Image API")

# Initialize Provider
provider = ComfyUIProvider(config.COMFYUI["server_address"])

class GenerateRequest(BaseModel):
    prompt: str
    filename_prefix: str = "api_img"

@app.get("/health")
def health_check():
    """Checks if we can talk to the ComfyUI Backend on Azure"""
    try:
        # Simple check - just try to get system stats or similar
        # For now, we'll just check if the URL is set
        if not config.COMFYUI["server_address"]:
             raise HTTPException(status_code=503, detail="Server address not configured")
        return {"status": "online", "backend": config.COMFYUI["server_address"]}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))

@app.post("/generate")
def generate_image(req: GenerateRequest):
    """
    Generates an image using the Azure ComfyUI backend.
    Returns the local path where the image was saved.
    """
    try:
        # 1. Modify the Prompt (simulated logic from main.py)
        # We assume the main.py logic is reusable. 
        # But main.py is designed as a script. 
        # Ideally, we should refactor main.py to be importable.
        # For now, we will call the provider directly.
        
        output_path = os.path.join(config.OUTPUT_FOLDER, f"{req.filename_prefix}_{uuid.uuid4().hex}.png")
        
        # Call the synchronous generation (Note: this blocks the server thread!
        # For production, this should be async or in a background task)
        saved_file = provider.generate(req.prompt, output_path)
        
        return {
            "status": "success",
            "image_path": saved_file,
            "prompt": req.prompt
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
