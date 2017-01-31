class FaceProcessor:
    def __init__(self):
        pass

    def process(self, image: bytes, metadata=None):
        normalized = normalize(image)
        path_normalized = save_image(normalized)
        ref_source = save_source_image_metadata(path_normalized, metadata)

        faces = detect_faces(normalized)
        for face in faces:
            path_face = save_image(face.get_image())
            ref_face = save_face_metadata(path_face, face.get_metadata(), ref_source)
            face_descriptor = calculate_descriptor_for_face(path_face)
            save_descriptor(face_descriptor, ref_face)
