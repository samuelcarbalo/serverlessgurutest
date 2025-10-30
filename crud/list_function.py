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


def listFunction(event, context):
    try:
        # Usamos table.scan() para obtener todos los elementos de la tabla.
        # ADVERTENCIA: scan() es costoso y lento en tablas grandes. Se prefiere usar Query + GSI.
        result = table.scan() 
        items = result.get('Items', [])

        return {
            'statusCode': 200,
            'headers': { 'Access-Control-Allow-Origin': '*' },
            'body': json.dumps(items)
        }
    except Exception as e:
        print(f"Error listing data: {e}")
        return { 'statusCode': 500, 'body': json.dumps({'message': 'Error interno del servidor.'}) }



