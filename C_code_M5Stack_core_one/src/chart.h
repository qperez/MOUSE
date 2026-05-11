#include <lvgl.h>

#ifdef __cplusplus
extern "C" {
#endif

void chart_init(lv_obj_t * parent);
void chart_add_value(uint8_t value);
void chart_refresh(void);
void chart_set_visible(bool visible);

#ifdef __cplusplus
}
#endif