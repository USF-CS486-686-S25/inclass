from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

MAX_VALUE = 2147483647
MIN_VALUE = -2147483648

def validate_decimal(value):
    try:
        num = int(value)
        if num > MAX_VALUE or num < MIN_VALUE:
            raise HTTPException(status_code=400, detail="Invalid 32-bit decimal value")
        return num
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid decimal value")

def validate_binary(value):
    if not all(c in '01' for c in value):
        raise HTTPException(status_code=400, detail="Invalid binary value")
    try:
        num = int(value, 2)
        if num > MAX_VALUE:
            raise HTTPException(status_code=400, detail="Value too large for 32-bit")
        return num
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid binary value")

def validate_hexadecimal(value):
    if not all(c in '0123456789abcdefABCDEF' for c in value):
        raise HTTPException(status_code=400, detail="Invalid hexadecimal value")
    try:
        num = int(value, 16)
        if num > MAX_VALUE:
            raise HTTPException(status_code=400, detail="Value too large for 32-bit")
        return num
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid hexadecimal value")

def decimal_to_binary(decimal):
    if decimal >= 0:
        return bin(decimal)[2:].zfill(32)
    else:
        return bin(decimal % (1 << 32))[2:]

def decimal_to_hexadecimal(decimal):
    if decimal >= 0:
        return hex(decimal)[2:].upper().zfill(8)
    else:
        return hex(decimal % (1 << 32))[2:].upper()

def binary_to_decimal(binary):
    return int(binary, 2)

def binary_to_hexadecimal(binary):
    decimal = binary_to_decimal(binary)
    return decimal_to_hexadecimal(decimal)

def hexadecimal_to_decimal(hexadecimal):
    return int(hexadecimal, 16)

def hexadecimal_to_binary(hexadecimal):
    decimal = hexadecimal_to_decimal(hexadecimal)
    return decimal_to_binary(decimal)

@app.get("/")
async def root():
    return RedirectResponse(url="/static/index.html")

@app.get("/convert/decimal")
async def convert_decimal(value: str):
    decimal = validate_decimal(value)
    binary = decimal_to_binary(decimal)
    hexadecimal = decimal_to_hexadecimal(decimal)
    return {"binary": binary, "hexadecimal": hexadecimal}

@app.get("/convert/binary")
async def convert_binary(value: str):
    decimal = validate_binary(value)
    binary = decimal_to_binary(decimal)
    hexadecimal = binary_to_hexadecimal(binary)
    return {"decimal": decimal, "hexadecimal": hexadecimal}

@app.get("/convert/hexadecimal")
async def convert_hexadecimal(value: str):
    decimal = validate_hexadecimal(value)
    binary = hexadecimal_to_binary(decimal)
    hexadecimal = decimal_to_hexadecimal(decimal)
    return {"decimal": decimal, "binary": binary}