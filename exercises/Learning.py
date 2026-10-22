class LLMService: 
    def __init__(self, model_name: str)-> None: 
        self._modelName =model_name # create a private variable called modelName and assign the value of model_name that you just passed  to it.
        self._request_count: int =0
        
    @property
    def model_name(self): # object 
        return self._modelName
    
    @property
    def request_count(self):
        return self._request_count
    
    def ask(self, prompt):
        self._request_count +=1
        return f"[{self._modelName}] Response to : {prompt}"
    def __repr__(self):# 
        return f"LLMService(model_name={self._modelName!r}, request_count={self._request_count})"
    
service =LLMService("gpt-4")
print(service.model_name)
response = service.ask("What is Aria?")
service.ask("Where is Aria located?")
print(service.request_count)
print(service)


    
    
    