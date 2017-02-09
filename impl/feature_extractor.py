from typing import List

from face_search.impl.descriptor import Descriptor
from face_search.impl.face import Face


def save_image(param):
    pass


def save_face_metadata(path_face, param):
    pass


def save_descriptor(face_descriptor, ref_face):
    pass


def calculate_descriptor_for_face(path_face):
    pass


class FeatureExtractor:
    def __init__(self):
        pass

    def process_faces(self, faces: List[Face]) -> List[Descriptor]:
        return [self.process_face(face) for face in faces]

    def process_face(self, face: Face) -> Descriptor:
        path_face = save_image(face.get_image())
        ref_face = save_face_metadata(path_face, face.get_metadata())
        face_descriptor = calculate_descriptor_for_face(path_face)
        save_descriptor(face_descriptor, ref_face)
        return face_descriptor
