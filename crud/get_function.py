import json
import uuid
import os
import boto3
from datetime import datetime
from urllib.parse import unquote

# Configuración de DynamoDB
# Usamos boto3.resource para una interfaz de alto nivel (más fácil de usar)
dynamodb = boto3.resource('dynamodb', region_name=os.environ['REGION'])
table = dynamodb.Table(os.environ['TEST_TABLE'])


def getFunction(event, context):
    try:
        # Recupera el ID del path: /{id}
        data_pk = event['pathParameters']['id']

        result = table.get_item(Key={'PK': 'PRODUCTS', 'SK': data_pk})
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

