import json
import random

def lambda_handler(event, context):
    agent = event['agent']
    actionGroup = event['actionGroup']
    api_path = event['apiPath']
    httpMethod = event['httpMethod']
    parameters = event.get('parameters', [])
    
    # Fetching the 'requestBody' from the correct location in the event structure
    requestBody = event.get('requestBody', {}).get('content', {}).get('application/json', {})
    session_attributes = event['sessionAttributes']
    prompt_session_attributes = event['promptSessionAttributes']
    messageVersion = event['messageVersion']  # Corrected syntax error here

    print(json.dumps(event))

    # Assuming that 'body' contains the actual data payload
    if 'properties' in requestBody:
        body = {prop['name']: prop['value'] for prop in requestBody['properties']}
    else:
        body = {}

    if api_path == '/customers' and httpMethod == 'GET':
        r = get_customers(event, context)
    elif api_path == '/customers' and httpMethod == 'POST':
        r = create_customer(body, context)  # Pass the extracted 'body' here
    elif api_path == '/orders' and httpMethod == 'GET':
        r = get_orders(event, context)
    elif api_path == '/orders' and httpMethod == 'POST':
        r = create_order(body, context)  # Pass the extracted 'body' here
    elif api_path.startswith('/customer_orders/') and httpMethod == 'PUT':
        r = update_order(body, context)  # Pass the extracted 'body' here
    elif api_path.startswith('/customer_orders/') and httpMethod == 'GET':
        r = get_customer_orders(event, context)
    elif api_path == '/products' and httpMethod == 'GET':
        r = get_products(event, context)
    else:
        return {
            'statusCode': 404,
            'body': json.dumps('Not Found')
        }

    responseBody = {
        "application/json": {
            "body": r
        }
    }
    action_response = {
        'actionGroup': actionGroup,
        'apiPath': api_path,
        'httpMethod': httpMethod,
        'httpStatusCode': 200,
        'responseBody': responseBody
    }

    api_response = {
        'messageVersion': '1.0',
        'response': action_response,
        'sessionAttributes': session_attributes,
        'promptSessionAttributes': prompt_session_attributes
    }

    print(api_response)

    return api_response

# Mock data for customers, orders, and products
mock_customers = [
    {'id': 1, 'name': 'John Doe'},
    {'id': 2, 'name': 'Jane Smith'},
    {'id': 3, 'name': 'Alice Johnson'},
    {'id': 4, 'name': 'Bob Brown'},
    {'id': 5, 'name': 'Eve White'}
]

mock_orders = [
    {'id': 1, 'customerId': 1, 'productId': 101, 'quantity': 2},
    {'id': 2, 'customerId': 2, 'productId': 102, 'quantity': 1},
    {'id': 3, 'customerId': 3, 'productId': 103, 'quantity': 3},
    {'id': 4, 'customerId': 4, 'productId': 104, 'quantity': 4},
    {'id': 5, 'customerId': 5, 'productId': 105, 'quantity': 5}
]

mock_products = [
    {'id': 101, 'name': 'Laptop', 'price': 899.99},
    {'id': 102, 'name': 'Smartphone', 'price': 699.99},
    {'id': 103, 'name': 'Tablet', 'price': 399.99},
    {'id': 104, 'name': 'Headphones', 'price': 149.99},
    {'id': 105, 'name': 'Smart Watch', 'price': 249.99}
]

def get_customers(event, context):
    return json.dumps(mock_customers[:5])  # Return first 5 records

def create_customer(body, context):
    new_customer_data = body
    new_customer_data['id'] = random.randint(100, 999)  # Randomly generate an ID
    return json.dumps(new_customer_data)

def get_orders(event, context):
    return json.dumps(mock_orders[:5])  # Return first 5 records

def create_order(body, context):
    new_order_data = body
    new_order_data['id'] = random.randint(1000, 9999)  # Randomly generate an ID
    return json.dumps(new_order_data)

def update_order(body, context):
    # Assuming the 'body' parameter contains the updated order data
    return json.dumps(body)

def get_customer_orders(event, context):
    # Extracting customerId from the parameters list in the event
    customer_id = None
    for param in event.get('parameters', []):
        if param['name'] == 'customerId':
            customer_id = int(param['value'])
            break

    if customer_id is None:
        return {
            'statusCode': 400,
            'body': json.dumps('customerId parameter is missing or invalid.')
        }

    # Filter orders based on the extracted customer_id
    customer_orders = [order for order in mock_orders if order['customerId'] == customer_id]

    return {
        'statusCode': 200,
        'body': json.dumps(customer_orders[:5])  # Return first 5 records
    }

def get_products(event, context):
    return json.dumps(mock_products[:5])  # Return first 5 records
