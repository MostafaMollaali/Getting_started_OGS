from pathlib import Path
import gmsh
import math

def create_rectangle_mesh(
    filepath: Path,
    width: float,
    height: float,
    mesh_size: float,
    center_z: float = 0.0
) -> None:

    gmsh.initialize()
    gmsh.option.setNumber("General.Verbosity", 0)
    gmsh.option.setNumber("Mesh.CharacteristicLengthMin", mesh_size)
    gmsh.option.setNumber("Mesh.CharacteristicLengthMax", mesh_size)
    gmsh.model.add(filepath.stem)

    z = center_z

    p1 = gmsh.model.occ.addPoint(0.0,    z + height/2, 0.0, mesh_size)
    p2 = gmsh.model.occ.addPoint(width,  z + height/2, 0.0, mesh_size)
    p3 = gmsh.model.occ.addPoint(width,  z - height/2, 0.0, mesh_size)
    p4 = gmsh.model.occ.addPoint(0.0,    z - height/2, 0.0, mesh_size)
    gmsh.model.occ.synchronize()

    l1 = gmsh.model.occ.addLine(p1, p2)
    l2 = gmsh.model.occ.addLine(p2, p3)
    l3 = gmsh.model.occ.addLine(p3, p4)
    l4 = gmsh.model.occ.addLine(p4, p1)
    gmsh.model.occ.synchronize()

    cl   = gmsh.model.occ.addCurveLoop([l1, l2, l3, l4])
    surf = gmsh.model.occ.addPlaneSurface([cl])
    gmsh.model.occ.synchronize()

    pg_domain = gmsh.model.addPhysicalGroup(2, [surf])
    gmsh.model.setPhysicalName(2, pg_domain, "domain")
    bcs = [("top", l1), ("right", l2), ("bottom", l3), ("left", l4)]
    for name, line in bcs:
        pg = gmsh.model.addPhysicalGroup(1, [line])
        gmsh.model.setPhysicalName(1, pg, name)

    gmsh.model.mesh.generate(2)
    gmsh.write(str(filepath.with_suffix(".msh")))
    gmsh.finalize()

def create_rectangle_frac_mesh(
    filepath: Path,
    width: float,
    height: float,
    mesh_size: float,
    center_z: float = 0.0,
    mode="domain",
) -> None:

    gmsh.initialize()
    gmsh.option.setNumber("General.Verbosity", 0)
    gmsh.option.setNumber("Mesh.CharacteristicLengthMin", mesh_size)
    gmsh.option.setNumber("Mesh.CharacteristicLengthMax", mesh_size)
    gmsh.model.add(filepath.stem)
    
    z = center_z
    
    # Define points
    p1 = gmsh.model.occ.addPoint(0.0, z + height / 2, 0.0, mesh_size)
    p2 = gmsh.model.occ.addPoint(width, z + height / 2, 0.0, mesh_size)
    p3 = gmsh.model.occ.addPoint(width, z - height / 2, 0.0, mesh_size)
    p4 = gmsh.model.occ.addPoint(0.0, z - height / 2, 0.0, mesh_size)
    
    # Fracture line
    angle_rad = math.radians(30.0)
    p5_x = 0.0
    p6_x = width
    p5_y = z - width * math.tan(angle_rad) / 2
    p6_y = z + width * math.tan(angle_rad) / 2
    
    p5 = gmsh.model.occ.addPoint(p5_x, p5_y, 0.0, mesh_size)
    p6 = gmsh.model.occ.addPoint(p6_x, p6_y, 0.0, mesh_size)
    gmsh.model.occ.synchronize()
    
    # Define lines
    l1 = gmsh.model.occ.addLine(p2, p1)
    l2 = gmsh.model.occ.addLine(p1, p5)
    l3 = gmsh.model.occ.addLine(p5, p4)
    l4 = gmsh.model.occ.addLine(p4, p3)
    l5 = gmsh.model.occ.addLine(p3, p6)
    l6 = gmsh.model.occ.addLine(p6, p2)
    l7 = gmsh.model.occ.addLine(p6, p5)
    gmsh.model.occ.synchronize()
    
    # Create surfaces
    cl1 = gmsh.model.occ.addCurveLoop([l1, l2, -l7, l6])
    surf1 = gmsh.model.occ.addPlaneSurface([cl1])
    cl2 = gmsh.model.occ.addCurveLoop([l4, l5, l7, l3])
    surf2 = gmsh.model.occ.addPlaneSurface([cl2])
    gmsh.model.occ.synchronize()
    
    if mode == "BC":
        bcs = [("top", l1), ("bottom", l4)]
        for name, line in bcs:
            pg = gmsh.model.addPhysicalGroup(1, [line])
            gmsh.model.setPhysicalName(1, pg, name)
    
        gmsh.model.addPhysicalGroup(1, [l5, l6], name="right")
        gmsh.model.addPhysicalGroup(1, [l2, l3], name="left")
        gmsh.model.addPhysicalGroup(0, [p4], name="p4")
    
    elif mode == "domain":
        gmsh.model.addPhysicalGroup(2, [surf1], name="top_surf")
        gmsh.model.addPhysicalGroup(2, [surf2], name="bot_surf")
        gmsh.model.addPhysicalGroup(1, [l7], name="fracture")
    
    gmsh.model.mesh.generate(2)
    gmsh.write(str(filepath.with_suffix(".msh")))
    gmsh.finalize()


