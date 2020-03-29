import vtk


def clean(vtk_poly):

    clean_poly = vtk.vtkCleanPolyData()
    clean_poly.SetInputData(vtk_poly)
    clean_poly.Update()

    return clean_poly.GetOutput()


def triangulate(vtk_poly):

    triangle = vtk.vtkTriangleFilter()
    triangle.SetInputData(vtk_poly)
    triangle.Update()

    return triangle.GetOutput()


def smooth(vtk_poly, smooth_filter='sinc', smooth_itr=40, relaxation=0.2):
    # TODO: investigate other options such as laplace beltrami, proper laplace smoothing or SPHARM

    if smooth_filter == 'laplacian':
        # performing Laplacian smoothing
        smoother = vtk.vtkSmoothPolyDataFilter()
        smoother.SetNumberOfIterations(smooth_itr)
        smoother.SetRelaxationFactor(relaxation)

    elif smooth_filter == 'sinc':
        # performing Sinc smoothing
        # Note: needs faces! otherwise segfault!
        # Note: works only with triangles
        smoother = vtk.vtkWindowedSincPolyDataFilter()
        smoother.SetNumberOfIterations(smooth_itr)

    else:
        raise ValueError(f'The filter type {smooth_filter} is not supported.')

    smoother.SetInputData(vtk_poly)
    smoother.FeatureEdgeSmoothingOff()
    smoother.BoundarySmoothingOn()
    smoother.Update()

    return smoother.GetOutput()


def reduce_poly(vtk_poly, decimator='pro', target_spacing=(1.0, 1.0, 1.0), target_reduction=0.5):
    """
    Possibly available decimators are: QuadricDecimation, QuadricClustering and DecimatePro
    """

    if decimator == 'pro':
        deci = vtk.vtkDecimatePro()
        deci.SetTargetReduction(target_reduction)
        deci.PreserveTopologyOn()
        deci.BoundaryVertexDeletionOn()
    elif decimator == 'quad':
        deci = vtk.vtkQuadricDecimation()
        deci.VolumePreservationOn()
        deci.SetTargetReduction(target_reduction)
    elif decimator == 'cluster':
        deci = vtk.vtkQuadricClustering()
        deci.SetDivisionSpacing(*target_spacing)
    else:
        raise ValueError(f'\'{decimator}\' is not a valid vtk decimator.')

    deci.SetInputData(vtk_poly)
    deci.Update()

    return deci.GetOutput()


def reeb_graph(poly):

    reeb = vtk.vtkPolyDataToReebGraphFilter()
    reeb.SetInputData(poly)
    reeb.Update()

    return reeb.GetOutput()


def reeb_skeleton(poly, reeb):

    # ReebGraphSurfaceSekeletonFilter atm not available through python
    raise NotImplementedError('vtk skeletonization is not available through python.')


def marching_cube(vtk_image, label_values=(1,)):
    """
    image to surface mesh conversion
    """

    march = vtk.vtkDiscreteMarchingCubes()
    march.SetInputData(vtk_image)
    march.SetNumberOfContours(len(label_values))
    for idx, value in enumerate(label_values):
        march.SetValue(idx, value)  # requires contour_idx, contour_value
    march.Update()

    return march.GetOutput()


def threshold(vtk_poly, min_val=0, max_val=1):

    vtk_thresh = vtk.vtkThreshold()
    vtk_thresh.SetInputData(vtk_poly)
    vtk_thresh.ThresholdBetween(min_val, max_val)
    vtk_thresh.Update()

    return vtk_thresh.GetOutput()

# TODO: threshold may be used with vtkExtractPolyDataGeometry?
# TODO: incorporate inspiration for mesh splitting: https://lorensen.github.io/VTKExamples/site/Cxx/Meshes/SplitPolyData/
