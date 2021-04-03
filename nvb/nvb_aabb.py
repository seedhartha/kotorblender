import mathutils


def generate_tree(aabb_tree, face_list, rlevel = 0):
    if (rlevel > 128):
        print("WARNING: Error generating aabb. Recursion level exceeds 128")
        aabb_tree = []
        return

    if not face_list:
        # We are finished with the generation
        return

    # Calculate Bounding box centers and min/max coordinates
    bb_min         = mathutils.Vector(( 100000.0,  100000.0,  100000.0))
    bb_max         = mathutils.Vector((-100000.0, -100000.0, -100000.0))
    bb_avgcentroid = mathutils.Vector((0.0, 0.0, 0.0))
    for face in face_list:
        face_vertices = face[1]
        # Every vertex in the face
        for vertex in face_vertices:
            # We have to check 2x3 coordinates (min and max)
            for ax in range(3):
                # First the min
                if bb_min[ax] > vertex[ax]:
                    bb_min[ax] = vertex[ax]
                # Then the max
                if bb_max[ax] < vertex[ax]:
                     bb_max[ax] = vertex[ax]

        face_centroid = face[2]
        bb_avgcentroid = bb_avgcentroid + face_centroid

    bb_avgcentroid = bb_avgcentroid / len(face_list)

    bb_centroid = (bb_min + bb_max) /2

    if (len(face_list) == 1):
        # Only one face left in face list
        # This node is a leaf, save the face in the leaf
        linked_face_idx = face_list[0][0]
        aabb_treenode = [bb_min.x, bb_min.y, bb_min.z, bb_max.x, bb_max.y, bb_max.z, linked_face_idx]
        aabb_tree.append(aabb_treenode)
    else:
        # This is a node in the tree
        linked_face_idx = -1 # -1 indicates nodes
        aabb_treenode = [bb_min.x, bb_min.y, bb_min.z, bb_max.x, bb_max.y, bb_max.z, linked_face_idx]
        aabb_tree.append(aabb_treenode)

        # Size of bounding box
        bb_size = bb_max - bb_min

        # Longest axis of bounding box
        split_axis = 0 # x
        if (bb_size.y > bb_size.x):
            split_axis = 1 # y
        if (bb_size.z > bb_size.y):
            split_axis = 2 # z

        # Change axis in case points are coplanar with
        # the split plane
        change_axis = True
        for face in face_list:
            face_centroid = face[2]
            change_axis = change_axis and (face_centroid[split_axis] == bb_avgcentroid[split_axis])

        if (change_axis):
            split_axis += 1
            if (split_axis >= 3):
                split_axis = 0

        # Put items on the left- and rightside of the splitplane
        # into sperate lists
        face_list_left  = []
        face_list_right = []
        found_split     = False
        tested_axes     = 1
        while not found_split:
            # Sort faces by side
            face_list_left  = []
            face_list_right = []
            leftside        = True
            for face in face_list:
                face_centroid = face[2]

                leftside = (face_centroid[split_axis] < bb_avgcentroid[split_axis])
                if leftside:
                    face_list_left.append(face)
                else:
                    face_list_right.append(face)

            # Try to prevent tree degeneration
            if (face_list_left) and (face_list_right):
                # Neither list is empty, this split will do just fine
                found_split = True
            else:
                # At least one of the list is empty
                # Try another axis to prevent degeneration
                tested_axes += 1

                split_axis  += 1
                if (split_axis >= 3):
                    split_axis = 0
                if (tested_axes >= 3):
                    # We have tried all axes, but
                    # the tree degenerates with each of them
                    # Just take the degenerate one
                    print("WARNING: Error generating aabb. Split problem.")
                    aabb_tree = []
                    return

        generate_tree(aabb_tree, face_list_left, rlevel+1)
        generate_tree(aabb_tree, face_list_right, rlevel+1)
