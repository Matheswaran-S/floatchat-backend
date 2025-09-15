from fastapi import APIRouter

# Create a router object
router = APIRouter()

# Example endpoint: fake ocean data
@router.get("/mock")
def get_mock_data():
    return {
        "location": "Arabian Sea",
        "depth": "100m",
        "temperature": "25°C",
        "salinity": "35 PSU"
    }
# Example: dynamic endpoint using query parameter
@router.get("/temperature")
def get_temperature(depth: int):
    # For now, return a fake temperature based on depth
    temp = 25 - (depth / 1000)  # just a simple formula
    return {
        "location": "Arabian Sea",
        "depth": f"{depth}m",
        "temperature": f"{temp:.1f}°C"
    }
# Example: dynamic endpoint for salinity
@router.get("/salinity")
def get_salinity(depth: int):
    # Fake salinity based on depth
    salinity = 35 + (depth / 2000)  # deeper → slightly more saline
    return {
        "location": "Arabian Sea",
        "depth": f"{depth}m",
        "salinity": f"{salinity:.2f} PSU"
    }
