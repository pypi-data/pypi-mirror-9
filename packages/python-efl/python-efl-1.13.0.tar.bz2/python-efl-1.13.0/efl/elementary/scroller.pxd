from efl.evas cimport Eina_Bool, Evas_Object, Evas_Coord
from object cimport Object


cdef extern from "Elementary.h":

    cpdef enum Elm_Scroller_Policy:
        ELM_SCROLLER_POLICY_AUTO
        ELM_SCROLLER_POLICY_ON
        ELM_SCROLLER_POLICY_OFF
    ctypedef enum Elm_Scroller_Policy:
        pass

    cpdef enum Elm_Scroller_Single_Direction:
        ELM_SCROLLER_SINGLE_DIRECTION_NONE
        ELM_SCROLLER_SINGLE_DIRECTION_SOFT
        ELM_SCROLLER_SINGLE_DIRECTION_HARD
        ELM_SCROLLER_SINGLE_DIRECTION_LAST
    ctypedef enum Elm_Scroller_Single_Direction:
        pass

    cpdef enum Elm_Scroller_Movement_Block:
        ELM_SCROLLER_MOVEMENT_NO_BLOCK
        ELM_SCROLLER_MOVEMENT_BLOCK_VERTICAL
        ELM_SCROLLER_MOVEMENT_BLOCK_HORIZONTAL
    ctypedef enum Elm_Scroller_Movement_Block:
        pass


    Evas_Object             *elm_scroller_add(Evas_Object *parent)
    void                     elm_scroller_custom_widget_base_theme_set(Evas_Object *obj, const char *widget, const char *base)
    void                     elm_scroller_content_min_limit(Evas_Object *obj, Eina_Bool w, Eina_Bool h)
    void                     elm_scroller_region_show(Evas_Object *obj, Evas_Coord x, Evas_Coord y, Evas_Coord w, Evas_Coord h)
    void                     elm_scroller_policy_set(Evas_Object *obj, Elm_Scroller_Policy policy_h, Elm_Scroller_Policy policy_v)
    void                     elm_scroller_policy_get(const Evas_Object *obj, Elm_Scroller_Policy *policy_h, Elm_Scroller_Policy *policy_v)
    void                     elm_scroller_single_direction_set(Evas_Object *obj, Elm_Scroller_Single_Direction single_dir)
    Elm_Scroller_Single_Direction elm_scroller_single_direction_get(const Evas_Object *obj)
    void                     elm_scroller_region_get(const Evas_Object *obj, Evas_Coord *x, Evas_Coord *y, Evas_Coord *w, Evas_Coord *h)
    void                     elm_scroller_child_size_get(const Evas_Object *obj, Evas_Coord *w, Evas_Coord *h)
    void                     elm_scroller_page_snap_set(Evas_Object *obj, Eina_Bool page_h_snap, Eina_Bool page_v_snap)
    void                     elm_scroller_page_snap_get(const Evas_Object *obj, Eina_Bool *page_h_snap, Eina_Bool *page_v_snap)
    void                     elm_scroller_bounce_set(Evas_Object *obj, Eina_Bool h_bounce, Eina_Bool v_bounce)
    void                     elm_scroller_bounce_get(const Evas_Object *obj, Eina_Bool *h_bounce, Eina_Bool *v_bounce)
    void                     elm_scroller_page_relative_set(Evas_Object *obj, double h_pagerel, double v_pagerel)
    void                     elm_scroller_page_relative_get(const Evas_Object *obj, double *h_pagerel, double *v_pagerel)
    void                     elm_scroller_page_size_set(Evas_Object *obj, Evas_Coord h_pagesize, Evas_Coord v_pagesize)
    void                     elm_scroller_page_size_get(const Evas_Object *obj, Evas_Coord *h_pagesize, Evas_Coord *v_pagesize)
    void                     elm_scroller_step_size_set(Evas_Object *obj, Evas_Coord x, Evas_Coord y)
    void                     elm_scroller_step_size_get(const Evas_Object *obj, Evas_Coord *x, Evas_Coord *y)
    void                     elm_scroller_page_scroll_limit_set(const Evas_Object *obj, Evas_Coord page_limit_h, Evas_Coord page_limit_v)
    void                     elm_scroller_page_scroll_limit_get(const Evas_Object *obj, Evas_Coord *page_limit_h, Evas_Coord *page_limit_v)
    void                     elm_scroller_current_page_get(const Evas_Object *obj, int *h_pagenumber, int *v_pagenumber)
    void                     elm_scroller_last_page_get(const Evas_Object *obj, int *h_pagenumber, int *v_pagenumber)
    void                     elm_scroller_page_show(Evas_Object *obj, int h_pagenumber, int v_pagenumber)
    void                     elm_scroller_page_bring_in(Evas_Object *obj, int h_pagenumber, int v_pagenumber)
    void                     elm_scroller_region_bring_in(Evas_Object *obj, Evas_Coord x, Evas_Coord y, Evas_Coord w, Evas_Coord h)
    void                     elm_scroller_propagate_events_set(Evas_Object *obj, Eina_Bool propagation)
    Eina_Bool                elm_scroller_propagate_events_get(const Evas_Object *obj)
    void                     elm_scroller_gravity_set(Evas_Object *obj, double x, double y)
    void                     elm_scroller_gravity_get(const Evas_Object *obj, double *x, double *y)
    void                     elm_scroller_movement_block_set(Evas_Object *obj, Elm_Scroller_Movement_Block block)
    Elm_Scroller_Movement_Block elm_scroller_movement_block_get(const Evas_Object *obj)

cdef class Scrollable(Object):
    pass
