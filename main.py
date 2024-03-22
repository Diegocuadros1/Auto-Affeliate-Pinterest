import requests
import os
from dotenv import load_dotenv
from create.creating_poster import create_poster


load_dotenv()

API_TOKEN = os.getenv('AIRTABLE_API_TOKEN')
    
AIRTABLE_BASE_ID = "apprPJ63OMWs0lMpU"

airtable_number = input("Row to be created: ")

airtable_number = (f'{{row-number}}="{airtable_number}"')

endpoint = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/Amazon-data?view=Grid%20view"

headers = {
    "Authorization": f"Bearer {API_TOKEN}"
}

params = {
    'pageSize': 1,
    'filterByFormula': airtable_number
}




response = requests.get(endpoint, headers=headers, params=params)

if response.status_code == 200:
    records = response.json()
    print("received api from airtable...")
    
    for record in records["records"]:
        fields = record["fields"]
        create_poster(fields)
        print("Product Affeliate Link: ", fields["Product URL AFF"])
else:
    print("There has been a" + response.status_code + "error")

