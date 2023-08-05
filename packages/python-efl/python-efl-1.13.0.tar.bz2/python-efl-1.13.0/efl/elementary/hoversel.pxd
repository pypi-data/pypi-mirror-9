from efl.evas cimport Eina_Bool, Eina_List, Evas_Object, Evas_Smart_Cb
from object_item cimport Elm_Object_Item


cdef extern from "Elementary.h":

    cpdef enum Elm_Icon_Type:
        ELM_ICON_NONE
        ELM_ICON_FILE
        ELM_ICON_STANDARD
    ctypedef enum Elm_Icon_Type:
        pass

    Evas_Object             *elm_hoversel_add(Evas_Object *parent)
    void                     elm_hoversel_horizontal_set(Evas_Object *obj, Eina_Bool horizontal)
    Eina_Bool                elm_hoversel_horizontal_get(const Evas_Object *obj)
    void                     elm_hoversel_hover_parent_set(Evas_Object *obj, Evas_Object *parent)
    Evas_Object             *elm_hoversel_hover_parent_get(const Evas_Object *obj)
    void                     elm_hoversel_hover_begin(Evas_Object *obj)
    void                     elm_hoversel_hover_end(Evas_Object *obj)
    Eina_Bool                elm_hoversel_expanded_get(const Evas_Object *obj)
    void                     elm_hoversel_clear(Evas_Object *obj)
    Eina_List               *elm_hoversel_items_get(const Evas_Object *obj)
    Elm_Object_Item         *elm_hoversel_item_add(Evas_Object *obj, const char *label, const char *icon_file, Elm_Icon_Type icon_type, Evas_Smart_Cb func, void *data)
    void                     elm_hoversel_item_icon_set(Elm_Object_Item *it, const char *icon_file, const char *icon_group, Elm_Icon_Type icon_type)
    void                     elm_hoversel_item_icon_get(const Elm_Object_Item *it, const char **icon_file, const char **icon_group, Elm_Icon_Type *icon_type)
