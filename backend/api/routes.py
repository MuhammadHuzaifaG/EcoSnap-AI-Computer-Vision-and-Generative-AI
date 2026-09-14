from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List
from services.classifier import classifier_service
from services.generator import generator_service
from utils.helpers import validate_and_load_image

router = APIRouter()

class StepInstruction(BaseModel):
    step_number: int
    title: str
    description: str

class UpcycleResponse(BaseModel):
    original_category: str
    raw_label: str
    confidence: float
    upcycling_title: str
    suggested_prompt: str
    synthetic_image_base64: str
    estimated_time: str
    difficulty: str
    tools_needed: List[str]
    instructions: List[StepInstruction]

# Pre-defined step templates based on material type
DIY_GUIDES = {
    "Bottle": {
        "title": "Glass Bottle Ambient Table Lamp",
        "time": "45 mins",
        "difficulty": "Easy",
        "tools": ["Glass Drill Bit", "LED String Lights", "Safety Goggles", "Grit Sandpaper"],
        "steps": [
            {"step_number": 1, "title": "Clean & Prep", "description": "Soak the bottle in warm soapy water to peel off labels. Dry completely and smooth any rough edges."},
            {"step_number": 2, "title": "Drill Cable Hole", "description": "Using a 1/2-inch glass diamond drill bit at low speed, bore a hole near the bottom base under cold running water."},
            {"step_number": 3, "title": "Feed Wiring", "description": "Insert the warm-white LED wire string through the rear hole until distributed evenly inside the glass chamber."},
            {"step_number": 4, "title": "Seal & Power On", "description": "Place a rubber grommet around the cord entry to prevent friction, plug in, and enjoy your new ambient lamp."}
        ]
    },
    "Glass": {
        "title": "Hanging Wall Planter Vessel",
        "time": "30 mins",
        "difficulty": "Intermediate",
        "tools": ["Leather Straps", "Mounting Hook", "Potting Mix", "Small Succulents"],
        "steps": [
            {"step_number": 1, "title": "Prepare Base", "description": "Ensure glass vessel is thoroughly washed and disinfected."},
            {"step_number": 2, "title": "Harness Assembly", "description": "Loop durable leather straps securely around the rim and neck of the vessel."},
            {"step_number": 3, "title": "Drainage Layer", "description": "Add a 1-inch bottom layer of activated charcoal and gravel to prevent root rot."},
            {"step_number": 4, "title": "Planting", "description": "Fill with succulent potting soil, embed your greenery, and hang near bright indirect light."}
        ]
    },
    "Default": {
        "title": "Upcycled Designer Desk Organizer",
        "time": "25 mins",
        "difficulty": "Beginner",
        "tools": ["Utility Knife", "Non-toxic Glue", "Acrylic Paint", "Ruler"],
        "steps": [
            {"step_number": 1, "title": "Structural Marking", "description": "Measure and mark cut lines according to your desk storage requirements."},
            {"step_number": 2, "title": "Precision Cut", "description": "Carefully trim material sections using a straight edge and utility blade."},
            {"step_number": 3, "title": "Assembly", "description": "Bond structural components using eco-friendly craft adhesive and let set for 15 minutes."},
            {"step_number": 4, "title": "Finishing", "description": "Apply a coat of non-toxic acrylic paint or lacquer for a modern matte finish."}
        ]
    }
}

@router.post("/analyze", response_model=UpcycleResponse)
async def analyze_image(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="No image file provided.")

    file_bytes = await file.read()
    
    # 1. Validate & preprocess uploaded image
    pil_image = validate_and_load_image(file_bytes, file.filename)

    # 2. Run Computer Vision Classification
    classification_result = classifier_service.classify(pil_image)
    category = classification_result["detected_category"]

    # 3. Trigger Generative AI Synthetic Image Creation
    synthetic_image_b64 = await generator_service.generate_upcycled_concept(
        prompt=classification_result["suggested_prompt"],
        original_image=pil_image
    )

    # 4. Fetch instructions blueprint
    guide = DIY_GUIDES.get(category, DIY_GUIDES["Default"])

    return UpcycleResponse(
        original_category=category,
        raw_label=classification_result["raw_label"],
        confidence=classification_result["confidence"],
        upcycling_title=guide["title"],
        suggested_prompt=classification_result["suggested_prompt"],
        synthetic_image_base64=synthetic_image_b64,
        estimated_time=guide["time"],
        difficulty=guide["difficulty"],
        tools_needed=guide["tools"],
        instructions=[StepInstruction(**s) for s in guide["steps"]]
    )