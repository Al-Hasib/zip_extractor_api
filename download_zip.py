import requests
import os


# 121281
username = "KGAUTO"
password = "K@A@2023"
output_path = "downloaded_vehicle_images.zip"

def download_zip_file(vin_number, username="KGAUTO", password="K@A@2023"):
    """
    Download a zip file from a URL with query parameters for authentication
    """
    url = "https://aisapi.gytech.biz/Main/vehicleimage/"
    url = url+vin_number
    try:
        # Add username and password as query parameters
        params = {
            'username': username,
            'password': password
        }
        
        # Send GET request with parameters
        response = requests.get(url, params=params, stream=True)
        
        # Print response details for debugging
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {response.headers}")
        
        # Check if the request was successful
        if response.status_code == 200:
            # Create directory if it doesn't exist
            Output_file = f"{vin_number}.zip"
            # os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
            output_path = os.path.join("zip_file", Output_file)
            
            # Write the content to file
            with open(output_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
            
            print(f"Successfully downloaded zip file to {output_path}")
            return output_path
        else:
            print(f"Response content: {response.text[:200]}...")  # Print first 200 chars of response
            return output_path
    
    except Exception as e:
        print(f"Error downloading file: {str(e)}")
        return False

# Usage example
url = "https://aisapi.gytech.biz/Main/vehicleimage/121281"
username = "KGAUTO"
password = "K@A@2023"
output_path = "downloaded_vehicle_images.zip"

# download_zip_file(url, output_path, username, password)