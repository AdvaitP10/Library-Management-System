from typing import Optional, List, Annotated
from dotenv import load_dotenv
from fastapi import FastAPI, Body, HTTPException, status, Query
from fastapi.responses import Response
from pydantic import ConfigDict, BaseModel, Field
from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated
from bson import ObjectId
import motor.motor_asyncio
import os


app = FastAPI()
load_dotenv()

# connecting Database 
database_url = os.environ.get("DATABASE_URL")
client = motor.motor_asyncio.AsyncIOMotorClient(database_url)
db = client.library
student_collection = db.get_collection("students")

PyObjectId = Annotated[str, BeforeValidator(str)]


# Models
# address model for student model
class Address(BaseModel):
    city: str = Field(...)
    country: str = Field(...)

# student model
class StudentModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str = Field(...)
    age: int = Field(..., ge=0)
    address: Address
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "name": "Jane Doe",
                "age": 20,
                "address": {
                    "city": "Mumbai",
                    "country": "India"
                }
            }
        },
    )

# address model for updating address
class UpdateAddress(BaseModel):
    city: Optional[str] = None
    country: Optional[str] = None


# student model for updates
class UpdateStudentModel(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    address: Optional[UpdateAddress]
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "name": "Jane Doe",
                "age": 20,
                "address": {
                    "city": "Mumbai",
                    "country": "India"
                }
            }
        },
    )

# to return list of student
class StudentCollection(BaseModel):
    data: List[StudentModel]


# APIs
# POST request to create student entry in db
@app.post(
    "/students",
    response_description="Add new student",
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
)
async def create_students(student: StudentModel = Body(...)):
    new_student = await student_collection.insert_one(
        student.model_dump(by_alias=True, exclude=["id"])
    )
    created_student = await student_collection.find_one(
        {"_id": new_student.inserted_id}
    )
    return {"id": str(created_student["_id"])}

# GET request to get list of all students or list of students with applied filters like country or age
@app.get(
    "/students",
    response_description="List all students",
    response_model=StudentCollection,
    response_model_by_alias=False,
)
async def list_students(countryQuery: Annotated[str | None, Query(alias="Country")] = None, ageQuery: Annotated[int | None, Query(alias="Age")] = None):
    students = await student_collection.find().to_list(1000)
    filtered_students = []

    if ageQuery is not None and countryQuery is not None:
        for student in students:
            if student['age'] >= ageQuery and student['address']['country'] == countryQuery:
                filtered_students.append(student)

    elif ageQuery is not None:
        for student in students:
            if student['age'] >= ageQuery:
                filtered_students.append(student)
    
    elif countryQuery is not None:
        for student in students:
            if student['address']['country'] == countryQuery:
                filtered_students.append(student)
    
    else: return StudentCollection(data=students)
    
    return StudentCollection(data=filtered_students)

    


# GET request to find and return a student with a given id
@app.get(
    "/students/{id}",
    response_description="Get a single student",
    response_model=StudentModel,
    response_model_by_alias=False,
)
async def show_student(id: str):
    if (
        student := await student_collection.find_one({"_id": ObjectId(id)})
    ) is not None:
        return student

    raise HTTPException(status_code=404, detail=f"Student {id} not found")

# PATCH request to make changes in a particular student entry(by id)
@app.patch(
    "/students/{id}",
    response_description="Update a student",
    response_model_by_alias=False,
    status_code=status.HTTP_204_NO_CONTENT
)
async def update_student(id: str, student: UpdateStudentModel = Body(...)):
    student = {
        k: v for k, v in student.model_dump(by_alias=True).items() if v is not None
    }

    student_to_update = await student_collection.find_one({"_id": ObjectId(id)})
    actual_address = student_to_update['address']
    update_address = student['address']

    if len(student) >= 1:
        if update_address is not None:
            if update_address['city'] is not None:
                actual_address['city'] = update_address['city']
            if update_address['country'] is not None:
                actual_address['country'] = update_address['country']
            student["address"] = actual_address
        update_result = await student_collection.find_one_and_update(
            {"_id": ObjectId(id)},
            {"$set": student}
        )
        if update_result is not None:
            return {}
        else:
            raise HTTPException(status_code=404, detail=f"Student {id} not found")

        
# DELETE request to delete a student entry from the db with the given id
@app.delete("/students/{id}", response_description="Delete a student")
async def delete_student(id: str):
    delete_result = await student_collection.delete_one({"_id": ObjectId(id)})

    if delete_result.deleted_count == 1:
        return {}
    raise HTTPException(status_code=404, detail=f"Student {id} not found")