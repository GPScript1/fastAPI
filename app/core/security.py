from fastapi import Header, HTTPException
import os
import hashlib

def verificar_api_key(
    api_key: str = Header(..., alias="api-key"),
    api_key_name: str = Header(..., alias="api-key-name")
):

    expected_key_plain = os.getenv("API_KEY")
    expected_name = os.getenv("API_KEY_NAME")


    expected_key_hash = hashlib.sha256(expected_key_plain.encode()).hexdigest()


    if api_key_name != expected_name or api_key != expected_key_hash:
        raise HTTPException(status_code=403, detail="API Key inválida")
