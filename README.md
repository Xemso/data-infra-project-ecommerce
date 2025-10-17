Data Infrastructure Project: Protein Powerhouse

This repository contains the source code and configuration files for the final data infrastructure project. The project deploys a scalable, real-time e-commerce architecture for a fictional supplement store, "Protein Powerhouse."

1. Global Architecture

The infrastructure is designed around an event-driven microservices architecture, fully containerized and orchestrated by Kubernetes.

The data flow is as follows:

Web Application (Producer): An e-commerce site developed with Flask that receives customer orders.

Apache Kafka (Event Hub): Each order is sent as an event to a Kafka topic, decoupling the services.

Processing Service (Consumer): A Python script that listens for order events in real-time, processes them, and generates a sales report.

All these components run resiliently within a Kubernetes cluster.

2. Technology Stack

Docker: For the containerization of our Python applications.

Kubernetes: For the orchestration, deployment, scalability, and management of all our services.

Python / Flask: For the rapid development of the web application and the processing service.

Apache Kafka: For managing the real-time data flow asynchronously and reliably.

kubectl: For interacting with the Kubernetes cluster from the command line.

3. How to Launch the Project

To run the entire infrastructure in a local environment, follow these steps.

Prerequisites

Have Docker Desktop installed, with the Kubernetes engine enabled in its settings.

Have kubectl configured to interact with the Docker Desktop cluster.

Deployment Instructions

Build the Docker Images:
Open a terminal at the root of the project.

# Build the web application image (producer)
docker build -t boutique-app -f Dockerfile .

# Build the processing service image (consumer)
docker build -t boutique-consumer -f Dockerfile.consumer .


Deploy the Infrastructure on Kubernetes:
Apply all the configuration files.

# Deploy Kafka and Zookeeper
kubectl apply -f kafka.yaml

# Deploy the web application
kubectl apply -f deployment.yaml

# Deploy the processing service
kubectl apply -f consumer-deployment.yaml


Wait a few minutes for all pods to reach the Running status (check with kubectl get pods).

Access the Website:
The site is exposed on port 30001. Open your browser and go to the address:
http://localhost:30001

Observe the Real-Time Data Flow:
To see orders being processed live, display the logs of the consumer pod.

# First, find the name of the consumer pod
kubectl get pods

# Then, display its live logs (replace the pod name)
kubectl logs -f <boutique-consumer-pod-name>


Each click on "Ajouter au Panier" on the website will display a new message in this terminal.

4. Data Model

The order events sent to Kafka follow the following JSON model:

{
  "order_id": "a-unique-uuid-for-each-order",
  "product_id": "WHEY001",
  "quantity": 1,
  "timestamp": "datetime-in-iso-8601-format"
}
