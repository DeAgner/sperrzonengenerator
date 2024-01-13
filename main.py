import tkinter as tk
from tkinter import filedialog
import ifcopenshell
from ifcopenshell.api import run
import uuid
import ifcopenshell.template
import ifcopenshell.geom
import numpy as np
import ifcopenshell.util.placement
import os

from Processors.ifc_import import open_ifc_file
from Processors.ifc_filter import get_ifc_object_guids_with_material, get_transformed_wall_vertices, flatten_wall_vertices
from Processors.merge_coordinates import merge_coordinates_within_radius
from Processors.sperrzonen import create_ifcaxis2placement, create_ifclocalplacement, create_ifcpolyline, create_ifcextrudedareasolid

class IFCGeneratorGUI:
    def __init__(self, master):
        self.master = master
        master.title("Sperrzonen Generator")

        # Label und Entry für den IFC-Dateipfad
        self.label_ifc_path = tk.Label(master, text="IFC-Dateipfad:")
        self.label_ifc_path.pack()

        self.entry_ifc_path = tk.Entry(master)
        self.entry_ifc_path.pack()

        # Button zum Durchsuchen und Auswählen des IFC-Dateipfads
        self.btn_browse_ifc = tk.Button(master, text="Durchsuchen", command=self.browse_ifc_file)
        self.btn_browse_ifc.pack()

        # Label und Entry für den Radius
        self.label_radius = tk.Label(master, text="Merge Radius:")
        self.label_radius.pack()

        self.entry_radius = tk.Entry(master)
        self.entry_radius.pack()

        # Label und Entry für den Sperrzonen-Radius
        self.label_sp_radius = tk.Label(master, text="Sperrzonen-Radius:")
        self.label_sp_radius.pack()

        self.entry_sp_radius = tk.Entry(master)
        self.entry_sp_radius.pack()

        # Label und Entry für die Sperrzonen-Höhe
        self.label_sp_height = tk.Label(master, text="Sperrzonen-Höhe:")
        self.label_sp_height.pack()

        self.entry_sp_height = tk.Entry(master)
        self.entry_sp_height.pack()

        # Label und Entry für den Ausgabepfad
        self.label_output_path = tk.Label(master, text="Ausgabepfad:")
        self.label_output_path.pack()

        self.entry_output_path = tk.Entry(master)
        self.entry_output_path.pack()

        # Button zum Generieren der IFC-Datei
        self.btn_generate_ifc = tk.Button(master, text="IFC generieren", command=self.generate_ifc)
        self.btn_generate_ifc.pack()

    # Pfad IFC File

    def browse_ifc_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("IFC Dateien", "*.ifc")])
        self.entry_ifc_path.delete(0, tk.END)
        self.entry_ifc_path.insert(0, file_path)

    # Inputs angeben

    def generate_ifc(self):
        ifc_file_path = self.entry_ifc_path.get()
        radius = float(self.entry_radius.get())
        sp_radius = float(self.entry_sp_radius.get())
        sp_height = float(self.entry_sp_height.get())
        output_path = self.entry_output_path.get()

       
        # IFC-Modell öffnen
        ifc_file = open_ifc_file(ifc_file_path)

        # Materialfilter: Nur Wände aus Beton
        desired_materials = ["Beton"]
        object_types = ["IfcWall", "IfcColumn"]

        # Erhalten Sie die GUIDs von IFC-Objekten mit dem gewünschten Material
        guids = get_ifc_object_guids_with_material(ifc_file, object_types, desired_materials)

        print("GUIDs der Objekte mit dem gewünschten Material:", guids)

        # Liste umformatieren
        mod_walls = get_transformed_wall_vertices(ifc_file, guids)
        flat_list = flatten_wall_vertices(mod_walls)

        # Das Ergebnis ist eine flache Liste von Floats
        print(flat_list)

        # Merge der Koordinaten
        coordinates = flat_list
        result = merge_coordinates_within_radius(coordinates, radius)

        # Liste von Floats umwandeln
        flat_coordinates = [array.tolist() for array in result]
        print("\nFlache Koordinatenliste:")
        print(flat_coordinates)

        def zone(p):
            list_w = []
            for index, item in enumerate(p):
                w = ifcfile.createIfcBuildingElementProxy(
                    create_guid(),
                    owner_history,
                    "SPZ_"+str(index+1),
                    "Beschreibung der SPZ",
                    None,
                    create_ifclocalplacement(ifcfile, point=item),
                    product_shape,
                    None
                )
                list_w.append(w)
            return list_w

        create_guid = lambda: ifcopenshell.guid.compress(uuid.uuid1().hex)

        # Erstellung von IFC-Vorlagen
        ifcfile = ifcopenshell.template.create(
            filename="Sperrzonen",
            creator="Dominik Agner",
            organization="HSLU",
            schema_identifier="IFC2x3",
            project_name="Test Zone Creation"
        )

        # Erhalten Sie Referenzen zu Instanzen, die in der Vorlage definiert sind
        owner_history = ifcfile.by_type("IfcOwnerHistory")[0]
        project = ifcfile.by_type("IfcProject")[0]
        context = ifcfile.by_type("IfcGeometricRepresentationContext")[0]

        # Erstellen Sie einen Standort, ein Gebäude und ein Stockwerk. Viele Hierarchien sind möglich.
        site = run("root.create_entity", ifcfile, ifc_class="IfcSite", name="My Site")
        building = run("root.create_entity", ifcfile, ifc_class="IfcBuilding", name="Building A")
        storey = run("root.create_entity", ifcfile, ifc_class="IfcBuildingStorey", name="Ground Floor")

        # Da der Standort unsere oberste Ebene ist, weisen Sie ihn dem Projekt zu.
        # Platzieren Sie dann unser Gebäude auf dem Grundstück und unser Stockwerk in dem Gebäude.
        run("aggregate.assign_object", ifcfile, relating_object=project, product=site)
        run("aggregate.assign_object", ifcfile, relating_object=site, product=building)
        run("aggregate.assign_object", ifcfile, relating_object=building, product=storey)

        settings = ifcopenshell.geom.settings()
        settings.set(settings.USE_WORLD_COORDS, True)

        #Solid und Shape für Sperrzone erstellen
       
        ##Sperrzone Parameter

        polyline = create_ifcpolyline(ifcfile, [(0.0, 0.0, 0.0), (0.0, 0.0, sp_height)])

        solid = ifcfile.createIfcSweptDiskSolid()

        solid.Directrix = polyline

        solid.Radius = sp_radius
        solid.InnerRadius=None
        solid.StartParam = 0.0
        solid.EndParam = 1.0

        body_representation = ifcfile.createIfcShapeRepresentation(context, "Body", "AdvancedSweptSolid", [solid])

        product_shape = ifcfile.createIfcProductDefinitionShape(None, None, [body_representation])

        wall_list = zone(flat_coordinates)

        # Beziehen Sie das Fenster und die Wand auf das Stockwerk des Gebäudes
        ifcfile.createIfcRelContainedInSpatialStructure(
            create_guid(),
            owner_history,
            "Building Storey Container",
            None,
            wall_list,
            storey)

        # Schreiben des Inhalts der IFC  Datei auf die Festplatte
        ifcfile.write(output_path)

        print(f"IFC-Datei generiert und gespeichert unter: {output_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = IFCGeneratorGUI(root)
    root.mainloop()