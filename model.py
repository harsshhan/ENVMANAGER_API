from pydantic import BaseModel
from typing import Optional,List,Dict,Any

class Newproject(BaseModel):
    email:str
    project_name:str
    
class Newenv(BaseModel):
    project_id:str
    key_name:str
    key_value:str

class Editenv(BaseModel):
    project_id:str
    env_id:str
    key_name:str
    key_value:str

class DeleteEnv(BaseModel):
    project_id:str
    env_id:str

class Project(BaseModel):
    project_id: str
    project_name: str
    env: Optional[List[Dict[str, Any]]] = [] 
    access_level: str 

class UserProjectsResponse(BaseModel):
    projects: List[Project]