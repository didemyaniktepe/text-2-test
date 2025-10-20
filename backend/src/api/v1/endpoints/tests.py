
import logging
from typing import List, Annotated

from src.services.test_case_service import TestCaseService
from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends
from src.core.container import Container

from ..schemas.test import (
    TestCaseCreate,
    TestGenerationResponse,
    TestStatusResponse
)

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/generate", response_model=TestGenerationResponse)
@inject
async def generate_test(
    request: TestCaseCreate,
    service: Annotated[TestCaseService, Depends(Provide[Container.test_case_service])]
):
    test_case = await service.create(
            scenario=request.scenario,
            url=request.url,
            folder_name=request.folder_name
    )
    return test_case

@router.post("/{test_id}/run",response_model=List[TestStatusResponse],)
@inject
async def run_test(
    test_id: str,
    service: Annotated[TestCaseService, Depends(Provide[Container.test_case_service])]
) -> List[TestStatusResponse]:
    status_updates = []
    async for status in service.run_test_by_id(test_id):
        status_updates.append(TestStatusResponse(
            test_id=test_id,
            status=status
    ))
    return status_updates


