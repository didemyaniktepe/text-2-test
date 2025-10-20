from datetime import datetime
from pydantic import BaseModel
from src.domain.test.entities.test_case import TestCase
from src.domain.test.value_objects.test_status import TestStatus

class TestCaseCreate(BaseModel):
    scenario: str 
    url: str
    folder_name: str = "" 
    
class TestGenerationResponse(BaseModel):
    id: str 
    url: str 
    scenario: str 
    generated_script: str
    created_at: datetime 
    status: TestStatus 
    
    @classmethod
    def from_entity(cls, entity: TestCase) -> "TestGenerationResponse":
        return cls(
            id=entity.id,
            url=entity.url,
            scenario=entity.scenario,
            generated_script=entity.generated_script,
            created_at=entity.created_at,
            status=entity.status
        )
        
class TestStatusResponse(BaseModel):
    test_id: str 
    status: TestStatus 
