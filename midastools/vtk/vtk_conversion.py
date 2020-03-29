import vtk
from vtk.util import numpy_support
import math


def poly_to_img(poly, origin=None, dim=None, spacing=(1.0, 1.0, 1.0)):

    # compute dimensions and origin
    bounds = [0 for _ in range(6)]
    poly.GetBounds(bounds)
    if dim is None:
        dim = [0 for _ in range(3)]
        for idx_dim in range(3):
            dim[idx_dim] = int(math.ceil((bounds[idx_dim * 2 + 1] - bounds[idx_dim * 2]) / spacing[idx_dim]))

    if origin is None:
        origin = [0 for _ in range(3)]
        origin[0] = bounds[0]  # + spacing[0]/2
        origin[1] = bounds[2]  # + spacing[0]/2
        origin[2] = bounds[4]  # + spacing[0]/2

    # generate empty image volume
    image_ = vtk.vtkImageData()
    image_.SetSpacing(*spacing)
    image_.SetDimensions(*dim)
    image_.SetExtent(0, dim[0]-1, 0, dim[1]-1, 0, dim[2]-1)
    image_.SetOrigin(*origin)
    image_.AllocateScalars(vtk.VTK_UNSIGNED_CHAR, 1)

    # fill image with foreground voxels
    inval = 1
    outval = 0
    count = image_.GetNumberOfPoints()
    for idx_pix in range(count):
        image_.GetPointData().GetScalars().SetTuple1(idx_pix, inval)

    # create image stencil
    pol_to_stenc = vtk.vtkPolyDataToImageStencil()
    pol_to_stenc.SetTolerance(0)
    pol_to_stenc.SetInputData(poly)
    pol_to_stenc.SetOutputOrigin(*origin)
    pol_to_stenc.SetOutputSpacing(*spacing)
    pol_to_stenc.SetOutputWholeExtent(image_.GetExtent())
    pol_to_stenc.Update()

    # cut the corresponding white image and set the background
    image_stenc = vtk.vtkImageStencil()
    image_stenc.SetInputData(image_)
    image_stenc.SetStencilData(pol_to_stenc.GetOutput())
    image_stenc.ReverseStencilOff()
    image_stenc.SetBackgroundValue(outval)
    image_stenc.Update()

    return image_stenc.GetOutput()


def np_verts_to_vtk_poly(np_verts, np_triangles=None):
    """
    Takes in N_v x 3 numpy array of coordinates and N_t x 3 numpy array of triangle faces
    """

    vtk_points = vtk.vtkPoints()
    vtk_vertices = vtk.vtkCellArray()

    vtk_poly = vtk.vtkPolyData()

    verts_temp = np_verts.tolist()
    for vert_ in verts_temp:
        id = vtk_points.InsertNextPoint(vert_)
        vtk_vertices.InsertNextCell(1)
        vtk_vertices.InsertCellPoint(id)

    vtk_poly.SetVerts(vtk_vertices)
    vtk_poly.SetPoints(vtk_points)

    if np_triangles is not None:
        vtk_triangles = vtk.vtkCellArray()

        triangles_temp = np_triangles.tolist()
        for tri_ in triangles_temp:
            vtk_tri = vtk.vtkTriangle()
            vtk_tri.GetPointIds().SetId(0, tri_[0])
            vtk_tri.GetPointIds().SetId(1, tri_[1])
            vtk_tri.GetPointIds().SetId(2, tri_[2])
            vtk_triangles.InsertNextCell(vtk_tri)

        vtk_poly.SetPolys(vtk_triangles)

    return vtk_poly


def vtk_poly_to_np_verts(vtk_poly):
    """
    Note: code expects that polydata contains vertices and only triangle polygons
    :param vtk_poly:
    :return:
    """

    # make sure you're fetching the correct info GetVerts() / GetPoints()
    vtk_verts = vtk_poly.GetPoints()
    np_verts = numpy_support.vtk_to_numpy(vtk_verts.GetData())

    vtk_poly_cells = vtk_poly.GetPolys()
    n_polys = vtk_poly.GetNumberOfPolys()
    np_triangles_raw = numpy_support.vtk_to_numpy(vtk_poly_cells.GetData())
    np_triangles = np_triangles_raw.reshape((n_polys, -1))[..., 1:]  # Note: there is currently no check that assures that triangles are received

    return np_verts, np_triangles


def vtk_to_itk_image(image_vtk):

    # TODO: needs ITKVtkGlue which requires ITK to be compiled from source and built again a specific VTK version
    #       pypi wheel is coming - try from source https://github.com/InsightSoftwareConsortium/ITKVtkGlue/blob/master/setup.py in the meantime
    raise NotImplementedError('Requires ITKVtkGlue module during ITK compilation.')


def vtk_to_numpy_image(vtk_image):

    dims = vtk_image.GetDimensions()
    data = vtk_image.GetPointData().GetScalars()  # was .GetArray(0)

    np_image = numpy_support.vtk_to_numpy(data)
    np_image = np_image.reshape(dims, order='F')

    return np_image


def np_to_vtk_data(np_data):

    # convert numpy array to vtk image data object
    vtk_data = numpy_support.numpy_to_vtk(num_array=np_data.ravel(order='f'),
                                          deep=True,
                                          array_type=vtk.VTK_UNSIGNED_CHAR)

    return vtk_data


def np_to_vtk_points(np_points):
    """

    :param points: numpy array (Nx3) of coordinates)
    :return:
    """

    points_temp = np_points.tolist()

    vtk_points = vtk.vtkPoints()
    vtk_points.SetNumberOfPoints(len(points_temp))
    for idx, point in enumerate(points_temp):
        vtk_points.SetPoint(idx, *point)

    return vtk_points


def vtk_points_to_polyline(vtk_points):
    """

    creates a polyline, creating lines along point path
    :param vtk_points:
    :return:
    """

    lines = vtk.vtkCellArray()
    for k in range(vtk_points.GetNumberOfPoints() - 1):
        line = vtk.vtkLine()
        line.GetPointIds().SetId(0, k)
        line.GetPointIds().SetId(1, k + 1)
        lines.InsertNextCell(line)

    polyline = vtk.vtkPolyData()
    polyline.SetLines(lines)
    polyline.SetPoints(vtk_points)

    return polyline


def vtk_data_to_image(vtk_data, dims, origin=(0, 0, 0), spacing=(1, 1, 1)):

    # generate vtk image volume from vtk data array
    vtk_image = vtk.vtkImageData()
    vtk_image.SetSpacing(*spacing)
    vtk_image.SetDimensions(*dims)
    vtk_image.SetExtent(0, dims[0] - 1, 0, dims[1] - 1, 0, dims[2] - 1)
    vtk_image.SetOrigin(*origin)
    vtk_image.GetPointData().SetScalars(vtk_data)

    return vtk_image


def extract_geometry(vtk_unstructured):

    vtk_geometry = vtk.vtkGeometryFilter()
    vtk_geometry.SetInputData(vtk_unstructured)
    vtk_geometry.Update()

    return vtk_geometry.GetOutput()


def read_vtp(filename):

    reader = vtk.vtkXMLPolyDataReader()
    reader.SetFileName(filename)
    reader.Update()

    return reader.GetOutput()


def write_vtp(filename, poly):

    writer = vtk.vtkXMLPolyDataWriter()
    writer.SetFileName(filename)
    writer.SetInputData(poly)
    writer.Write()


def deep_copy(vtk_poly):

    vtk_poly_copy = vtk.vtkPolyData()
    vtk_poly_copy.DeepCopy(vtk_poly)

    return vtk_poly_copy
