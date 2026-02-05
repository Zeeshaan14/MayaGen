from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid
import os

from ..core import config
from ..services.comfy_client import ComfyUIProvider

app = FastAPI(title="MayaGen FastAPI")

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For dev, allow all. In prod, strict this to localhost:3000
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Provider
# Note: config.COMFYUI["server_address"] is from the new config structure
provider = ComfyUIProvider(config.COMFYUI["server_address"])

from fastapi.staticfiles import StaticFiles

# Mount static files to serve images
app.mount("/images", StaticFiles(directory=config.OUTPUT_FOLDER), name="images")

class GenerateRequest(BaseModel):
    prompt: str
    filename_prefix: str = "api_img"
    width: int = 512
    height: int = 768 # Standard SD1.5 Portrait
    provider: str = "comfyui" # default
    model: str = "sd15" # Options: sd15, flux
    category: str = "uncategorized" # new

@app.get("/health")
def health_check():
    """Checks if we can talk to the ComfyUI Backend on Azure"""
    try:
        if not config.COMFYUI["server_address"]:
             raise HTTPException(status_code=503, detail="Server address not configured")
        return {"status": "online", "backend": config.COMFYUI["server_address"]}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))

@app.get("/images")
def list_images():
    """Lists all generated images by walking the output directory."""
    images = []
    base_url = "http://127.0.0.1:8000/images"
    
    if not os.path.exists(config.OUTPUT_FOLDER):
         return {"images": []}

    for root, dirs, files in os.walk(config.OUTPUT_FOLDER):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                # Calculate relative category path
                rel_dir = os.path.relpath(root, config.OUTPUT_FOLDER)
                category = rel_dir if rel_dir != "." else "uncategorized"
                
                # Windows path fix for URL
                safe_rel_path = os.path.join(rel_dir, file).replace("\\", "/")
                if safe_rel_path.startswith("./"):
                    safe_rel_path = safe_rel_path[2:]

                images.append({
                    "filename": file,
                    "category": category,
                    "url": f"{base_url}/{safe_rel_path}"
                })
    
    # Sort by newest first (filesystem order is arbitrary, but we can't easily get creation time efficiently without stat calls. 
    # For now, reverse list is a simple heuristic if OS walks in order, otherwise we might settle for arbitrary order)
    return {"images": images[::-1]}

@app.post("/generate")
def generate_image(req: GenerateRequest):
    """
    Generates an image using the Azure ComfyUI backend.
    """
    try:
        # Determine Folder Path
        safe_category = "".join([c for c in req.category if c.isalnum() or c in (' ', '_', '-')]).strip().replace(" ", "_")
        category_dir = os.path.join(config.OUTPUT_FOLDER, safe_category)
        os.makedirs(category_dir, exist_ok=True)

        filename = f"{req.filename_prefix}_{uuid.uuid4().hex}.png"
        output_path = os.path.join(category_dir, filename)
        
        saved_file = ""
        
        if req.provider == "comfyui":
             # Select Workflow
             workflow_path = config.WORKFLOWS.get(req.model, config.WORKFLOWS["sd15"])
             
             # Call the synchronous generation (now with workflow_path)
             saved_file = provider.generate(req.prompt, output_path, req.width, req.height, workflow_path)
        else:
             # Mock Logic for other providers
             saved_file = f"mock_{req.provider}_image_generated_at_{output_path}"
             # In real impl, you'd call OpenAIClient.generate(...)
        
        # Construct URL
        # Assuming the server is running on localhost:8000. 
        # In prod, get base URL from config or request.
        image_url = f"http://127.0.0.1:8000/images/{safe_category}/{filename}"

        return {
            "status": "success",
            "image_url": image_url, # Return URL instead of path
            "prompt": req.prompt,
            "provider": req.provider,
            "category": safe_category
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
