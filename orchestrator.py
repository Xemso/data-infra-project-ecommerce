import os
from kafka import KafkaConsumer
import json
from collections import Counter
import time

# --- Kafka Configuration ---
KAFKA_BROKER_URL = os.environ.get('KAFKA_BROKER_URL', 'kafka-service:9092')
ORDER_TOPIC = os.environ.get('ORDER_TOPIC', 'orders')
REPORT_FILE = 'data/sales_report.txt'

# Ensure the data directory exists
if not os.path.exists('data'):
    os.makedirs('data')

def connect_to_kafka():
    """Tries to connect to Kafka, with retries."""
    for i in range(10):
        try:
            consumer = KafkaConsumer(
                ORDER_TOPIC,
                bootstrap_servers=KAFKA_BROKER_URL,
                # Decode messages from JSON
                value_deserializer=lambda v: json.loads(v.decode('utf-8')),
                auto_offset_reset='earliest', # Start reading at the very beginning of the topic
                api_version=(0, 10, 1)
            )
            print("Successfully connected to Kafka as a consumer.")
            return consumer
        except Exception as e:
            print(f"Failed to connect to Kafka, retrying in 5 seconds... ({i+1}/10)")
            time.sleep(5)
    return None

def process_messages():
    """Listens for messages from Kafka and processes them."""
    consumer = connect_to_kafka()
    if not consumer:
        print("Could not connect to Kafka after several retries. Exiting.")
        return

    print(f"Listening for messages on topic '{ORDER_TOPIC}'...")
    
    # Using a Counter to easily count product sales
    sales_counter = Counter()

    for message in consumer:
        # Extract order data from the Kafka message
        order = message.value
        print(f"Received order: {order}")

        product_id = order.get('product_id')
        quantity = order.get('quantity', 0)

        if product_id:
            # Increment the count for this product
            sales_counter[product_id] += quantity
            
            # Generate and write the report after each message
            generate_report(sales_counter)

def generate_report(sales_counter):
    """Generates a sales report from the collected data."""
    try:
        with open(REPORT_FILE, 'w') as f:
            f.write("--- Rapport des Ventes en Temps Réel ---\n")
            f.write(f"Dernière mise à jour : {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            if not sales_counter:
                f.write("Aucune vente enregistrée pour le moment.\n")
            else:
                f.write("Ventes par produit :\n")
                for product, count in sales_counter.items():
                    f.write(f"- Produit {product}: {count} unité(s)\n")
            
        print(f"Sales report updated at {REPORT_FILE}")
    except Exception as e:
        print(f"Error writing report: {e}")

if __name__ == "__main__":
    process_messages()