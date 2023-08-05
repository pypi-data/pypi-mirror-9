from efl.evas cimport Eina_Bool, Evas_Object, Evas_Smart_Cb, Eina_List

cdef extern from "Elementary.h":

    ctypedef struct Elm_Object_Item

    ctypedef Evas_Object    *(*Elm_Tooltip_Content_Cb)      (void *data, Evas_Object *obj, Evas_Object *tooltip)
    ctypedef Evas_Object    *(*Elm_Tooltip_Item_Content_Cb) (void *data, Evas_Object *obj, Evas_Object *tooltip, void *item)

    Evas_Object *   elm_object_item_widget_get(const Elm_Object_Item *it)
    void            elm_object_item_part_content_set(Elm_Object_Item *it, const char *part, Evas_Object* content)
    void            elm_object_item_content_set(Elm_Object_Item *it, Evas_Object* content)
    Evas_Object *   elm_object_item_part_content_get(const Elm_Object_Item *it, const char *part)
    Evas_Object *   elm_object_item_content_get(const Elm_Object_Item *it)
    Evas_Object *   elm_object_item_part_content_unset(Elm_Object_Item *it, const char *part)
    Evas_Object *   elm_object_item_content_unset(Elm_Object_Item *it)
    void            elm_object_item_part_text_set(Elm_Object_Item *item, const char *part, const char *label)
    void            elm_object_item_text_set(Elm_Object_Item *item, const char *label)
    const char *    elm_object_item_part_text_get(const Elm_Object_Item *item, const char *part)
    const char *    elm_object_item_text_get(const Elm_Object_Item *item)
    void            elm_object_item_domain_translatable_part_text_set(Elm_Object_Item *it, const char *part, const char *domain, const char *text)
    const char *    elm_object_item_translatable_part_text_get(const Elm_Object_Item *it, const char *part)
    void            elm_object_item_domain_part_text_translatable_set(Elm_Object_Item *it, const char *part, const char *domain, Eina_Bool translatable)

    #TODO: void            elm_object_item_access_info_set(Elm_Object_Item *it, const char *txt)
    void *          elm_object_item_data_get(const Elm_Object_Item *item)
    void            elm_object_item_data_set(Elm_Object_Item *item, void *data)
    void            elm_object_item_signal_emit(Elm_Object_Item *it, const char *emission, const char *source)
    void            elm_object_item_disabled_set(Elm_Object_Item *it, Eina_Bool disabled)
    Eina_Bool       elm_object_item_disabled_get(const Elm_Object_Item *it)
    void            elm_object_item_del_cb_set(Elm_Object_Item *it, Evas_Smart_Cb del_cb)
    void            elm_object_item_del(Elm_Object_Item *item)
    void            elm_object_item_tooltip_text_set(Elm_Object_Item *it, const char *text)
    Eina_Bool       elm_object_item_tooltip_window_mode_set(Elm_Object_Item *it, Eina_Bool disable)
    Eina_Bool       elm_object_item_tooltip_window_mode_get(const Elm_Object_Item *it)
    void            elm_object_item_tooltip_content_cb_set(Elm_Object_Item *it, Elm_Tooltip_Item_Content_Cb func, void *data, Evas_Smart_Cb del_cb)
    void            elm_object_item_tooltip_unset(Elm_Object_Item *it)
    void            elm_object_item_tooltip_style_set(Elm_Object_Item *it, const char *style)
    const char *    elm_object_item_tooltip_style_get(const Elm_Object_Item *it)
    void            elm_object_item_cursor_set(Elm_Object_Item *it, const char *cursor)
    const char *    elm_object_item_cursor_get(const Elm_Object_Item *it)
    void            elm_object_item_cursor_unset(Elm_Object_Item *it)
    void            elm_object_item_cursor_style_set(Elm_Object_Item *it, const char *style)
    const char *    elm_object_item_cursor_style_get(const Elm_Object_Item *it)
    void            elm_object_item_cursor_engine_only_set(Elm_Object_Item *it, Eina_Bool engine_only)
    Eina_Bool       elm_object_item_cursor_engine_only_get(const Elm_Object_Item *it)
    void            elm_object_item_focus_set(Elm_Object_Item *it, Eina_Bool focused)
    Eina_Bool       elm_object_item_focus_get(const Elm_Object_Item *it)


    #TODO: Evas_Object *   elm_object_item_access_register(Elm_Object_Item *item)
    #TODO: void            elm_object_item_access_unregister(Elm_Object_Item *item)
    #TODO: Evas_Object *   elm_object_item_access_object_get(const Elm_Object_Item *item)
    #TODO: void            elm_object_item_access_order_set(Elm_Object_Item *item, Eina_List *objs)
    #TODO: const Eina_List *elm_object_item_access_order_get(const Elm_Object_Item *item)
    #TODO: void            elm_object_item_access_order_unset(Elm_Object_Item *item)

    Evas_Object *   elm_object_item_track(Elm_Object_Item *it)
    void            elm_object_item_untrack(Elm_Object_Item *it)
    int             elm_object_item_track_get(const Elm_Object_Item *it)
    void            elm_object_item_style_set(Elm_Object_Item *it, const char *part)
    const char *    elm_object_item_style_get(Elm_Object_Item *it)



cdef _object_item_to_python(Elm_Object_Item *it)
cdef Elm_Object_Item * _object_item_from_python(ObjectItem item) except NULL
cdef _object_item_list_to_python(const Eina_List *lst)
cdef void _object_item_del_cb(void *data, Evas_Object *o, void *event_info) with gil
cdef void _object_item_callback(void *data, Evas_Object *obj, void *event_info) with gil
cdef void _object_item_callback2(void *data, Evas_Object *obj, void *event_info) with gil

cdef class ObjectItem(object):
    cdef:
        Elm_Object_Item *item
        object cb_func
        object cb_data
        tuple args
        dict kwargs
        readonly dict data
        int _set_obj(self, Elm_Object_Item *item) except 0

    cdef int _set_properties_from_keyword_args(self, dict kwargs) except 0
