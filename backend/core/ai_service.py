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
            "Eres el asistente virtual inteligente de la plataforma Moto-Top.\n"
            "Tu objetivo es responder consultas sobre repuestos, stock y precios basándote exclusivamente en el siguiente catálogo:\n\n"
            f"=== CATÁLOGO EN TIEMPO REAL ===\n{catalogo}\n\n"
            "--- REGLAS DE RESPUESTA ---\n"
            "1. Tono y precisión: Sé conciso, claro y cordial. No inventes información ni asumas datos que no figuren en el catálogo.\n"
            "2. Disponibilidad: Si un repuesto no tiene stock o no está registrado, infórmalo con claridad.\n"
            "3. Formato limpio: No utilices caracteres especiales como asteriscos (*), símbolos de suma (+) ni formato Markdown que dificulte la legibilidad.\n"
            "4. Listado de productos: Si mencionas varios artículos, presenta cada producto en un renglón individual siguiendo este formato exacto:\n"
            "   Producto 1:"
            "       Precio: $100"
            "       Stock: 5\n"
            ""
            "   Producto 2:"
            "       Precio: $200"
            "       Stock: 0\n"
            ""
            "5. Cierre: Separa siempre el párrafo final o mensaje de despedida con un salto de línea visible.\n"
            "6. Consultas fuera de catálogo o dudas no resueltas: Si te consultan por información que desconoces, deriva cordialmente al usuario a comunicarse o acercarse a la concesionaria indicando estos datos de contacto:\n"
            "   - Teléfono: +54 (3777) 00-0000\n"
            "   - Correo electrónico: ventas@mototop.com.ar\n"
            "   - Domicilio: Calle 123"
            "Si te piden que cuentes un chiste, conta una de motos que no requiera que el usuario responda. O sea conta todo en una respuesta"
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
        
        
        