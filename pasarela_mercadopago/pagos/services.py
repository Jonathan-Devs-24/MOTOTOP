# pasarela_mercadopago/pagos/services.py
import os
import mercadopago
from dotenv import load_dotenv

# Carga las variables de entorno desde el archivo .env 
load_dotenv()

# Inicializa el SDK de MP con el token del .env
sdk = mercadopago.SDK(os.getenv("MP_ACCESS_TOKEN"))

def crear_preferencia_pago(items, external_reference):
    """
    Crea una preferencia de PAGO en MP.
    """
    # 1. Leemos la URL base desde el .env
    api_base = os.getenv("API_BASE_URL", "http://127.0.0.1:8080/api/")
    
    # 2. Limpieza estricta para obtener la raíz del servidor de la pasarela
    # Si viene como 'http://127.0.0.1:8080/api/', nos quedamos con 'http://127.0.0.1:8080'
    base_url = api_base.replace("/api/", "").rstrip("/")

    # 3. Construimos las URLs de retorno asegurando que tengan un formato limpio
    success_url = f"{base_url}/pagos/feedback/"
    
    # --- PRUEBA EN CONSOLA ---
    # Esto te va a permitir ver exactamente qué URL le estás mandando a Mercado Pago
    print(f"--> URL de éxito enviada a MP: {success_url}")
    # -------------------------

    preference_data = {
        "items": items,
        "external_reference": str(external_reference),
        
        "back_urls": {
            "success": success_url,
            "failure": success_url,
            "pending": success_url
        },
        
        # Si te sigue fallando por las restricciones de localhost de MP, 
        # podés comentar temporalmente esta línea de abajo con un '#' para probar.
        "auto_return": "approved",
    }
    
    try:
        preference_response = sdk.preference().create(preference_data)
        
        if "status" in preference_response and preference_response["status"] >= 400:
            print("--- ERROR DE MERCADO PAGO ---")
            print(preference_response)
            return None
            
        return preference_response["response"]
    except Exception as e:
        print(f"Error crítico en el SDK de MP: {e}")
        return None