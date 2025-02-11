import litellm
import argparse

def encode_image(image_path):
    import base64

    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def process_image(image_path, prompt):
    base64_image = encode_image(image_path)
    resp = litellm.completion(
        model="openrouter/anthropic/claude-3.5-sonnet",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": "data:image/png;base64," + base64_image
                        },
                    },
                ],
            }
        ],
    )
    return resp.choices[0].message.content

def main():
    parser = argparse.ArgumentParser(description='Process an image with a given prompt')
    parser.add_argument('image_path', help='Path to the image file')
    parser.add_argument('prompt', help='Prompt to apply to the image')
    
    args = parser.parse_args()
    
    try:
        response = process_image(args.image_path, args.prompt)
        print(response)
    except Exception as e:
        print(f"Error processing image: {e}")

if __name__ == "__main__":
    main()
