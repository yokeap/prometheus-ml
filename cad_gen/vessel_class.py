import os
import sys
import numpy as np
freecad_libs = [
    '/usr/local/lib/FreeCAD.so',
    '/usr/lib/freecad-python3/lib/FreeCAD.so',
    '/usr/lib/freecad-python3/lib/',
]
# freecad_libs ='/usr/lib/freecad-python3/lib/'

for lib in freecad_libs:
    if os.path.exists(lib):
        path = os.path.dirname(lib)
        if path not in sys.path:
            sys.path.append(path)
        break

else:
    raise ValueError("FreeCAD library was not found!")

import FreeCAD                              # noqa
from FreeCAD import Units                   # noqa

femtools_libs = [
    '/usr/local/Mod/Fem/femtools',
    '/usr/share/freecad/Mod/Fem/femtools',
]
for lib in femtools_libs:
    if os.path.exists(lib):
        path = os.path.dirname(lib)
        if path not in sys.path:
            sys.path.append(path)
        path = os.path.abspath(os.path.join(lib, '..', '..'))
        if path not in sys.path:
            sys.path.append(path)
        path = os.path.abspath(os.path.join(lib, '..', '..', '..', 'Ext'))
        if path not in sys.path:
            sys.path.append(path)
        break
else:
    raise ValueError("femtools library was not found!")

from femtools.ccxtools import FemToolsCcx   # noqa
from femmesh.gmshtools import GmshTools     # noqa

import MeshPart
import Mesh

