#!/usr/bin/env python3
"""
Test script for image generation functionality
"""
import asyncio
import os
from dotenv import load_dotenv
from ai_service import AIService

# Load environment variables
load_dotenv()

async def test_image_generation():
    """Test the image generation functionality"""
    try:
        # Initialize AI service
        ai_service = AIService()
        
        # Test with a sample prompt
        test_prompt = "A creative upcycled plastic bottle transformed into a beautiful succulent planter, painted in bright turquoise and decorated with geometric patterns, sitting on a wooden windowsill with green plants"
        
        print("Testing image generation...")
        print(f"Prompt: {test_prompt}")
        
        # Generate image
        img_base64, img_filename = ai_service.generate_product_image(test_prompt, "test_project")
        
        if img_base64 and img_filename:
            print(f"✅ Image generated successfully: {img_filename}")
            print(f"📁 Image saved to: static/generated_images/{img_filename}")
            print(f"🔗 Base64 data length: {len(img_base64)} characters")
        else:
            print("❌ Failed to generate image")
            
    except Exception as e:
        print(f"❌ Error during image generation test: {e}")

if __name__ == "__main__":
    asyncio.run(test_image_generation())
