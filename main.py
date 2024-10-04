from fastapi import FastAPI,HTTPException
from database import db
from model import *
import uuid
import json
from fastapi.encoders import jsonable_encoder

app=FastAPI()

@app.get('/')
def main():
    return "Server Running Successfully"



#adding new project
@app.post('/newproject')
async def new_project(data: Newproject):
    try:
        collection = db['user']
        project_id = str(uuid.uuid4())

        existing_user = collection.find_one({'email': data.email})

        if existing_user:
            collection.update_one({"email": data.email}, {'$addToSet': {"admin": project_id}})
        else:
            new_user_data = {'email': data.email, 'admin': [project_id], 'developer': []}
            collection.insert_one(new_user_data)

        new_project_data = {
            'project_id': project_id,
            'project_name': data.project_name,
            'envs': []
        }
        project_collection = db['projects']
        project_collection.insert_one(new_project_data)

        response = jsonable_encoder({
            "detail": "Project added successfully",
            "project_id": project_id,  
            "project_name": data.project_name
        })
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add project: {str(e)}")


#adding env data into a project
@app.post('/addenv',response_model=Newenv)
async def add_env(data:Newenv):
    env_id=str(uuid.uuid4())
    try:
        collection=db['projects']
        collection.update_one({'project_id':data.project_id},{'$addToSet':{'envs':{
            "env_id":env_id, 
            "key_name":data.key_name,
            "key_value":data.key_value}
        }})
        return Newenv(
            project_id=data.project_id,
            key_name=data.key_name,
            key_value=data.key_value,
            env_id=env_id 
        )
    except:
        return {"message":"failed to add"}

    
#fetch project
@app.post('/getproject/{email}', response_model=UserProjectsResponse)
async def get_project(email: str):
    collection = db['user']
    user_data = collection.find_one({'email': email}, {'_id': 0})

    if user_data is None:
        raise HTTPException(status_code=404, detail="User not found")

    admin_list = user_data.get('admin', [])
    dev_list = user_data.get('developer', [])

    project_collection = db['projects']
    projects = []

    if admin_list:
        admin_projects = project_collection.find({'project_id': {'$in': admin_list}}, {'_id': 0})
        for project in admin_projects:
            projects.append(Project(**project, access_level='admin', env=project.get('envs', [])))

    if dev_list:
        dev_projects = project_collection.find({'project_id': {'$in': dev_list}}, {'_id': 0})
        for project in dev_projects:
            projects.append(Project(**project, access_level='developer', env=project.get('envs', []))) 

    return UserProjectsResponse(projects=projects)

#edit env data
@app.patch('/editenv')
async def edit_env(data: Editenv):
    collection = db['projects']
    
    result = collection.update_one(
        {"project_id": data.project_id, "envs.env_id": data.env_id},
        {"$set": {"envs.$.key_name": data.key_name, "envs.$.key_value": data.key_value}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Project or environment variable not found")
    
    return {"message": "Environment variable updated successfully"}


#delete project 
@app.delete('/deleteproject')
async def delete_project(data: DeleteProject):
    try:
        collection=db['projects']
        result=collection.delete_one({"project_id":data.project_id})

        user_collection=db['user']
        
        user_collection.update_one({'email':data.email},{'$pull':{'admin':data.project_id}})


        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Project not found")
        return {"message": "Project deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete project: {str(e)}")



#delete env data
@app.delete('/envdelete')
async def delete_env(data:DeleteEnv):
    try:
        collection=db['projects']
        result=collection.update_one({'project_id':data.project_id},{'$pull':{'envs':{'env_id':data.env_id}}})
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404,detail='Env not found')
        return {'message':'env deleted successfully'}
    except Exception as e:
        
        return HTTPException(status_code=500,detail=f'Failed to delete env data : {str(e)}')


#adding developer to the project by admin
@app.post('/add_developer')
async def add_developer(data:AddDeveloper):
    try:
        collection=db['user']
        user=collection.find_one({'email':data.email})
        print(data.email)
        if not user:
            raise HTTPException(status_code=403,detail='User does not exist')
        if data.project_id in user.get('developer', []):
            raise HTTPException(status_code=400, detail="Project already exists for this user")
        result = collection.update_one({'email':data.email},{'$addToSet':{'developer':data.project_id}})

        if result.modified_count==0:
            raise HTTPException(status_code=404,detail='Failed to Update')
        return {'message':'Updated Successfully'}
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Failed to add: {str(e)}')