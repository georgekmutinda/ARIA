from pathlib import Path
Test = Path("Test")
print(Test)
print(Test.resolve())
Test.mkdir(exist_ok=True)
Test = Test / "Test1"
print(Test)
print(Test.resolve())
with open(Test, "w") as f: 
    f.write("The start of the text file")
    #context = f.read() this doesn't work because the file is opened in write mode, so you can't read from it. You can only write to it. If you want to read from the file, you need to open it in read mode.
    
