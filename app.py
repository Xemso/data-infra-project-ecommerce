import os
from flask import Flask, render_template_string, request, redirect
from kafka import KafkaProducer
import json
import uuid
from datetime import datetime
import time

# --- Flask App Configuration ---
app = Flask(__name__)

# --- Kafka Configuration ---
KAFA_BROKER_URL = os.environ.get('KAFKA_BROKER_URL', 'kafka-service:9092')
ORDER_TOPIC = os.environ.get('ORDER_TOPIC', 'orders')

# --- Web Page Template (with Tailwind CSS) ---
html_template = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Protein Powerhouse</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 font-sans">
    <nav class="bg-white shadow-md">
        <div class="container mx-auto px-6 py-3 flex justify-between items-center">
            <a class="text-2xl font-bold text-gray-800" href="#">
                <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="currentColor" class="inline-block" viewBox="0 0 16 16"><path d="M8 16a.5.5 0 0 1-.5-.5V1a.5.5 0 0 1 1 0v14.5a.5.5 0 0 1-.5.5z"/><path d="M5.429 8.321c.214-.214.56-.214.774 0l.928.928.928-.928c.214-.214.56-.214.774 0l.928.928.928-.928c.214-.214.56-.214.774 0l.928.928c.214.214.214.56 0 .774l-.928.928-.928-.928a.5.5 0 0 0-.774 0l-.928.928-.928-.928a.5.5 0 0 0-.774 0l-.928.928-.928-.928a.5.5 0 0 0-.774 0l-.928.928c-.214.214-.214.56 0 .774l.928.928.928-.928a.5.5 0 0 0 .774 0l.928.928.928-.928a.5.5 0 0 0 .774 0l.928.928c.214.214.214.56 0 .774l-.928.928L8 9.096l-.928.928c-.214.214-.56.214-.774 0l-.928-.928L4.5 9.87c-.214.214-.214.56 0 .774l.928.928.928-.928c.214-.214.56-.214.774 0l.928.928c.214.214.214.56 0 .774l-2.678 2.679a.5.5 0 0 1-.708 0L2 11.422V8.5a.5.5 0 0 1 .5-.5h2.428l.5.5a.5.5 0 0 0 .708 0l.292-.292z"/></svg>
                Protein Powerhouse
            </a>
            <div class="hidden md:block">
                <a class="text-gray-600 hover:text-gray-800 px-3" href="#">Catalogue</a>
                <a class="text-gray-600 hover:text-gray-800 px-3" href="#">Contact</a>
            </div>
        </div>
    </nav>

    <div class="container mx-auto px-6 py-12">
        <!-- Message Banners -->
        {% if message %}
        <div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded-lg relative mb-6" role="alert">
            <strong class="font-bold">Succès!</strong>
            <span class="block sm:inline">{{ message }}</span>
        </div>
        {% endif %}
        {% if error %}
        <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg relative mb-6" role="alert">
            <strong class="font-bold">Erreur!</strong>
            <span class="block sm:inline">{{ error }}</span>
        </div>
        {% endif %}

        <div class="bg-white rounded-lg shadow-xl p-8 md:flex">
            <div class="md:w-1/3">
                <div class="bg-blue-500 text-white rounded-lg w-full h-80 flex items-center justify-center text-3xl font-bold">
                    Whey Isolate
                </div>
            </div>
            <div class="md:w-2/3 md:pl-10 mt-6 md:mt-0">
                <p class="text-sm text-blue-600 font-semibold">MEILLEURE VENTE</p>
                <h1 class="text-4xl font-bold text-gray-900 mt-2">Whey Isolate Pro Series</h1>
                <p class="text-gray-600 mt-4">
                    Notre Whey Isolate est micro-filtrée pour une pureté maximale. Avec 25g de protéines par portion, c'est le choix idéal pour la récupération et la croissance musculaire.
                </p>
                <div class="flex items-baseline mt-6">
                    <span class="text-3xl font-bold text-gray-900">49,99€</span>
                    <span class="text-xl text-gray-500 line-through ml-3">69,99€</span>
                </div>
                <form action="/buy" method="POST" class="mt-8">
                    <button type="submit" class="w-full bg-blue-600 text-white font-bold py-3 px-6 rounded-lg hover:bg-blue-700 transition duration-300">
                        Ajouter au Panier
                    </button>
                </form>
            </div>
        </div>
    </div>
    <footer class="bg-white mt-12 py-6">
        <div class="container mx-auto px-6 text-center text-gray-600">
            &copy; 2025 Protein Powerhouse. Tous droits réservés.
        </div>
    </footer>
</body>
</html>
"""

@app.route('/')
def index():
    """Renders the main page."""
    message = request.args.get('message')
    error = request.args.get('error')
    return render_template_string(html_template, message=message, error=error)

@app.route('/buy', methods=['POST'])
def buy():
    """Endpoint to handle a purchase event."""
    producer = None
    try:
        # --- Create a new producer for each request ---
        print("Attempting to connect to Kafka for this request...")
        producer = KafkaProducer(
            bootstrap_servers=KAFA_BROKER_URL,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            api_version=(0, 10, 1),
            # Set a timeout to avoid long waits
            request_timeout_ms=5000 
        )
        print("Connection successful for this request.")

        order_data = {
            'order_id': str(uuid.uuid4()),
            'product_id': 'WHEY001',
            'quantity': 1,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Send message to Kafka
        print(f"Attempting to send order to Kafka: {order_data}")
        producer.send(ORDER_TOPIC, value=order_data)
        producer.flush() 
        print(f"SUCCESS: Order sent to Kafka successfully!")
        
        return redirect('/?message=Produit+ajouté+au+panier+avec+succès!')
        
    except Exception as e:
        print(f"FATAL ERROR: Could not send message to Kafka: {e}")
        return redirect(f'/?error=Erreur+interne+lors+de+la+commande.')
    finally:
        # --- Close the producer connection ---
        if producer:
            producer.close()
            print("Producer connection closed.")


if __name__ == '__main__':
    # This part is for local testing, not used in Docker
    app.run(host='0.0.0.0', port=5000)