class Vessel(object):
    """
    The base class to work with parametric pressure vessel models.
    """

    def __init__(self, filename: str, debug=True):
        """
        Creates a pressure vessel analysis class that can be used to run
        multiple simulations for the given design template by changing its
        parameters.
        """
        self.filename = filename
        self.debug = debug

        print("Opening:", filename)
        self.doc = FreeCAD.open(filename)
        FreeCAD.setActiveDocument("vessel_c")
        self.doc = FreeCAD.ActiveDocument 
        self.exp_index = None

        self.sketch_params = []
        obj = self.doc.getObject('Sketch')

        """
            print('***Parametric properties are:***')
            print('Sketch is:')
            for c in obj.Constraints:
                if c.Name:
                    self.sketch_params.append(str(c.Name))
                    print(str(c.Name))
            """

    def set_low1_len(self, line_a1):
            try: 
                obj = self.doc.getObject('Sketch028') 
                obj.setDatum('myhull_a1', Units.Quantity(line_a1 , Units.Unit('mm')))
                self.doc.recompute()
            except: 
               print('failed in setting line_a1 length')
            # except Exception as e:
            #     print(e)    
    def set_low2_len(self, line_a2):
        try: 
            obj = self.doc.getObject('Sketch028') 
            obj.setDatum('myhull_a2', Units.Quantity(line_a2 , Units.Unit('mm')))
            self.doc.recompute()
        except: 
               print('failed in setting line_a2 length')
               
    def set_medium1_len(self, line_b1):
            try: 
                obj = self.doc.getObject('Sketch026') 
                obj.setDatum('myhull_b1', Units.Quantity(line_b1 , Units.Unit('mm')))
                self.doc.recompute()
            except: 
             print('failed in setting line_b1 length')

    def set_medium2_len(self, line_b2):
        try: 
            obj = self.doc.getObject('Sketch026') 
            obj.setDatum('myhull_b2', Units.Quantity(line_b2 , Units.Unit('mm')))
            self.doc.recompute()
        except: 
            print('failed in setting line_b2 length')
    def set_bow_len(self, line_d1):
        try: 
            obj = self.doc.getObject('Sketch029') 
            obj.setDatum('myhull_d1', Units.Quantity(line_d1 , Units.Unit('mm')))
            self.doc.recompute()
        except: 
            print('failed in setting line_d1 length')               
               
    def get_low1_details(self):
         obj_spz = self.doc.getObject('Sketch028')  
         my_a1=obj_spz.getDatum('myhull_a1').getValueAs('mm')
         return(my_a1)
         
    def get_low2_details(self):
        obj_spz = self.doc.getObject('Sketch028')  
        my_a2=obj_spz.getDatum('myhull_a2').getValueAs('mm')
        return(my_a2)
    
    def get_medium1_details(self):
        obj_spz = self.doc.getObject('Sketch026')  
        my_b1=obj_spz.getDatum('myhull_b1').getValueAs('mm')
        return(my_b1)
        
    def get_medium2_details(self):
        obj_spz = self.doc.getObject('Sketch026')  
        my_b2=obj_spz.getDatum('myhull_b2').getValueAs('mm')
        return(my_b2)
    def get_bow_details(self):
        obj_spz = self.doc.getObject('Sketch029')  
        my_d1=obj_spz.getDatum('myhull_d1').getValueAs('mm')
        return(my_d1)

            
        # self.doc.save()

        return (my_a)
    
    def sketch_edit(self, sketch_name, data_name, val):
        try:
            sketch = self.doc.getObject(sketch_name) 
            
            sketch.setDatum(data_name, Units.Quantity(val, Units.Unit('mm')))       
            
            sketch.touch()
            sketch.recompute()
            
            # Find and Force-Recompute Interpolation Curve
            for obj in self.doc.Objects:
                if obj.TypeId == "Part::FeaturePython":  # Check for generic FeaturePython objects
                    print(f"Recomputing {obj.Label} (Curves Workbench Feature)...")

                    # 🔹 Try to find the real update function
                    if hasattr(obj, "execute"):
                        print(f"Calling execute() on {obj.Label}")
                        obj.execute()
                    elif hasattr(obj, "onChanged"):
                        print(f"Calling onChanged() on {obj.Label}")
                        obj.onChanged("Geometry")  # Simulate a geometry change
                    elif hasattr(obj, "touch"):
                        print(f"Calling touch() on {obj.Label}")
                        obj.touch()
                        obj.recompute()
                        self.doc.recompute()
                    else:
                        print(f"⚠️ No update method found for {obj.Label}")

                    obj.recompute()  # Force recompute after trying updates
                    

            self.doc.recompute()  # Recompute document to apply changes across all dependencies
            print("Document recomputed and dependencies updated.")
            

        except Exception as e:
            print(e)


    def recompute(self):
        """
        Recompute the design after setting all parametric values of design
        """
        self.clean()
        self.doc.recompute()

    def create_stl(self, exp_index):
        """
        Generate stl file from the current design
        """
        # try:
        self.doc.recompute()

        # Find the Compound object
        compound_obj = None
        for obj in self.doc.Objects:
            if "Compound" in obj.TypeId and obj.Shape is not None:
                compound_obj = obj
                break

        if not compound_obj:
            print("No Compound object found.")
            exit()

        compound_obj.touch()
        self.doc.recompute()

        if not compound_obj.Shape:
            print(
                "Error: Compound object has no valid shape. Check interpolation settings.")
            exit()

        # 🔹 Force a deep copy to refresh shape
        compound_obj.Shape = compound_obj.Shape.copy()
        self.doc.recompute()

        # 🔹 Convert to solid if needed
        try:
            solid_shape = compound_obj.Shape.Solid
            if not solid_shape.isValid():
                print(
                    "Warning: Shape is not a valid solid. Proceeding with the existing shape.")
                solid_shape = compound_obj.Shape
        except AttributeError:
            solid_shape = compound_obj.Shape

        # Convert Compound to Mesh
        mesh = MeshPart.meshFromShape(
            Shape=solid_shape, LinearDeflection=0.0001, AngularDeflection=0.1, Relative=True)
        mesh_obj = self.doc.addObject("Mesh::Feature", "Compound_Mesh")
        mesh_obj.Mesh = mesh

        self.doc.recompute()

        # print(__objs__.Name, self.doc.Name)
        stl_name = u"./stl_repo/ship_gen.stl"
        Mesh.export([mesh_obj], stl_name)
        del compound_obj
        # except Exception as e:
        # print(e)
 #     # print("An error occurred while creating stl file")

    def get_exp_index(self) -> int:
        """
        Returns the experiment index of current design.
        """
        print('self index is:', self.exp_index)
        return self.exp_index

    def set_exp_index(self, exp_ind) -> int:
        """
        set the experiment index of current design
        """
        self.exp_index = exp_ind

    def clean(self):
        """
        Removes all temporary artifacts from the model.
        """
        if self.doc.getObject('CCX_Results'):
            self.doc.removeObject('CCX_Results')
        if self.doc.getObject('ResultMesh'):
            self.doc.removeObject('ResultMesh')
        if self.doc.getObject('ccx_dat_file'):
            self.doc.removeObject('ccx_dat_file')


if __name__ == '__main__':
    run()
