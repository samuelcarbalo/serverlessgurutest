import json
import uuid
import os
import boto3
from datetime import datetime

# Configuración de DynamoDB
# Usamos boto3.resource para una interfaz de alto nivel (más fácil de usar)
dynamodb = boto3.resource('dynamodb', region_name=os.environ['REGION'])
table = dynamodb.Table(os.environ['TEST_TABLE'])
print(f"Using table: {os.environ['TEST_TABLE']}")
def createFunction(event, context):
    try:
        timestamp = str(datetime.now().timestamp())
        body = json.loads(event['body'])
        if 'name' not in body or 'description' not in body:
            return { 'statusCode': 400, 'body': json.dumps({'message': 'Faltan campos obligatorios: name y description.'}) }
        item = {
            'PK': body['name'],
            'SK': str(uuid.uuid4()),
            "name": body['name'],
            "description": body['description'],
            "price": body['price'],
            "category": body['category'],
            "disponible": True,
            'createdAt': timestamp,
            'updatedAt': timestamp,
        }

        # Inserción
        table.put_item(Item=item)

        return {
            'statusCode': 201,
            'headers': { 'Access-Control-Allow-Origin': '*' },
            'body': json.dumps(item)
        }
    except Exception as e:
        print(f"Error creating data: {e}")
        return { 'statusCode': 500, 'body': json.dumps({'message': 'Error interno del servidor.'}) }

def getFunction(event, context):
    try:
        # Recupera el ID del path: /datas/{id}
        data_id = event['pathParameters']['id']
        
        result = table.get_item(Key={'id': data_id})
        item = result.get('Item')

        if not item:
            return { 'statusCode': 404, 'body': json.dumps({'message': 'Tarea no encontrada.'}) }

        return {
            'statusCode': 200,
            'headers': { 'Access-Control-Allow-Origin': '*' },
            'body': json.dumps(item)
        }
    except Exception as e:
        print(f"Error getting data: {e}")
        return { 'statusCode': 500, 'body': json.dumps({'message': 'Error interno del servidor.'}) }
