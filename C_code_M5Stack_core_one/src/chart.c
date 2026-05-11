#include "chart.h"

#define MAX_VALUES_CPU_LOAD 130

static lv_obj_t * chart;
static lv_chart_series_t * ser;
static uint8_t values[MAX_VALUES_CPU_LOAD] = {0};
static uint8_t index_val = 0;

static void add_faded_area(lv_event_t * e)
{
    lv_draw_task_t * draw_task = lv_event_get_draw_task(e);
    if(!draw_task) return;
    if(lv_draw_task_get_type(draw_task) != LV_DRAW_TASK_TYPE_LINE) return;

    void * raw_dsc = lv_draw_task_get_draw_dsc(draw_task);
    if(!raw_dsc) return;

    lv_draw_dsc_base_t * base_dsc = (lv_draw_dsc_base_t *)raw_dsc;
    if(base_dsc->part != LV_PART_ITEMS) return;

    lv_draw_line_dsc_t * line_dsc = (lv_draw_line_dsc_t *)raw_dsc;

    /* Vérifier que les coordonnées sont sensées */
    if(line_dsc->p1.x < 0 || line_dsc->p2.x < 0) return;
    if(line_dsc->p1.y < 0 || line_dsc->p2.y < 0) return;

    lv_obj_t * obj = lv_event_get_target_obj(e);
    lv_area_t coords;
    lv_obj_get_coords(obj, &coords);

    int32_t full_h = lv_obj_get_height(obj);
    if(full_h <= 0) return;  /* éviter division par zéro */

    int32_t f1 = (LV_MIN(line_dsc->p1.y, line_dsc->p2.y) - coords.y1) * 255 / full_h;
    int32_t f2 = (LV_MAX(line_dsc->p1.y, line_dsc->p2.y) - coords.y1) * 255 / full_h;
    f1 = LV_CLAMP(0, f1, 255);
    f2 = LV_CLAMP(0, f2, 255);

    const lv_chart_series_t * ser_local = lv_chart_get_series_next(obj, NULL);
    if(!ser_local) return;
    lv_color_t ser_color = lv_chart_get_series_color(obj, ser_local);

    /* Triangle */
    lv_draw_triangle_dsc_t tri;
    lv_draw_triangle_dsc_init(&tri);
    tri.p[0] = line_dsc->p1;
    tri.p[1] = line_dsc->p2;
    tri.p[2].x = line_dsc->p1.y < line_dsc->p2.y ? line_dsc->p1.x : line_dsc->p2.x;
    tri.p[2].y = LV_MAX(line_dsc->p1.y, line_dsc->p2.y);
    tri.grad.dir = LV_GRAD_DIR_VER;
    tri.grad.stops[0].color = ser_color;
    tri.grad.stops[0].opa   = 255 - f1;
    tri.grad.stops[1].color = ser_color;
    tri.grad.stops[1].opa   = 255 - f2;
    lv_draw_triangle(base_dsc->layer, &tri);

    /* Rectangle */
    lv_draw_rect_dsc_t rect;
    lv_draw_rect_dsc_init(&rect);
    rect.bg_grad.dir = LV_GRAD_DIR_VER;
    rect.bg_grad.stops[0].color = ser_color;
    rect.bg_grad.stops[0].opa   = 255 - f2;
    rect.bg_grad.stops[1].color = ser_color;
    rect.bg_grad.stops[1].opa   = 0;
    lv_area_t area = {
        .x1 = (int32_t)LV_MIN(line_dsc->p1.x, line_dsc->p2.x),
        .x2 = (int32_t)LV_MAX(line_dsc->p1.x, line_dsc->p2.x) - 1,
        .y1 = LV_MAX(line_dsc->p1.y, line_dsc->p2.y),
        .y2 = coords.y2
    };
    lv_draw_rect(base_dsc->layer, &rect, &area);
}

static void draw_event_cb(lv_event_t * e)
{
    lv_draw_task_t * task = lv_event_get_draw_task(e);
    lv_draw_dsc_base_t * base = (lv_draw_dsc_base_t *)lv_draw_task_get_draw_dsc(task);

    if(base->part == LV_PART_ITEMS &&
       lv_draw_task_get_type(task) == LV_DRAW_TASK_TYPE_LINE)
    {
        add_faded_area(e);
    }
}

void chart_init(lv_obj_t * parent)
{
    chart = lv_chart_create(parent);
    lv_obj_set_size(chart, 200, 150);
    lv_obj_align(chart, LV_ALIGN_RIGHT_MID, -10, -5);
    lv_chart_set_type(chart, LV_CHART_TYPE_LINE);
    lv_chart_set_point_count(chart, MAX_VALUES_CPU_LOAD);
    lv_obj_set_style_line_width(chart, 1, LV_PART_ITEMS);

    ser = lv_chart_add_series(chart,
          lv_palette_main(LV_PALETTE_GREEN),
          LV_CHART_AXIS_PRIMARY_Y);

    // Ombre
    lv_obj_set_style_shadow_color(chart, lv_color_black(), 0);
    lv_obj_set_style_shadow_width(chart, 20, 0);
    lv_obj_set_style_shadow_opa(chart, LV_OPA_30, 0);
    lv_obj_set_style_shadow_offset_x(chart, 4, 0);
    lv_obj_set_style_shadow_offset_y(chart, 4, 0);

    lv_obj_add_event_cb(chart, draw_event_cb, LV_EVENT_DRAW_TASK_ADDED, NULL);
    lv_obj_add_flag(chart, LV_OBJ_FLAG_SEND_DRAW_TASK_EVENTS);
    
}

void chart_add_value(uint8_t value)
{
    values[index_val] = value;
    index_val = (index_val + 1) % MAX_VALUES_CPU_LOAD;
    lv_chart_set_next_value(chart, ser, value);
}

void chart_refresh(void)
{
    lv_chart_refresh(chart);
}

void chart_set_visible(bool visible)
{
    if(visible)
        lv_obj_remove_flag(chart, LV_OBJ_FLAG_HIDDEN);
    else
        lv_obj_add_flag(chart, LV_OBJ_FLAG_HIDDEN);
}