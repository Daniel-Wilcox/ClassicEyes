import importlib.util
import os


# from app_files.pages import (HomePage, Page1, Page2)


def import_from_filepath(module_name: str, filepath: str):

    # Validate the provided path
    filepath = os.path.abspath(filepath)
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Module '{module_name}' doesn't exists at {filepath}.")

    # Create a module spec from the file path
    spec = importlib.util.spec_from_file_location(module_name, filepath)
    if spec is None:
        raise ImportError(f"Couldn't load spec for module {module_name}' from '{filepath}'")

    # Create a new module based on the spec
    module = importlib.util.module_from_spec(spec)

    # Execute the module (this runs the file)
    if spec.loader is not None:
        spec.loader.exec_module(module)
    else:
        raise ImportError(f"Could not load module '{module_name}' from '{filepath}'")

    return module



def get_page_classes(pages_dir:str):
    # Get list of module names (filename without extension)
    python_page_files = [
            os.path.splitext(page_name)[0]
            for page_name in os.listdir(pages_dir) 
            if page_name.endswith(".py") and not page_name.startswith("_") and not page_name.startswith("Abstract")
        ]
    
    # Assuming module and filename are the same
    all_modules = [
        import_from_filepath(
            module_name, os.path.join(pages_dir, f"{module_name}.py")
        )
        for module_name in python_page_files
    ]
    return all_modules


    
def main():
    # Define init defaults
    root_path = os.getcwd()
    # print(f"{root_path = }")

    app_files_path = os.path.join(root_path, "app_files")
    # print(f"{app_files_path = }")

    all_pages_path = os.path.join(app_files_path, "pages")
    # print(f"{all_pages_path = }")

    all_handlers_path = os.path.join(app_files_path, "handlers")
    # print(f"{all_handlers_path = }")

    # page_classes_user = [HomePage, Page1, Page2]
    page_classes_func = get_page_classes(all_pages_path)


    test = [
        os.path.splitext(module)[0]
        for module in os.listdir(all_pages_path)
        if module.endswith(".py") and not module.startswith("_") and not module.startswith("abstract")
    ]

    print(f"{test = }")


    print(page_classes_func[1])

    

if __name__ == "__main__":
    main()
