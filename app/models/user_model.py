from pydantic import BaseModel, EmailStr

class RegisterPatientRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: str

class RegisterDoctorRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: str
    specialization: str
    qualification: str
    experience: int = 0
    hospital_name: str
    hospital_address: str
    city: str
    state: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str