import vtk
from med_shape.utils_vtk import vtk_primitives, vtk_mesh, vtk_conversion


def smooth_actor(vtk_poly, b_calc_normals=True):
    """
    calc surface normals, perform triangle conversion and return an actor based on that data
    """

    if not b_calc_normals:
        vtk_poly_ren = vtk.vtkPolyData()
        vtk_poly_ren.DeepCopy(vtk_poly)
    else:
        poly_normals = vtk.vtkPolyDataNormals()
        poly_normals.SetInputData(vtk_poly)
        poly_normals.Update()
        vtk_poly_ren = poly_normals.GetOutput()

    # convert triangle polygons to strips
    stripper = vtk.vtkStripper()
    stripper.SetInputData(vtk_poly_ren)
    stripper.Update()

    actor = vtk_primitives.poly_to_actor(stripper.GetOutput())

    return actor


def render(list_actors, b_scalar_visibility=False):

    # Create a rendering window and renderer
    colors = vtk.vtkNamedColors()
    ren = vtk.vtkRenderer()
    ren_win = vtk.vtkRenderWindow()
    ren_win.AddRenderer(ren)
    ren.SetBackground(colors.GetColor3d('Black'))

    # Create a renderwindowinteractor
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(ren_win)

    # Assign actors to the renderer
    for actor in list_actors:
        if b_scalar_visibility:
            actor.GetMapper().ScalarVisibilityOn()
            actor.GetMapper().SetScalarModeToUsePointData()
            actor.GetMapper().SetColorModeToMapScalars()
        ren.AddActor(actor)

    # Enable user interface interactor
    iren.Initialize()
    ren_win.Render()
    # ren.GetActiveCamera().SetPosition(-0.5, 0.1, 0.0)
    # ren.GetActiveCamera().SetViewUp(0.1, 0.0, 1.0)
    # ren_win.Render()
    iren.Start()


def save_render(filename, vtk_render_window):

    image_filter = vtk.vtkWindowToImageFilter()
    image_filter.SetInput(vtk_render_window)
    image_filter.Update()

    writer = vtk.vtkPNGWriter()
    writer.SetFileName(filename)
    writer.SetInputData(image_filter.GetOutput())
    writer.Write()  # TODO: check if this needs an Update() step


def render_meshes(vtk_polys, opacity=0.5):
    """
    allows for simple visual comparison
    :param vtk_polys: list of vtk_poly data
    :return:
    """
    colors = vtk.vtkNamedColors()
    colors_selection = ['Red', 'Green', 'Blue', 'Brown', 'Yellow']

    actors = list()
    for idx_poly, vtk_poly_ in enumerate(vtk_polys):
        actors.append(smooth_actor(vtk_poly_))
        actors[-1].GetProperty().SetOpacity(opacity)
        actors[-1].GetProperty().SetColor(colors.GetColor3d(colors_selection[idx_poly]))

    render(actors)


if __name__ == '__main__':

    filename = '/home/rog/Desktop/hip_slicer/femur_model/femur_r_full.vtp'
    poly = vtk_conversion.read_vtp(filename)
    print('Poly', poly)
    poly_tri = vtk_mesh.triangulate(poly)
    print('Poly_tri', poly_tri)
    render(poly_tri)

    # image = itk_bridge.poly_to_img(poly_tri)
    # print(image)
    #reeb = reeb_graph(poly_tri)
    #print('Poly_reeb', reeb)
    # render(reader)

    # TODO: tal @ FitSplineToCutterOutput example
