import litellm
import argparse

def encode_image(image_path):
    import base64

    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def main():
    parser = argparse.ArgumentParser(description='Analyze an image with a custom prompt')
    parser.add_argument('image_path', help='Path to the image file')
    parser.add_argument('prompt', help='Prompt to apply to the image')
    
    args = parser.parse_args()
    
    # Getting the base64 string
    base64_image = encode_image(args.image_path)
    
    resp = litellm.completion(
        model="openrouter/anthropic/claude-3.5-sonnet",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": args.prompt},
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

    print(resp.choices[0].message.content)

if __name__ == "__main__":
    main()
