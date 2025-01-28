from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import uvicorn

app = FastAPI()

# Serve static files
app.mount("/static", StaticFiles(directory="."), name="static")

class ConversionRequest(BaseModel):
    value: str
    from_base: str

MAX_32BIT = 0xFFFFFFFF
MIN_32BIT = -0x80000000

def validate_number(value: str, base: int) -> Optional[int]:
    try:
        num = int(value, base)
        if MIN_32BIT <= num <= MAX_32BIT:
            return num
        return None
    except ValueError:
        return None

@app.get("/")
async def root():
    return {"status": "alive"}

@app.post("/convert")
async def convert(request: ConversionRequest):
    base_map = {
        "decimal": 10,
        "binary": 2,
        "hex": 16
    }
    
    if request.from_base not in base_map:
        raise HTTPException(status_code=400, detail="Invalid base")
        
    num = validate_number(request.value, base_map[request.from_base])
    if num is None:
        raise HTTPException(status_code=400, detail="Invalid number for given base")
        
    return {
        "decimal": str(num),
        "binary": bin(num & 0xFFFFFFFF)[2:].zfill(32),
        "hex": hex(num & 0xFFFFFFFF)[2:].upper()
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
