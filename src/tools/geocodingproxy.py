import json
import requests
import json

def lambda_handler(event, context):
    agent = event['agent']
    actionGroup = event['actionGroup']
    apiPath = event['apiPath']
    httpMethod =  event['httpMethod']
    parameters = event.get('parameters', [])
    requestBody = event.get('requestBody', {})

    print(json.dumps(event))
    headers = {
        'content-type': 'application/json'
    }
    url = "http://api.openweathermap.org/geo/1.0/direct?q=London&limit=1&appid="
    response = requests.request("GET", url, headers=headers)
    #print(response.json()[0])
    r = {
        'name': response.json()[0]['name'],
        'country': response.json()[0]['country'],
        'lat': response.json()[0]['lat'],
        'lon': response.json()[0]['lon']
    }
    responseBody =  {
        "application/json": {
            "body": json.dumps(r)
        }
    }
    action_response = {
        'actionGroup': actionGroup,
        'apiPath': apiPath,
        'httpMethod': httpMethod,
        'httpStatusCode': 200,
        'responseBody': responseBody

    }

    responseBody = {'response': action_response, 'messageVersion': event['messageVersion']}
    
    print(responseBody)

    return responseBody
    


#lambda_handler(1,1)
