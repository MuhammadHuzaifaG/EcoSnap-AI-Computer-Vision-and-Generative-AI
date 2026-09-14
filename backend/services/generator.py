import httpx
from PIL import Image, ImageDraw, ImageFilter
from utils.helpers import image_to_base64
from core.config import settings

class ImageGeneratorService:
    async def generate_upcycled_concept(self, prompt: str, original_image: Image.Image) -> str:
        if settings.GENAI_API_KEY and settings.GENAI_API_KEY != "your_huggingface_api_key_here":
            try:
                return await self._call_remote_image_api(prompt)
            except Exception as e:
                print(f"⚠️ Remote GenAI API timeout or error: {e}. Switching to offline procedural demo mode.")
                return self._generate_procedural_demo_image(prompt, original_image)
        
        return self._generate_procedural_demo_image(prompt, original_image)

    async def _call_remote_image_api(self, prompt: str) -> str:
        url = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
        headers = {"Authorization": f"Bearer {settings.GENAI_API_KEY}"}
        payload = {"inputs": f"Professional product photograph of {prompt}, studio lighting, highly detailed 8k resolution, sustainable design concept"}

        # Short timeout so it never hangs the user interface
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                image_bytes = response.content
                import io
                generated_img = Image.open(io.BytesIO(image_bytes))
                return image_to_base64(generated_img)
            else:
                print(f"⚠️ HF API returned status {response.status_code}. Using fallback.")
                return self._generate_fallback_graphic(prompt)

    def _generate_procedural_demo_image(self, prompt: str, original_image: Image.Image) -> str:
        base = original_image.copy().resize((512, 512))
        base = base.filter(ImageFilter.SMOOTH_MORE)
        draw = ImageDraw.Draw(base)
        draw.rectangle([10, 10, 502, 502], outline="#10B981", width=4)
        draw.rectangle([10, 430, 502, 502], fill=(16, 185, 129, 200))
        return image_to_base64(base)

    def _generate_fallback_graphic(self, prompt: str) -> str:
        img = Image.new("RGB", (512, 512), color=(31, 41, 55))
        draw = ImageDraw.Draw(img)
        draw.text((50, 250), "Synthetic Upcycle Concept Generated", fill=(255, 255, 255))
        return image_to_base64(img)

generator_service = ImageGeneratorService()