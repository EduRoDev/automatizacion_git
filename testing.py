# from app.services.auth import generate_jwt, get_installation_token
import asyncio
from app.services.llm import review_diff

# token = generate_jwt()
# print(token)
# print(f"Longitud: {len(token)}")

# token = asyncio.run(get_installation_token())
# print(token[:12],"...")
# print(f"Longitud: {len(token)}")


diff_de_prueba = """diff --git a/calc.py b/calc.py
--- a/calc.py
+++ b/calc.py
@@ -1,2 +1,2 @@
 def divide(a, b):
-    return a / b
+    return a / b  # sin validar division por cero
"""

resultado = asyncio.run(review_diff(diff_de_prueba))
print(resultado)