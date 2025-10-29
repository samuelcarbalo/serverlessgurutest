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
        data_pk_encoded = event['pathParameters']['id']
        
        # 2. **DECODIFICAR** el valor para convertir %23 a #
        data_pk = unquote(data_pk_encoded) # <--- APLICACIÓN DE LA CORRECCIÓN

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
        
        # 1. DECODIFICACIÓN Y DATOS DE ENTRADA
        # Decodificar el PK para convertir %23 a #
        data_pk = unquote(event['pathParameters']['id'])
        body = json.loads(event['body'])
        
        update_assignments = []
        expression_attribute_values = {':updatedAt': timestamp}
        expression_attribute_names = {'#updatedAt': 'updatedAt'}
        
        IGNORAR_KEYS = ['PK', 'SK', 'createdAt', 'updatedAt']

        # 2. CONSTRUCCIÓN DE LA EXPRESIÓN DINÁMICA
        for key, value in body.items():
            if key not in IGNORAR_KEYS:
                # Conversión a Decimal para el precio
                
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
            'Key': {'PK': data_pk, 'SK': '#METADATA#'},
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
        return { 'statusCode': 500, 'body': json.dumps({'message': f'Error interno del servidor. Detalle: {e}'}) }

# --- 5. D - DELETE (Eliminar Producto) ---
def deleteFunction(event, context):
    try:
        data_pk_encoded = event['pathParameters']['id']
        
        # 2. **DECODIFICAR** el valor para convertir %23 a #
        data_pk = unquote(data_pk_encoded) # <--- APLICACIÓN DE LA CORRECCIÓN

        # La clave compuesta requiere PK y SK para eliminar
        table.delete_item(Key={'PK': data_pk, 'SK': '#METADATA#'})

        return {
            'statusCode': 204, # 204 No Content: éxito en la eliminación sin cuerpo de respuesta
            'headers': { 'Access-Control-Allow-Origin': '*' },
            'body': 'Item eliminado con exito.'
        }
    except Exception as e:
        print(f"Error deleting data: {e}")
        return { 'statusCode': 500, 'body': json.dumps({'message': 'Error interno del servidor.'}) }

