import csv
import os
from PIL import Image
import google.generativeai as genai
from google.api_core.exceptions import NotFound  # Import the NotFound exception properly

# Set your API key directly here
key = "API_KEY"  # Replace with your actual Google API key

# Configure the generative AI with your API key
genai.configure(api_key=key)

# List available models
available_models = []
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(model.name)
        available_models.append(model.name)

# Select a model that is not deprecated (use a valid model name from the available models)
model_name = 'models/gemini-1.5-flash'  # Replace with the exact model name from the list
if model_name not in available_models:
    raise ValueError(f"The model {model_name} is not available. Please select a valid model from: {available_models}")

model = genai.GenerativeModel(model_name)


def get_gemini_response(input_text, image, user_prompt):
    # Generate content using the provided input and image
    response = model.generate_content([input_text, image[0], user_prompt])
    return response.text


def input_image_details(image_path):
    # Check if the provided image path exists
    if os.path.exists(image_path):
        with open(image_path, "rb") as image_file:
            bytes_data = image_file.read()

        # Prepare image data for the API
        image_parts = [
            {
                'mime_type': 'image/jpeg',  # Adjust MIME type according to your image type (e.g., 'image/png')
                'data': bytes_data
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError(f'No file found at the provided path: {image_path}')


# Define your input and prompts
input_text = "ENTER INPUT TEXT"

input_prompt = """
ENTER THE PROMPT
"""

# Folder path containing the images
folder_path = "ENTER PATH"  # Replace with your folder path

# CSV file to store the results
csv_file_path = "output_results.csv"

# Iterate over all images in the folder
try:
    if os.path.exists(folder_path):
        # Open the CSV file to write the results
        with open(csv_file_path, mode='w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            # Write the header row
            csv_writer.writerow(["File Name", "Response"])

            for filename in os.listdir(folder_path):
                # Construct the full image path
                image_path = os.path.join(folder_path, filename)

                # Check if the file is an image (based on common extensions)
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif')):
                    try:
                        # Get the image details
                        image_data = input_image_details(image_path)

                        # Get the response using the Gemini model
                        response = get_gemini_response(input_prompt, image_data, input_text)

                        # Write the response to the CSV file
                        csv_writer.writerow([filename, response])

                        # Print the response for each image
                        print(f"Response for {filename}:")
                        print(response)

                    except FileNotFoundError as e:
                        print(e)

                    except NotFound as e:
                        print(f"Model not found or deprecated: {e}")

                    except Exception as e:
                        print(f"An unexpected error occurred while processing {filename}: {e}")

    else:
        raise FileNotFoundError(f"No folder found at the provided path: {folder_path}")

except FileNotFoundError as e:
    print(e)

except Exception as e:
    print(f"An unexpected error occurred: {e}")