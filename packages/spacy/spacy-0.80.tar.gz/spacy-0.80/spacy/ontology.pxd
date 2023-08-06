cdef struct Entity:
    int id
    int type
    float prior


cdef class Ontology:
    cdef vector[Entity] entities
    cdef PreshMap forms
