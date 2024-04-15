import json
import jsonschema
import gdspy

class QubitLayout:
    def __init__(self, junction_width=2, junction_length=4, wire_width=0.3, wire_length=10, connection_radius=4, wire_offset=0.7):
        self.junction_width = junction_width
        self.junction_length = junction_length
        self.wire_width = wire_width
        self.wire_length = wire_length
        self.connection_radius = connection_radius
        self.wire_offset = wire_offset
        self.layers = {
            "junction": 1,
            "wire": 2,
            "connection": 3
        }
        
        self.lib = gdspy.GdsLibrary()
        self.layout = gdspy.Cell('QUBIT_LAYOUT')
        
        # Schema used to validate imported JSON files
        self.schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "QubitLayout",
            "type": "object",
            "properties": {
                "junction_width": { "type": "number" },
                "junction_length": { "type": "number" },
                "wire_width": { "type": "number" },
                "wire_length": { "type": "number" },
                "connection_radius": { "type": "number" },
                "wire_offset": { "type": "number" },
                "layers": {
                    "type": "object",
                    "properties": {
                        "junction": { "type": "integer" },
                        "wire": { "type": "integer" },
                        "connection": { "type": "integer" }
                    },
                    "required": ["junction", "wire", "connection"]
                }
            },
            "required": ["junction_width", "junction_length", "wire_width", "wire_length", "connection_radius", "wire_offset", "layers"]
        }

    # Create a junction cell
    def create_junction(self):
        junction = gdspy.Cell('JUNCTION')
        junction.add(gdspy.Rectangle((-self.junction_width/2, -self.junction_length/2), (self.junction_width/2, self.junction_length/2), layer=self.layers["junction"]))
        return junction

    # Create a wire cell
    def create_wire(self):
        wire = gdspy.Cell('WIRE')
        wire.add(gdspy.Rectangle((-self.wire_width/2, 0), (self.wire_width/2, self.wire_length), layer=self.layers["wire"]))
        return wire
    
    # Create a connection cell
    def create_connection(self):
        connection = gdspy.Cell('CONNECTION')
        connection.add(gdspy.Round((0, 0), self.connection_radius, layer=self.layers["connection"]))
        return connection

    # Connect the junction, wire, and connection cells to their proper positions
    def connect_wires(self, junction, wire, connection):
        # Create a cell and translate the connection at the end of the wire
        wire_connection = gdspy.Cell('WIRE_CONNECTION')
        wire_connection.add([gdspy.CellReference(wire), gdspy.CellReference(connection, (0, self.wire_length))])
        
        # Create a cell and translate the wire_connection at each end of the junction
        wc1 = gdspy.CellReference(wire_connection, (-self.wire_offset, 0))
        wc2 = gdspy.CellReference(wire_connection, (self.wire_offset, 0), rotation = 180)
        
        self.layout.add([wc1, wc2])
        self.layout.add(gdspy.CellReference(junction))

    # Create the layout
    def create_layout(self):
        junction = self.create_junction()
        wire = self.create_wire()
        connection = self.create_connection()
        
        self.connect_wires(junction, wire, connection)
        self.lib.add(self.layout)
        gdspy.LayoutViewer()
        return self.layout
    
    # Write the layout to a gds and svg file
    def write_to_gds(self, filename):
        self.lib.write_gds(filename + '.gds')
        self.layout.write_svg(filename + '.svg')

    # Serialize the layout properties to a json file
    def to_json(self, filename):
        data = {
            "junction_width": self.junction_width,
            "junction_length": self.junction_length,
            "wire_width": self.wire_width,
            "wire_length": self.wire_length,
            "connection_radius": self.connection_radius,
            "wire_offset": self.wire_offset,
            "layers": {
                "junction": self.layers["junction"],
                "wire": self.layers["wire"],
                "connection": self.layers["connection"]
            }
        }

        out_file = open(filename + ".json", 'w')
        json_str = json.dump(data, out_file, indent=2)
        return json_str

    # Unserialize/parse the layout properties from a json file
    def from_json(self, filename):
        in_file = open(filename + ".json", "r")
        data = json.load(in_file)
        
        # Validate the json file against the schema
        if jsonschema.validate(data, schema=self.schema):
            raise Exception("Invalid JSON file")
        
        self.junction_width = data["junction_width"]
        self.junction_length = data["junction_length"]
        self.wire_width = data["wire_width"]
        self.wire_length = data["wire_length"]
        self.connection_radius = data["connection_radius"]
        self.wire_offset = data["wire_offset"]        
        self.layers = data["layers"]
    
    # Write the schema format to a JSON file
    def schema_format(self):
        out_file = open("schema.json", "w")
        json.dump(self.schema, out_file, indent=2)
    
    # Test that confirms the layout is fully connected with no gaps between features 
    def test_connectivity(self):
        polygons = self.layout.get_polygonsets()
        graph = {polygon: [] for polygon in polygons}
        
        # Create a graph of the polygons and check if they are connected
        for i in range(len(polygons)):
            for j in range(len(polygons)):
                if i != j and gdspy.boolean(polygons[i], polygons[j], 'and') != None:
                    graph[polygons[i]].append(polygons[j])
                    graph[polygons[j]].append(polygons[i])
        
        visited = set()
        stack = graph[polygons[0]]
        
        # Perform a depth-first search to check if all polygons are connected
        while stack:
            polygon = stack.pop()
            if polygon not in visited:
                visited.add(polygon)
                stack.extend(set(graph[polygon]) - visited)
        
        # Check if all polygons were visited
        return len(visited) == len(polygons)