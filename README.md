# Qubit Layout using gdspy library
## Python libraries:
1) pip install jsonschema (version 3.18.1) <br>
2) Linux <br>
pip install gdspy <br>
3) Windows <br>
download one of the gdspy configs from https://github.com/heitzmann/gdspy/releases (works on Python 2.7, 3.7, or 3.8) <br>
pip install [config location] <br>

## Running:
On command prompt/terminal run: python tester.py

### Notes on running:
- The import/deserialization section of the tester's code is currently commented out since there aren't any JSON files to import as is.
- You would only need to run it once to get a sample JSON file (qubit.json by default). After that you can uncomment the .from_json method and use its full functionality.
