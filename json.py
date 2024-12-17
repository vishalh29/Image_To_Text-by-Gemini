import google.generativeai as genai
import os
from pathlib import Path
import json

GOOGLE_API_KEY = "AIzaSyArud_pm9K2g6j4jLzLMhFzPlZ0r7O98wg"  # Replace with your actual API key
genai.configure(api_key=GOOGLE_API_KEY)

MODEL_CONFIG = {
    "temperature": 0.2,
    "top_p": 1,
    "top_k": 32,
    "max_output_tokens": 4096,
}

model = genai.GenerativeModel(model_name="gemini-1.5-flash", generation_config=MODEL_CONFIG)

def image_format(image_path):
    img = Path(image_path)

    if not img.exists():
        raise FileNotFoundError(f"Could not find image: {img}")

    image_parts = [
        {"mime_type": "image/png", "data": img.read_bytes()}  # You can change MIME type based on image type
    ]
    return image_parts

def gemini_output(image_path, system_prompt, user_prompt):
   
    image_info = image_format(image_path)
    input_prompt = [system_prompt, image_info[0], user_prompt]
    response = model.generate_content(input_prompt)
    
    # Ensure output is plain JSON by stripping unwanted markdown formatting
    output = response.text.strip()
    if output.startswith("```json"):
        output = output[7:]
    if output.endswith("```"):
        output = output[:-3]
    
    return output

def process_images_in_folder(input_folder, output_folder):

    image_files = [f for f in Path(input_folder).iterdir() if f.suffix.lower() in ['.png', '.jpg', '.jpeg']]
    
    Path(output_folder).mkdir(parents=True, exist_ok=True)
    
    for image_path in image_files:
        system_prompt = """
                       You are a specialist in comprehending receipts.
                       Input images in the form of receipts will be provided to you,
                       and your task is to respond to questions based on the content of the input image.
                       """
        user_prompt = "Convert image data into json format with appropriate json tags as required for the data in image "
        
        output = gemini_output(image_path, system_prompt, user_prompt)
        
        print(f"Response for image '{image_path.name}':\n{output}\n")
        
        output_file = Path(output_folder) / f"{image_path.stem}_response.json"  # Save with the same name as image, but with "_response"
        
        try:
            parsed_output = json.loads(output)  # Parse to ensure it is valid JSON
            with open(output_file, "w") as file:
                json.dump(parsed_output, file, indent=4)
            print(f"Response for image '{image_path.name}' has been saved to: {output_file}")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON for image '{image_path.name}': {e}")

input_folder = "/Users/vishal.hanchate/Desktop/intern/New Folder With Items"  # Replace with your folder path

output_folder = "/Users/vishal.hanchate/Desktop/untitled folder/"  # Replace with your desired output folder

process_images_in_folder(input_folder, output_folder)
