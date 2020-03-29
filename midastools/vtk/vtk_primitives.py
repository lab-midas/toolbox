import vtk
import random


def gen_plane(origin, normal):

    plane = vtk.vtkPlane()
    plane.SetOrigin(*origin)
    plane.SetNormal(*normal)
    plane.Update()

    return plane.GetOutput()


def gen_sphere(position, radius, res_phi=20, res_theta=20):

    sphere_source = vtk.vtkSphereSource()
    sphere_source.SetCenter(*position)
    sphere_source.SetRadius(radius)
    sphere_source.SetPhiResolution(res_phi)
    sphere_source.SetThetaResolution(res_theta)
    sphere_source.Update()

    return sphere_source.GetOutput()


def gen_arrow(res_tip, res_shaft):

    arrow_source = vtk.vtkArrowSource()
    arrow_source.SetTipResolution(res_tip)
    arrow_source.SetShaftResolution(res_shaft)
    arrow_source.Update()

    return arrow_source.GetOutput()


def gen_tube(polyline, radius=0.3, n_sides=50):

    tube_filter = vtk.vtkTubeFilter()
    tube_filter.SetInputData(polyline)
    tube_filter.SetRadius(radius)
    tube_filter.SetNumberOfSides(n_sides)
    tube_filter.Update()

    return tube_filter.GetOutput()


def gen_outline(vtk_poly):
    """
    generates a bounding box around given vtk_poly
    :return:
    """

    outline = vtk.vtkOutlineFilter()
    outline.SetInputData(vtk_poly)
    outline.Update()

    return outline.GetOutput()


def cut_surface(poly_surface, poly_cut):

    # generate cutter filter
    cutter = vtk.vtkCutter()
    cutter.SetCutFunction(poly_cut)
    cutter.SetInputData(poly_surface.GetOutput())
    cutter.Update()

    # convert polygons and lines to strips and polylines
    stripper = vtk.vtkStripper()
    stripper.SetInputData(cutter.GetOutput())
    stripper.Update()

    return stripper.GetOutput()


def fill_contour(vtk_poly):

    contour = vtk.vtkContourTriangulator()
    contour.SetInputData(vtk_poly)
    contour.Update()

    return contour.GetOutput()


def check_connectivity_closest(vtk_poly, origin=(0, 0, 0)):
    """
    Check connectivity of elements withing vtk_poly and keep the region closest to origin
    :param vtk_poly:
    :param origin:
    :return:
    """
    connectivity = vtk.vtkConnectivityFilter()
    connectivity.SetInputData(vtk_poly)
    connectivity.SetClosestPoint(origin)
    connectivity.SetExtractionModeToClosestPointRegion()
    connectivity.Update()

    return connectivity.GetOutput()


def apply_transform(vtk_poly, vtk_transform):

    transform_filter = vtk.vtkTransformPolyDataFilter()
    transform_filter.SetInputData(vtk_poly)
    transform_filter.SetTransform(vtk_transform)
    transform_filter.Update()

    return transform_filter.GetOutput()


def gen_transform(norm_x, norm_y, norm_z, translation=(0, 0, 0), scale=(1.0, 1.0, 1.0)):
    """
    create a vtkTransform based on the given vectors and scale factors
    :param matrix: a 4x4 matrix
    :param translation:
    :param scale:
    :return:
    """

    # Create the direction cosine matrix
    matrix = vtk.vtkMatrix4x4()
    matrix.Identity()
    for i in range(3):
        matrix.SetElement(i, 0, norm_x[i])
        matrix.SetElement(i, 1, norm_y[i])
        matrix.SetElement(i, 2, norm_z[i])

    # Apply the transforms
    vtk_transform = vtk.vtkTransform()
    vtk_transform.Translate(*translation)
    vtk_transform.Concatenate(matrix)
    vtk_transform.Scale(*scale)

    return vtk_transform


def normal_to_matrix(normal_vec):
    """
    generates direction cosines based on the given (normal) vector
    :return:
    """

    norm_x = normal_vec[:]
    norm_y = [0 for _ in range(3)]
    norm_z = [0 for _ in range(3)]

    # X axis is aligned to the given normal vector
    math = vtk.vtkMath()
    math.Normalize(norm_x)

    # The Z axis is an arbitrary vector cross X
    random_vec = [random.uniform(-1, 1) for _ in range(3)]
    math.Cross(norm_x, random_vec, norm_z)
    math.Normalize(norm_z)

    # The Y axis is Z cross X
    math.Cross(norm_z, norm_x, norm_y)

    return norm_x, norm_y, norm_z


def gen_mapper(vtk_poly):

    vtk_mapper = vtk.vtkPolyDataMapper()
    vtk_mapper.SetInputData(vtk_poly)
    vtk_mapper.Update()

    return vtk_mapper


def gen_actor(vtk_mapper):

    vtk_actor = vtk.vtkActor()
    vtk_actor.SetMapper(vtk_mapper)

    return vtk_actor


def poly_to_actor(vtk_poly):

    vtk_mapper = gen_mapper(vtk_poly)
    vtk_actor = gen_actor(vtk_mapper)

    return vtk_actor
