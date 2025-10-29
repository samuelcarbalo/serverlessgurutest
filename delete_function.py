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

# --- 5. D - DELETE (Eliminar Producto) ---
def deleteFunction(event, context):
    try:
        data_pk_encoded = event['pathParameters']['PK']
        
        # 2. **DECODIFICAR** el valor para convertir %23 a #
        data_pk = unquote(data_pk_encoded) # <--- APLICACIÓN DE LA CORRECCIÓN

        # La clave compuesta requiere PK y SK para eliminar
        table.delete_item(Key={'PK': data_pk, 'SK': '#METADATA#'})

        return {
            'statusCode': 204, # 204 No Content: éxito en la eliminación sin cuerpo de respuesta
            'headers': { 'Access-Control-Allow-Origin': '*' },
            'body': ''
        }
    except Exception as e:
        print(f"Error deleting data: {e}")
        return { 'statusCode': 500, 'body': json.dumps({'message': 'Error interno del servidor.'}) }

