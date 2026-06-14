import hashlib
import hmac

def verify(payload: bytes, secret: str, signature: str | None) -> bool:
    if not signature:
        return False

    if not signature.startswith("sha256="):
        return False

    expected = hmac.new(
        key=secret.encode("utf-8"),
        msg=payload,
        digestmod=hashlib.sha256
    ).hexdigest()

    received = signature.removeprefix("sha256=")
    return hmac.compare_digest(expected, received)