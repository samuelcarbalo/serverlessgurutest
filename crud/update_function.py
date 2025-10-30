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

# --- 4. U - UPDATE (Actualizar Producto) ---
def updateFunction(event, context):
    try:
        timestamp = str(datetime.now().timestamp())
        
        # 1. DECODIFICACIÓN Y DATOS DE ENTRADA
        data_sk = unquote(event['pathParameters']['id'])
        body = json.loads(event['body'])
        
        update_assignments = []
        expression_attribute_values = {':updatedAt': timestamp}
        expression_attribute_names = {'#updatedAt': 'updatedAt'}
        
        IGNORAR_KEYS = ['PK', 'SK', 'createdAt', 'updatedAt']

        # 2. CONSTRUCCIÓN DE LA EXPRESIÓN DINÁMICA
        for key, value in body.items():
            if key not in IGNORAR_KEYS:
                # Asignaciones (Ej: #name = :name)
                update_assignments.append(f'#{key} = :{key}')
                
                # Valores y Nombres
                expression_attribute_values[f':{key}'] = value
                expression_attribute_names[f'#{key}'] = key 

        # Si no hay campos válidos, devuelve 400
        if not update_assignments:
            return { 'statusCode': 400, 'body': json.dumps({'message': 'No se proporcionaron campos válidos para actualizar.'}) }

        # 3. ENSAMBLAJE DE LA EXPRESIÓN FINAL
        update_assignments.append('#updatedAt = :updatedAt')
        
        # Unir las asignaciones con comas y añadir 'SET ' al inicio
        update_expression_final = "SET " + ", ".join(update_assignments)

        # 4. PARÁMETROS Y EJECUCIÓN
        params = {
            'Key': {'PK': data_sk, 'SK': '#METADATA#'},
            'UpdateExpression': update_expression_final,
            'ExpressionAttributeValues': expression_attribute_values,
            'ExpressionAttributeNames': expression_attribute_names,
            'ReturnValues': 'ALL_NEW'
        }
        
        result = table.update_item(**params)
        
        return {
            'statusCode': 200,
            'headers': { 'Access-Control-Allow-Origin': '*' },
            'body': json.dumps(result['Attributes']) 
        }

    except Exception as e:
        print(f"Error updating data: {e}")
        return { 'statusCode': 500, 'body': json.dumps({'message': f'Internal Server Error. Detalle: {e}'}) }



