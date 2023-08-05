from efl.evas cimport Eina_Bool, Evas_Object, Evas_Coord, Evas_Event_Flags


cdef extern from "Elementary.h":

    cpdef enum Elm_Gesture_State:
        ELM_GESTURE_STATE_UNDEFINED
        ELM_GESTURE_STATE_START
        ELM_GESTURE_STATE_MOVE
        ELM_GESTURE_STATE_END
        ELM_GESTURE_STATE_ABORT
    ctypedef enum Elm_Gesture_State:
        pass

    cpdef enum Elm_Gesture_Type:
        ELM_GESTURE_FIRST
        ELM_GESTURE_N_TAPS
        ELM_GESTURE_N_LONG_TAPS
        ELM_GESTURE_N_DOUBLE_TAPS
        ELM_GESTURE_N_TRIPLE_TAPS
        ELM_GESTURE_MOMENTUM
        ELM_GESTURE_N_LINES
        ELM_GESTURE_N_FLICKS
        ELM_GESTURE_ZOOM
        ELM_GESTURE_ROTATE
        ELM_GESTURE_LAST
    ctypedef enum Elm_Gesture_Type:
        pass


    ctypedef struct Elm_Gesture_Taps_Info:
        Evas_Coord   x, y
        unsigned int n
        unsigned int timestamp

    ctypedef struct Elm_Gesture_Momentum_Info:
        Evas_Coord   x1
        Evas_Coord   y1
        Evas_Coord   x2
        Evas_Coord   y2

        unsigned int tx
        unsigned int ty

        Evas_Coord   mx
        Evas_Coord   my

        unsigned int n

    ctypedef struct Elm_Gesture_Line_Info:
        Elm_Gesture_Momentum_Info momentum
        double                    angle

    ctypedef struct Elm_Gesture_Zoom_Info:
        Evas_Coord x, y
        Evas_Coord radius
        double     zoom
        double     momentum

    ctypedef struct Elm_Gesture_Rotate_Info:
        Evas_Coord x, y
        Evas_Coord radius
        double     base_angle
        double     angle
        double     momentum

    ctypedef Evas_Event_Flags (*Elm_Gesture_Event_Cb)(void *data, void *event_info)

    # Gesture layer
    void                     elm_gesture_layer_cb_set(Evas_Object *obj, Elm_Gesture_Type idx, Elm_Gesture_State cb_type, Elm_Gesture_Event_Cb cb, void *data)
    Eina_Bool                elm_gesture_layer_hold_events_get(const Evas_Object *obj)
    void                     elm_gesture_layer_hold_events_set(Evas_Object *obj, Eina_Bool hold_events)
    void                     elm_gesture_layer_zoom_step_set(Evas_Object *obj, double step)
    double                   elm_gesture_layer_zoom_step_get(const Evas_Object *obj)
    void                     elm_gesture_layer_rotate_step_set(Evas_Object *obj, double step)
    double                   elm_gesture_layer_rotate_step_get(const Evas_Object *obj)
    Eina_Bool                elm_gesture_layer_attach(Evas_Object *obj, Evas_Object *target)
    Evas_Object             *elm_gesture_layer_add(Evas_Object *parent)

    void elm_gesture_layer_line_min_length_set(Evas_Object *obj, int line_min_length)
    int elm_gesture_layer_line_min_length_get(const Evas_Object *obj)
    void elm_gesture_layer_zoom_distance_tolerance_set(Evas_Object *obj, Evas_Coord zoom_distance_tolerance)
    Evas_Coord elm_gesture_layer_zoom_distance_tolerance_get(const Evas_Object *obj)
    void elm_gesture_layer_line_distance_tolerance_set(Evas_Object *obj, Evas_Coord line_distance_tolerance)
    Evas_Coord elm_gesture_layer_line_distance_tolerance_get(const Evas_Object *obj)
    void elm_gesture_layer_line_angular_tolerance_set(Evas_Object *obj, double line_angular_tolerance)
    double elm_gesture_layer_line_angular_tolerance_get(const Evas_Object *obj)
    void elm_gesture_layer_zoom_wheel_factor_set(Evas_Object *obj, double zoom_wheel_factor)
    double elm_gesture_layer_zoom_wheel_factor_get(const Evas_Object *obj)
    void elm_gesture_layer_zoom_finger_factor_set(Evas_Object *obj, double zoom_finger_factor)
    double elm_gesture_layer_zoom_finger_factor_get(const Evas_Object *obj)
    void elm_gesture_layer_rotate_angular_tolerance_set(Evas_Object *obj, double rotate_angular_tolerance)
    double elm_gesture_layer_rotate_angular_tolerance_get(const Evas_Object *obj)
    void elm_gesture_layer_flick_time_limit_ms_set(Evas_Object *obj, unsigned int flick_time_limit_ms)
    unsigned int elm_gesture_layer_flick_time_limit_ms_get(const Evas_Object *obj)
    void elm_gesture_layer_long_tap_start_timeout_set(Evas_Object *obj, double long_tap_start_timeout)
    double elm_gesture_layer_long_tap_start_timeout_get(const Evas_Object *obj)
    void elm_gesture_layer_continues_enable_set(Evas_Object *obj, Eina_Bool continues_enable)
    Eina_Bool elm_gesture_layer_continues_enable_get(const Evas_Object *obj)
    void elm_gesture_layer_double_tap_timeout_set(Evas_Object *obj, double double_tap_timeout)
    double elm_gesture_layer_double_tap_timeout_get(const Evas_Object *obj)
    void elm_gesture_layer_tap_finger_size_set(Evas_Object *obj, Evas_Coord sz)
    Evas_Coord elm_gesture_layer_tap_finger_size_get(const Evas_Object *obj)
    # TODO: void elm_gesture_layer_tap_longpress_cb_add(Evas_Object *obj, Elm_Gesture_State state, Elm_Gesture_Event_Cb cb, void *data)
    # TODO: void elm_gesture_layer_tap_longpress_cb_del(Evas_Object *obj, Elm_Gesture_State state, Elm_Gesture_Event_Cb cb, void *data)
