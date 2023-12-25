import ifcopenshell
from ifccsv import IfcCsv

model = ifcopenshell.open("./data/leapfrog_examples/Boreholes_with_lithology.ifc")
# Using the selector is optional. You may specify elements as a list manually if you prefer.
# e.g. elements = model.by_type("IfcElement")
elements = ifcopenshell.util.selector.Selector.parse(model, ".IfcElement")
attributes = ["Name", "Description"]

# Export our model's elements and their attributes to a CSV.
ifc_csv = IfcCsv()
ifc_csv.export(model, elements, attributes, output="out.csv", format="csv", delimiter=",", null="-")

# Optionally, you can explicitly export to different formats.
# ifc_csv = IfcCsv()
# ifc_csv.export(model, elements, attributes)
ifc_csv.export_csv("out.csv", delimiter=";")
# ifc_csv.export_ods("out.ods")
# ifc_csv.export_xlsx("out.xlsx")

# Optionally, you can create a Pandas DataFrame.
df = ifc_csv.export_pd()
print(df)

# Optionally, you can directly fetch the headers and rows as Python lists.
print(ifc_csv.headers)
print(ifc_csv.results)

# You can also import changes from a CSV
ifc_csv.Import(model, "input.csv")
model.write("/path/to/updated_model.ifc")