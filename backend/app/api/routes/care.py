from fastapi import APIRouter, Query

from app.schemas.analysis import ProviderEntry
from app.services.care_navigation_service import provider_directory


router = APIRouter(tags=["care"])


@router.get("/care/providers", response_model=list[ProviderEntry])
def get_care_providers(city: str | None = Query(default=None)):
    providers = provider_directory()
    if city:
        city_norm = city.strip().lower()
        providers = [p for p in providers if p.city.lower() == city_norm]
    return providers
