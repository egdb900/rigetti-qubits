from qubits import QubitLayout

# Test fixture using layout with the same dimensions as shown in the image
def test_layout():
    q1 = QubitLayout(2, 0.4, 0.3, 10, 4, 2)
    # Uncomment to load from json file (NOTE: Enter the filename minus the .json)
    # q1.from_json("qubit") 
    
    q1.create_layout()
    if q1.test_connectivity():
        print('Qubit layout is fully connected')
    else:
        print('Qubit layout is not fully connected')
    
    # Uncomment to save to json file (NOTE: Enter the filename minus the .json)
    # q1.to_json("qubit") 
    q1.schema_format()
    q1.write_to_gds("qubit")

if __name__=="__main__":
    test_layout()