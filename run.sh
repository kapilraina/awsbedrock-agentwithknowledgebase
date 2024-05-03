python3 -m venv brkba 
source brkba/bin/activate
pip install -r requirements.txt 
aws cloudformation deploy --template template.yaml --stack-name akb-demo-stack OR
sam deploy --region us-east-1