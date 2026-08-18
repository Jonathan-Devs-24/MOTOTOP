# backend/core/ai_service.py
from google import genai
from google.genai import types
from django.conf import settings
from .models import Producto

class GeminiAssistantService:
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model_name = "gemini-3.6-flash"

    def _obtener_catalogo_contexto(self) -> str:
        """Obtiene la lista de productos activos, precios y stock actual."""
        productos = Producto.objects.filter(activo=True).values('id', 'nombre', 'precio_base', 'stock')
        
        if not productos.exists():
            return "No hay productos registrados actualmente en el sistema."
            
        lineas = [
            f"- ID: {p['id']} | Producto: {p['nombre']} | Precio: ${p['precio_base']} | Stock: {p['stock']}"
            for p in productos
        ]
        return "\n".join(lineas)

    def responder(self, mensaje_usuario: str) -> str:
        catalogo = self._obtener_catalogo_contexto()
        
        system_instruction = (
            "Eres el asistente virtual inteligente de la plataforma Moto-Top. "
            "Tu tarea es responder dudas sobre stock, repuestos disponibles y precios según el catálogo:\n\n"
            f"=== CATÁLOGO EN TIEMPO REAL ===\n{catalogo}\n\n"
            "Reglas: Responde de forma concisa y cordial. Si un repuesto no tiene stock o no figura, indícalo claramente."
        )

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.2,
        )

        # Usar chat.send_message para evitar bloqueos y warnings de AFC
        chat = self.client.chats.create(
            model=self.model_name,
            config=config,
        )

        response = chat.send_message(mensaje_usuario)
        return response.text
        
        
        