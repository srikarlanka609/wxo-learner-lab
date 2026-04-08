import requests
import os
import json
from dotenv import load_dotenv

def get_bearer_token(api_key):
    """Get bearer token from API key using IBM Cloud IAM endpoints"""
    token_endpoints = [
        'https://iam.cloud.ibm.com/identity/token',  # Standard IBM Cloud IAM
        'https://iam.platform.saas.ibm.com/siusermgr/api/1.0/apikeys/token',  # Watson Orchestrate specific
    ]
    
    access_token = None
    last_error = None
    
    for token_url in token_endpoints:
        try:
            # Try standard IBM Cloud IAM format first
            if 'iam.cloud.ibm.com' in token_url:
                token_response = requests.post(
                    token_url,
                    headers={'Content-Type': 'application/x-www-form-urlencoded'},
                    data={
                        'grant_type': 'urn:ibm:params:oauth:grant-type:apikey',
                        'apikey': api_key
                    },
                    timeout=10
                )
            else:
                # Watson Orchestrate specific format
                token_response = requests.post(
                    token_url,
                    headers={'Content-Type': 'application/json'},
                    json={'apikey': api_key},
                    timeout=10
                )
            
            if token_response.status_code == 200:
                token_data = token_response.json()
                access_token = token_data.get('access_token')
                if access_token:
                    return access_token
            else:
                last_error = f"Status {token_response.status_code}: {token_response.text}"
                
        except Exception as e:
            last_error = str(e)
            continue
    
    # If we get here, all endpoints failed
    raise Exception(f"Failed to get bearer token from all endpoints. Last error: {last_error}")

def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Configuration from environment variables
    url = os.getenv("URL")
    api_key = os.getenv("API_KEY")
    company_name = os.getenv("COMPANY_NAME", "Default Company")
    
    # Check if environment variables are set
    if not url:
        print("Error: URL not found in .env file")
        return
    
    if not api_key:
        print("Error: API_KEY not found in .env file")
        print("Please add your IBM Cloud API key to the .env file:")
        print("  API_KEY=your_api_key_here")
        return
    
    # Check if API_KEY is still the placeholder text
    if api_key.startswith("<") or "your-api-key" in api_key.lower():
        print("Error: API_KEY not configured!")
        print("Please update the API_KEY variable in your .env file with your actual IBM Cloud API key.")
        return
    
    # Get bearer token from API key
    try:
        print("Getting bearer token from API key...")
        bearer_token = get_bearer_token(api_key)
        print("Successfully obtained bearer token!\n")
    except Exception as e:
        print(f"Error getting bearer token: {e}")
        return
    
    # Headers
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json",
        "Accept": "text/event-stream"
    }
    
    

    # Read company_json from file
    print("Reading company_json.txt file")
    try:
        with open("company_json.txt", "r", encoding="utf-8") as f:
            company_json = f.read()
    except FileNotFoundError:
        print("Error: company_json.txt not found")
        return
    except Exception as e:
        print(f"Error reading company_json.txt: {e}")
        return
    print("company_json.txt file was read")

    


    # Read question from file
    print("Reading question.txt file")
    try:
        with open("question.txt", "r", encoding="utf-8") as f:
            question = f.read()
    except FileNotFoundError:
        print("Error: question.txt not found")
        return
    except Exception as e:
        print(f"Error reading question.txt: {e}")
        return
    print("question.txt file was read")



    # Create JSON payload - request body format
    payload = {
        "parameters": {
            "max_new_tokens": 2000,
            "prompt_variables": {
                "company_json": company_json,
                "question": question
            }
        }
    }
    
    # Make the POST request
    try:
        print("Sending request...\n")
        print("=" * 70)
        print("RESPONSE:")
        print("=" * 70)
        
        response = requests.post(url, headers=headers, json=payload, stream=True)
        
        # Check if request was successful
        response.raise_for_status()
        
        # Stream the response
        for line in response.iter_lines():
            if line:
                line_text = line.decode('utf-8')
                
                # Parse the SSE format
                if line_text.startswith('data: '):
                    data_str = line_text[6:]  # Remove "data: " prefix
                    
                    # Skip [DONE] marker
                    if data_str.strip() == '[DONE]':
                        continue
                    
                    try:
                        # Parse JSON
                        data = json.loads(data_str)
                        
                        # Extract and print the generated text
                        if 'results' in data:
                            for result in data['results']:
                                if 'generated_text' in result:
                                    text = result['generated_text']
                                    print(text, end='', flush=True)
                                    
                    except json.JSONDecodeError:
                        # If not valid JSON, skip it
                        pass
        
        print("\n" + "=" * 70)
        print("STREAMING COMPLETE")
        print("=" * 70)
                
    except requests.exceptions.RequestException as e:
        print(f"\nError making request: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")

if __name__ == "__main__":
    main()