import math
class Student:
    
    count = 0
    total_age = 0
    
    def __init__(self, name, age):
        self.name=name
        self.age = age
        Student.count +=1
        Student.total_age+=age# whenever a student is created increment the count
        
    #INSTANCE METHODS
    def get_info(self): # the self here represents who called the class, like whose info are you getting
        return f"Name: {self.name}, Age : {self.age}"
    
    @classmethod
    def get_count(cls): # which class are we getting the count of 
        return f"Total student count is {cls.count}"
    
    @classmethod
    def get_average_age(cls):
        if cls.count==0:
            return f"Enter students first"
        else:
            average = math.floor(cls.total_age/cls.count)
            return f"Average age of students is {average}"

student1 = Student("John", 15)
student2 = Student("Mika", 14)
student3 =Student("JOhn", 17)

print(student1.get_info())

print(Student.get_count())
print(Student.get_average_age())
    