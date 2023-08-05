from efl.evas cimport Evas_Object, Eina_List, Eina_Bool
from object_item cimport Elm_Object_Item


cdef extern from "Elementary.h":

    cpdef enum Elm_Colorselector_Mode:
        ELM_COLORSELECTOR_PALETTE
        ELM_COLORSELECTOR_COMPONENTS
        ELM_COLORSELECTOR_BOTH
    ctypedef enum Elm_Colorselector_Mode:
        pass


    Evas_Object *           elm_colorselector_add(Evas_Object *parent)
    void                    elm_colorselector_color_set(Evas_Object *obj, int r, int g, int b, int a)
    void                    elm_colorselector_color_get(const Evas_Object *obj, int *r, int *g, int *b, int *a)
    void                    elm_colorselector_mode_set(Evas_Object *obj, Elm_Colorselector_Mode mode)
    Elm_Colorselector_Mode  elm_colorselector_mode_get(const Evas_Object *obj)
    void                    elm_colorselector_palette_item_color_get(const Elm_Object_Item *it, int *r, int *g, int *b, int *a)
    void                    elm_colorselector_palette_item_color_set(Elm_Object_Item *it, int r, int g, int b, int a)
    Elm_Object_Item *       elm_colorselector_palette_color_add(Evas_Object *obj, int r, int g, int b, int a)
    void                    elm_colorselector_palette_clear(Evas_Object *obj)
    void                    elm_colorselector_palette_name_set(Evas_Object *obj, const char *palette_name)
    const char *            elm_colorselector_palette_name_get(const Evas_Object *obj)
    const Eina_List *       elm_colorselector_palette_items_get(const Evas_Object *obj)
    Eina_Bool               elm_colorselector_palette_item_selected_get(const Elm_Object_Item *it)
    void                    elm_colorselector_palette_item_selected_set(Elm_Object_Item *it, Eina_Bool selected)
    Elm_Object_Item *       elm_colorselector_palette_selected_item_get(const Evas_Object *obj)
