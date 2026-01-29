import os  
import json  
  
# Define the file paths in the order they should appear in the new script  
file_paths = [  
    "extractors/__init__.py",  
    "extractors/extractor.py",  
    "extractors/shape_extractors/__init__.py",  
    "extractors/shape_extractors/base_shape_extractor.py",  
    "extractors/shape_extractors/text_shape_extractor.py",  
    "extractors/shape_extractors/table_shape_extractor.py",  
    "extractors/shape_extractors/picture_shape_extractor.py",  
    "recreator/__init__.py",  
    "recreator/recreator.py",  
    "recreator/shape_recreators/__init__.py",  
    "recreator/shape_recreators/base_shape_recreator.py",  
    "recreator/shape_recreators/text_shape_recreator.py",  
    "recreator/shape_recreators/table_shape_recreator.py",  
    "recreator/shape_recreators/picture_shape_recreator.py",  
    "utils/__init__.py",  
    "utils/argument_parser.py",  
    "utils/color_utils.py",  
    "main.py",  
    "README.md"  
]  
  
# Create a dictionary to store file paths and contents  
file_structure = {}  
  
# Iterate over the file paths  
for file_path in file_paths:  
    # Open each file in read mode  
    with open(file_path, "r") as file:  
        # Store the file content in the dictionary  
        file_structure[file_path] = file.read()  
  
# Write the file_structure dictionary to a new script  
with open("create_project.py", "w") as new_script:  
    new_script.write("import os\n")  
    new_script.write("import json\n\n")  
    new_script.write(f"file_structure = {json.dumps(file_structure)}\n\n")  
    new_script.write("""  
# Create directories and files  
for file_path, content in json.loads(file_structure).items():  
    directory = os.path.dirname(file_path)  
    if directory and not os.path.exists(directory):  
        os.makedirs(directory)  
  
    with open(file_path, "w") as file:  
        file.write(content)  
""")  
  
print("create_project.py created successfully.")  
