import requests
from dotenv import load_dotenv
import os
from datetime import datetime
from typing import Optional, Dict, Any, List

load_dotenv()

BASE_URL = os.getenv("API_NEW_URL")

def get_projects():
    response = requests.get(f"{BASE_URL}/projects/all")
    return response.json()

def get_project(project_id):
    response = requests.get(f"{BASE_URL}/projects/{project_id}")
    return response.json()

def update_project_dates(project_id,data):
    response = requests.put(f"{BASE_URL}/projects/{project_id}/dates", json=data)
    return response.json()

def update_project(project_id,data):
    response = requests.patch(f"{BASE_URL}/projects/{project_id}", json=data)
    return response.json()