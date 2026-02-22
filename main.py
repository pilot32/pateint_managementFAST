from fastapi import FastAPI , Path , HTTPException , Query
from pydantic import BaseModel, Field,computed_field
from typing import Annotated, Literal
from fastapi.responses import JSONResponse
import json

app = FastAPI()
class Patient(BaseModel):
    id: Annotated[str, Field(..., description='ID of the patient', examples=['P001'])]
    name: Annotated[str, Field(..., description='Name of the patient', examples=['akshat'])]
    city: str
    age: Annotated[int, Field(gt=0, le=120)]  # Constraints: age must be 1-120
    gender: Annotated[Literal['male','female','others'],Field(...,description='Gender of te patient')]
    height: Annotated[float, Field(gt=0, description="Height in cm")]
    weight: Annotated[float, Field(gt=0, description="Weight in kg")]
    ## these are the computed fields which will be computed at the time of runtime 
    # 
    # 
    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round(self.weight/(self.height**2),2)
        return bmi
    @computed_field
    @property
    def verdict(self)-> str:
        if self.bmi < 18.5: 
            return 'Underweight'
        elif self.bmi < 25:
            return 'Normal'
        elif self.bmi < 30:
            return 'Normal'
        else:  
            return 'Obese'


def load_data():
    with open('patients.json' , 'r') as f:
        data =json.load(f) 
        return data
    
def save_data(data):
    with open('patients.json' , 'w') as f:
        json.dump(data,f)


@app.get('/')
async def root():
    return {"message": "Patient Management API Running"}


@app.get('/view')
def view    ():
    data = load_data()
    return data

@app.get('/patient/{patient_id}')
def view_patient(patient_id: str = Path(..., descipriton='ID of the patient in the db', example='P001' )):
    #load all pateints data
    data = load_data()

    if patient_id in  data:
        return data[patient_id]
    raise HTTPException(
        status_code=404,
        detail=f"pateint with user id {patient_id} not found"
    )

@app.get('/sort')
def sort_patient(sort_by: str=Query(...,description='sort on the bases if height weight or bmi') ,order: str = Query('asc',description='sort in ascending order')):
    valid_fields=['height','weight','bmi']

    if sort_by not in valid_fields:
        raise HTTPException(status_code=400,detail=f'invalid field selected from {valid_fields}')
    
    if order not in ['asc' , 'desc']:
        raise HTTPException(status_code=400,detail=f'invalid ordeer select  between asc or dsc')

    data = load_data()
    sort_order =True if order == 'desc' else False
    sorted_data = sorted(data.values(),key = lambda x: x.get(sort_by,0),reverse=sort_order)
    return sorted_data

#endpoint to post the user data into the json file 

@app.post('/create')

def create_patient(patient : Patient):
    #steo 1 load the existing pateint data 

    data = load_data()
    # check if th patient alread exist
    if patient.id in data:
        raise HTTPException(status_code=400,detail='patient already exist')

    #new paient add tot the database
    data[patient.id] = patient.model_dump(exclude=['id'])
    
    #save into json file 
     
    save_data(data)

    return JSONResponse(status_code=201,content={'message':'patient created succesfully!'})
