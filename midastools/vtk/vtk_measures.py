import vtk


def calc_mass_properties(vtk_poly):

    mass_props = vtk.vtkMassProperties()
    mass_props.SetInputData(vtk_poly)
    mass_props.Update()

    volume = mass_props.GetVolume()
    surface_area = mass_props.GetSurfaceArea()
    shape_index = mass_props.GetNormalizedShapeIndex()

    return volume, surface_area, shape_index


# TODO: integrate function to calculate point to surface distance via vtkImplicitPolyDataDistance
