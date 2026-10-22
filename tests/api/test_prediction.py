from fastapi.testclient import TestClient
from api.app import create_app
from api.dependencies import get_inference_service
from fastapi import Request

app = create_app()



class MockInferenceService:
    def predict(self, *args, **kwargs):
        return "mock_detected_class", 0.95
    
def override_get_inference_service(request: Request):
    return MockInferenceService()
    
app.dependency_overrides[get_inference_service] = override_get_inference_service 
    
client = TestClient(app)

# --- Your tests below will now run perfectly ---

def test_health():
    response=client.get("/health")
    
    assert response.status_code==200
    assert response.json()["status"]=="ok"
    
    
def test_predict():
    with open("test_image.png", "rb")  as image:
        response = client.post("/predict",
                               files={"file": ("test_image.png",
                                               image,
                                               "image/png")},)   
        assert response.status_code==200
        body=response.json()
        assert "class_name" in body
        assert "confidence" in body
        
def test_predict_rejects_invalid_file_type():
    response = client.post(
        "/predict",
        files={
            "file": ("malicious.txt", b"this is not an image, deribately send the wrong file to see if the security check works", "text/plain",)
        },
    )
    assert response.status_code == 400
    
def test_prediction_response_contract():
    with open("test_image.png", "rb") as image:
        response = client.post("/predict", 
                               files=
                               {"file": ("test_image.png",
                                         image, 
                                         "image/png",)},)
        body =response.json()
        assert isinstance(body["class_name"], str)
        assert isinstance(body["confidence"], float)