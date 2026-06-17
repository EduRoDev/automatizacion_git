# # from app.services.auth import generate_jwt, get_installation_token
import asyncio
import time
from app.services.llm import review_diff

# # token = generate_jwt()
# # print(token)
# # print(f"Longitud: {len(token)}")

# # token = asyncio.run(get_installation_token())
# # print(token[:12],"...")
# # print(f"Longitud: {len(token)}")


diff_de_prueba = """diff --git a/calc.py b/calc.py
--- a/calc.py
+++ b/calc.py
@@ -1,2 +1,2 @@
 def divide(a, b):
-    return a / b
+    return a / b  # sin validar division por cero
"""

inicio = time.perf_counter()
resultado = asyncio.run(review_diff(diff_de_prueba))
fin = time.perf_counter()

print(f"Tiempo: {fin - inicio:.2f} segundos")
print(repr(resultado))

# import asyncio
# from app.services.llm import review_diff
# from app.services.parser import parser
# from app.services.review import parser_llm_response, validate_comment

# diff = """diff --git a/calc.py b/calc.py
# --- a/calc.py
# +++ b/calc.py
# @@ -1,2 +1,3 @@
#  def divide(a, b):
# +    resultado = a / b
#      return a / b
# """

# raw = asyncio.run(review_diff(diff))
# file_diffs = parser(diff)
# observaciones = parser_llm_response(raw)
# comentarios = validate_comment(observaciones, file_diffs)

# print(f"Crudas del modelo: {len(observaciones)}")
# for c in comentarios:
#     print(f"  {c.path}:{c.line} -> {c.body}")