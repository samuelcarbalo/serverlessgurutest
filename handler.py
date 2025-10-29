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
            'PK': "PRODUCT#" + str(uuid.uuid4()),
            'SK': "#METADATA#",
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
        data_pk = event['pathParameters']['PK']
        
        result = table.get_item(Key={'PK': data_pk, 'SK': '#METADATA#'})
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

# --- 4. U - UPDATE (Actualizar Producto) ---
def updateFunction(event, context):
    try:
        timestamp = str(datetime.now().timestamp())
        data_pk = event['pathParameters']['PK']
        body = json.loads(event['body'])
        
        # Prepara la expresión de actualización
        update_expression = ['SET']
        expression_attribute_values = {':updatedAt': timestamp}
        
        # Iterar sobre el cuerpo para construir la expresión de actualización
        for key, value in body.items():
            if key not in ['PK', 'SK', 'createdAt']: # Ignorar claves primarias y fecha de creación
                # Ejemplo: SET #n = :v, ...
                update_expression.append(f'#{key} = :{key}')
                expression_attribute_values[f':{key}'] = value

        # Si no hay campos para actualizar, devolver 400
        if len(update_expression) == 1:
            return { 'statusCode': 400, 'body': json.dumps({'message': 'No se proporcionaron campos válidos para actualizar.'}) }

        # Añadir updatedAt al final
        update_expression.append('#updatedAt = :updatedAt')
        
        params = {
            'Key': {'PK': data_pk, 'SK': '#METADATA#'},
            'UpdateExpression': ' '.join(update_expression).replace(' ,', ',').replace('SET #', 'SET #', 1),
            'ExpressionAttributeValues': expression_attribute_values,
            'ExpressionAttributeNames': {f'#{key}': key for key in body.keys() if key not in ['PK', 'SK', 'createdAt']} | {'#updatedAt': 'updatedAt'},
            'ReturnValues': 'ALL_NEW' # Devuelve el item actualizado
        }
        
        # Ejecutar la actualización
        result = table.update_item(**params)
        
        return {
            'statusCode': 200,
            'headers': { 'Access-Control-Allow-Origin': '*' },
            'body': json.dumps(result['Attributes'])
        }

    except Exception as e:
        print(f"Error updating data: {e}")
        return { 'statusCode': 500, 'body': json.dumps({'message': 'Error interno del servidor.'}) }

# --- 5. D - DELETE (Eliminar Producto) ---
def deleteFunction(event, context):
    try:
        data_pk = event['pathParameters']['PK']

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

