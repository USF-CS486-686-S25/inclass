import litellm
import argparse
import os

def encode_image(image_path):
    import base64

    # Get file extension
    _, ext = os.path.splitext(image_path.lower())
    if ext not in ['.png', '.jpg', '.jpeg', '.pdf']:
        raise ValueError(f"Unsupported file type: {ext}. Supported types are: .png, .jpg, .jpeg, .pdf")

    with open(image_path, "rb") as image_file:
        base64_string = base64.b64encode(image_file.read()).decode("utf-8")
        
        # Set correct mime type based on file extension
        if ext == '.pdf':
            mime_type = 'application/pdf'
        elif ext == '.png':
            mime_type = 'image/png'
        else:  # jpg or jpeg
            mime_type = 'image/jpeg'
            
        return f"data:{mime_type};base64,{base64_string}"

def process_image(image_path, prompt):
    base64_data = encode_image(image_path)
    resp = litellm.completion(
        #model="openrouter/anthropic/claude-3.5-sonnet",
        model="claude-3-5-sonnet-20241022",
        #model="openai/gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": base64_data
                        },
                    },
                ],
            }
        ],
    )
    return resp.choices[0].message.content

def main():
    parser = argparse.ArgumentParser(description='Process an image with a given prompt')
    parser.add_argument('image_path', help='Path to the image file (supports .png, .jpg, .jpeg, .pdf)')
    parser.add_argument('prompt', help='Prompt to apply to the image')
    
    args = parser.parse_args()
    
    try:
        response = process_image(args.image_path, args.prompt)
        print(response)
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error processing image: {e}")

if __name__ == "__main__":
    main()
