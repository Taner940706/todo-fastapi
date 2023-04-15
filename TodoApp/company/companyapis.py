from fastapi import APIRouter, Depends

from company import dependencies

router = APIRouter(
prefix="/companyapis",
    tags=["companyapis"],
    dependencies=[Depends(dependencies.get_token_header)],
    responses={418: {"description": "Internal Use Only"}}
)

@router.get("/")
async def get_company_name():
    return {"company_name": "Example Company"}

@router.get("/employees")
async def number_of_employees():
    return 162
