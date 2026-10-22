class BaseServive:
    def __init__(self, name:str) -> None:
        self.name = name
        
    def health_check(self) -> dict:
        return{"service": self.name, "status": "Ok"}
    
class LLMService(BaseServive):
    def __init__(self, model_name:str) -> None:
        super().__init__("LLMService")
        self._model_name = model_name
        
    def health_check(self) -> dict:
        base_result =super().health_check()
        base_result["model_name"] = self._model_name
        return base_result