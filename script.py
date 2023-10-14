# Import necessary libraries
import clr
import math
from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, ElementId

# Connect to the Revit Document
doc = _revit_.ActiveUIDocument.Document

# 1. Data Collection and Filtering:

# Collect all pipes in the model
pipes = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Pipe).WhereElementIsNotElementType().ToElements()

# Filter pipes based on System Abbreviation
valid_abbreviations = ["DOM", "IND", "PLU"]
filtered_pipes = [pipe for pipe in pipes if pipe.LookupParameter("System Abbreviation").AsString() not in valid_abbreviations]

# Further filter based on "Slope", "HID_RamalIndividual", and "HID_ColetorPredial"
final_pipes = []
for pipe in filtered_pipes:
    slope = pipe.LookupParameter("Slope").AsString()
    ramal_individual = pipe.LookupParameter("HID_RamalIndividual").AsInteger()
    coletor_predial = pipe.LookupParameter("HID_ColetorPredial").AsInteger()
    
    if slope != "" and (ramal_individual == 0 or coletor_predial == 1):
        final_pipes.append(pipe)

# Extract relevant data from filtered pipes
pipe_data = []
for pipe in final_pipes:
    flow = pipe.LookupParameter("Flow").AsDouble()
    inside_diameter = pipe.LookupParameter("Inside Diameter").AsDouble()
    slope = pipe.LookupParameter("Slope").AsDouble()
    
    pipe_type_id = pipe.GetTypeId()
    pipe_type = doc.GetElement(pipe_type_id)
    coef_rugosidade = pipe_type.LookupParameter("HID_Coef_Rugosidade").AsDouble()
    
    system_type = doc.GetElement(pipe.LookupParameter("System Type").AsElementId())
    key_group = system_type.LookupParameter("HID_KeyGroup").AsString()
    
    data = {
        "Flow": flow,
        "Inside Diameter": inside_diameter,
        "Slope": slope,
        "HID_Coef_Rugosidade": coef_rugosidade,
        "HID_KeyGroup": key_group
    }
    pipe_data.append(data)
    
# 2. Calculation for each Pipe:

for pipe, data in zip(final_pipes, pipe_data):
    # Calculate Qc and teta based on HID_KeyGroup
    Qa = data["Flow"] * 60
    if data["HID_KeyGroup"] != "HID_10":
        teta = 2 * math.pi
        Qc1 = 7.3497 * Qa ** 0.5352
        if Qc1/Qa < 0.2:
            Cs = 0.2
        elif Qc1/Qa > 1:
            Cs = 1
        else:
            Cs = Qc1/Qa
        Qc = Qa * Cs * 10**(-3)/60
    else:
        teta = math.pi
        Qc = Qa * 10**(-3)

    # Define Dint, Inc, and Ks
    Dint = data["Inside Diameter"] * 0.001
    Inc = data["Slope"] * 0.01
    Ks = data["HID_Coef_Rugosidade"]

    # Iterate to find the teta value that gives the minimum positive value of "new"
    min_new = float('inf')
    optimal_teta = teta
    for t in [i * 0.000001 for i in range(int(teta/0.000001))]:
        new_value = Ks * (Dint*2)/8 * (t - math.sin(t)) * (Dint/4(t - math.sin(t))/t)*(2/3) * (Inc)*(1/2) - Qc
        if 0 < new_value < min_new:
            min_new = new_value
            optimal_teta = t

    # Update the relevant parameters in the Revit model (assuming a parameter named "Teta" exists for storing the optimal teta value)
    pipe.LookupParameter("Teta").Set(optimal_teta)