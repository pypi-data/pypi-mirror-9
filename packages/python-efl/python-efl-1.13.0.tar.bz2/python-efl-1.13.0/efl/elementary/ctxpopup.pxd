from efl.evas cimport Eina_Bool, Eina_List, Evas_Object, Evas_Smart_Cb
from object_item cimport Elm_Object_Item


cdef extern from "Elementary.h":

    cpdef enum Elm_Ctxpopup_Direction:
        ELM_CTXPOPUP_DIRECTION_DOWN
        ELM_CTXPOPUP_DIRECTION_RIGHT
        ELM_CTXPOPUP_DIRECTION_LEFT
        ELM_CTXPOPUP_DIRECTION_UP
        ELM_CTXPOPUP_DIRECTION_UNKNOWN
    ctypedef enum Elm_Ctxpopup_Direction:
        pass


    Evas_Object             *elm_ctxpopup_add(Evas_Object *parent)
    void                     elm_ctxpopup_hover_parent_set(Evas_Object *obj, Evas_Object *parent)
    Evas_Object             *elm_ctxpopup_hover_parent_get(const Evas_Object *obj)
    void                     elm_ctxpopup_clear(Evas_Object *obj)
    void                     elm_ctxpopup_horizontal_set(Evas_Object *obj, Eina_Bool horizontal)
    Eina_Bool                elm_ctxpopup_horizontal_get(const Evas_Object *obj)
    Elm_Object_Item         *elm_ctxpopup_item_append(Evas_Object *obj, const char *label, Evas_Object *icon, Evas_Smart_Cb func, void *data)
    Elm_Object_Item         *elm_ctxpopup_item_prepend(Evas_Object *obj, const char *label, Evas_Object *icon, Evas_Smart_Cb func, void *data)
    void                     elm_ctxpopup_direction_priority_set(Evas_Object *obj, Elm_Ctxpopup_Direction first, Elm_Ctxpopup_Direction second, Elm_Ctxpopup_Direction third, Elm_Ctxpopup_Direction fourth)
    void                     elm_ctxpopup_direction_priority_get(const Evas_Object *obj, Elm_Ctxpopup_Direction *first, Elm_Ctxpopup_Direction *second, Elm_Ctxpopup_Direction *third, Elm_Ctxpopup_Direction *fourth)
    Elm_Ctxpopup_Direction   elm_ctxpopup_direction_get(const Evas_Object *obj)
    void                     elm_ctxpopup_dismiss(Evas_Object *obj)
    void                     elm_ctxpopup_auto_hide_disabled_set(Evas_Object *obj, Eina_Bool disabled)
    Eina_Bool                elm_ctxpopup_auto_hide_disabled_get(const Evas_Object *obj)
    Eina_List               *elm_ctxpopup_items_get(const Evas_Object *obj)
    Elm_Object_Item         *elm_ctxpopup_first_item_get(const Evas_Object *obj)
    Elm_Object_Item         *elm_ctxpopup_last_item_get(const Evas_Object *obj)
    Elm_Object_Item         *elm_ctxpopup_item_prev_get(const Elm_Object_Item *it)
    Elm_Object_Item         *elm_ctxpopup_item_next_get(const Elm_Object_Item *it)