def create_cube_mesh(
    filepath: Path,
    width: float,
    height: float,
    thickness: float,
    mesh_size: float,
    center_z: float = 0.0
) -> None:
    gmsh.initialize()
    gmsh.option.setNumber("General.Verbosity", 0)
    gmsh.option.setNumber("Mesh.CharacteristicLengthMin", mesh_size)
    gmsh.option.setNumber("Mesh.CharacteristicLengthMax", mesh_size)
    gmsh.model.add(filepath.stem)

    z0 = center_z - thickness/2.0
    z1 = center_z + thickness/2.0

    # 1) Create corner points
    coords = [
        (0.0,     0.0,     z0),  
        (width,   0.0,     z0),  
        (width,   height,  z0),  
        (0.0,     height,  z0),  
        (0.0,     0.0,     z1),  
        (width,   0.0,     z1),  
        (width,   height,  z1),  
        (0.0,     height,  z1)   
    ]
    pts = [gmsh.model.occ.addPoint(x, y, z, mesh_size) for x, y, z in coords]
    gmsh.model.occ.synchronize()

    l1  = gmsh.model.occ.addLine(pts[0], pts[1])
    l2  = gmsh.model.occ.addLine(pts[1], pts[2])
    l3  = gmsh.model.occ.addLine(pts[2], pts[3])
    l4  = gmsh.model.occ.addLine(pts[3], pts[0])
    l5  = gmsh.model.occ.addLine(pts[4], pts[5])
    l6  = gmsh.model.occ.addLine(pts[5], pts[6])
    l7  = gmsh.model.occ.addLine(pts[6], pts[7])
    l8  = gmsh.model.occ.addLine(pts[7], pts[4])
    l9  = gmsh.model.occ.addLine(pts[0], pts[4])
    l10 = gmsh.model.occ.addLine(pts[1], pts[5])
    l11 = gmsh.model.occ.addLine(pts[2], pts[6])
    l12 = gmsh.model.occ.addLine(pts[3], pts[7])
    gmsh.model.occ.synchronize()

    cl_bot   = gmsh.model.occ.addCurveLoop([ l1,  l2,  l3,  l4])
    cl_top   = gmsh.model.occ.addCurveLoop([ l5,  l6,  l7,  l8])
    cl_front = gmsh.model.occ.addCurveLoop([ l1,  l10, -l5,  -l9])
    cl_back  = gmsh.model.occ.addCurveLoop([-l3,  l11,  l7, -l12])
    cl_left  = gmsh.model.occ.addCurveLoop([ l9,  -l8, -l12,  l4])
    cl_right = gmsh.model.occ.addCurveLoop([ l10, l6,  -l11, -l2])
    gmsh.model.occ.synchronize()

    s_bot   = gmsh.model.occ.addPlaneSurface([cl_bot])
    s_top   = gmsh.model.occ.addPlaneSurface([cl_top])
    s_front = gmsh.model.occ.addPlaneSurface([cl_front])
    s_back  = gmsh.model.occ.addPlaneSurface([cl_back])
    s_left  = gmsh.model.occ.addPlaneSurface([cl_left])
    s_right = gmsh.model.occ.addPlaneSurface([cl_right])
    gmsh.model.occ.synchronize()

    sl  = gmsh.model.occ.addSurfaceLoop([s_bot, s_top, s_front, s_back, s_left, s_right])
    vol = gmsh.model.occ.addVolume([sl])
    gmsh.model.occ.synchronize()

    pg0 = gmsh.model.addPhysicalGroup(0, pts)
    gmsh.model.setPhysicalName(0, pg0, "points")

    all_edges = [l1, l2, l3, l4, l5, l6, l7, l8, l9, l10, l11, l12]
    pg1 = gmsh.model.addPhysicalGroup(1, all_edges)
    gmsh.model.setPhysicalName(1, pg1, "edges")

    face_map = {
        "bottom": s_bot,
        "top":    s_top,
        "front":  s_front,
        "back":   s_back,
        "left":   s_left,
        "right":  s_right,
    }
    for name, surf_tag in face_map.items():
        pg = gmsh.model.addPhysicalGroup(2, [surf_tag])
        gmsh.model.setPhysicalName(2, pg, name)

    pg3 = gmsh.model.addPhysicalGroup(3, [vol])
    gmsh.model.setPhysicalName(3, pg3, "volume")

    gmsh.model.mesh.generate(3)
    gmsh.write(str(filepath.with_suffix(".msh")))
    gmsh.finalize()