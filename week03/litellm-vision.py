import litellm

def encode_image(image_path):
    import base64

    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


image_path = "cat.png"
# Getting the base64 string
base64_image = encode_image(image_path)
resp = litellm.completion(
    model="openrouter/anthropic/claude-3.5-sonnet",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Whats in this image?"},
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



print(f"\nResponse: {resp}")
