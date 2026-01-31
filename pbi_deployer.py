import requests
import json
import os

class PBIDeployer:
    def __init__(self, tenant_id, client_id, client_secret):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None

    def get_access_token(self):
        """Authenticates with Azure AD and returns an access token."""
        url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "https://analysis.windows.net/powerbi/api/.default"
        }
        response = requests.post(url, data=data)
        response.raise_for_status()
        self.access_token = response.json().get("access_token")
        return self.access_token

    def upload_pbix(self, group_id, pbix_file_path, display_name):
        """Uploads a PBIX file to a specific Power BI Workspace (Group)."""
        url = f"https://api.powerbi.com/v1.0/myorg/groups/{group_id}/imports?datasetDisplayName={display_name}"
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        with open(pbix_file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(url, headers=headers, files=files)
        
        response.raise_for_status()
        return response.json() # Returns import details including report ID

    def rebind_report(self, group_id, report_id, dataset_id):
        """Rebinds a report to a different dataset."""
        url = f"https://api.powerbi.com/v1.0/myorg/groups/{group_id}/reports/{report_id}/Rebind"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "datasetId": dataset_id
        }
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.status_code == 200

if __name__ == "__main__":
    print("Power BI Deployer logic ready.")
