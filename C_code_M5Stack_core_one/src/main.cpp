#include <Arduino.h>
#include <ArduinoJson.h>
#include "M5Unified.h"
#include "main.h"
#include <lvgl.h>
#include <esp_timer.h>

#include "cpu_img.h"
#include "code_img.h"
#include "chart.h"  

uint8_t min_pwm_value = 1;
uint8_t pwm_value = min_pwm_value;
uint8_t max_pwm_value = 100;

uint8_t control_mode_pwm = 0;

double cpu_load_percent = 0;
double memory_load_percent = 0;
double energy_cpu_wh = 0;

String class_name;
String method_name;
int cyclomatic_complexity = 0;
int pwm_value_cyclo_complex_thermal = 0;
int pwm_value_cyclo_complex_erm = 0;


bool use_serial_heatpad = true;

constexpr int32_t HOR_RES = 320;
constexpr int32_t VER_RES = 240;

lv_display_t *display;

lv_obj_t * btn_mode;
lv_obj_t * btn_plus;
lv_obj_t * btn_minus;
lv_obj_t * label_cpu;
lv_obj_t * label_pwm;
lv_obj_t * label_energy_wh;
lv_obj_t * label_energy_wh_value;

bool mode3_active = false;
lv_obj_t * label_class;
lv_obj_t * label_method;
lv_obj_t * label_cyclo_complexity;
lv_obj_t * img_obj;  // garder référence à l'image
static lv_obj_t * col;

// Buttons
bool buttonAPressed = false;
bool buttonBPressed = false;
bool buttonCPressed = false;

unsigned long lastPressTime = 0;
const uint8_t debounceDelay = 50;


void my_display_flush(lv_display_t *disp, const lv_area_t *area, uint8_t *px_map)
{
    uint32_t w = (area->x2 - area->x1 + 1);
    uint32_t h = (area->y2 - area->y1 + 1);

    lv_draw_sw_rgb565_swap(px_map, w * h);
    M5.Display.pushImageDMA<uint16_t>(area->x1, area->y1, w, h, (uint16_t *)px_map);

    lv_disp_flush_ready(disp);
}

uint32_t my_tick_function()
{
    return (esp_timer_get_time() / 1000LL);
}


void create_ui()
{
    chart_init(lv_screen_active());

    LV_IMAGE_DECLARE(cpu_img);
    img_obj = lv_img_create(lv_screen_active());
    lv_img_set_src(img_obj, &cpu_img);
    lv_obj_align(img_obj, LV_ALIGN_LEFT_MID, 25, -40);

    label_cpu = lv_label_create(lv_screen_active());
    label_pwm = lv_label_create(lv_screen_active());
    label_energy_wh = lv_label_create(lv_screen_active());
    label_energy_wh_value = lv_label_create(lv_screen_active());

    lv_label_set_text(label_cpu, "CPU: ---%");
    lv_obj_align(label_cpu, LV_ALIGN_LEFT_MID, 15, 10);

    lv_label_set_text(label_pwm, "PWM: ---");
    lv_obj_align(label_pwm, LV_ALIGN_LEFT_MID, 15, 30);

    lv_label_set_text(label_energy_wh, "CPU Energy:");
    lv_obj_align(label_energy_wh, LV_ALIGN_LEFT_MID, 15, 50);

    lv_label_set_text(label_energy_wh_value, "---Wh");
    lv_obj_align(label_energy_wh_value, LV_ALIGN_LEFT_MID, 15, 70);
}

/*====================*/
// Banner
/*====================*/
void create_top_banner(void){
    lv_obj_t * banner = lv_obj_create(lv_screen_active());
    lv_obj_set_size(banner, HOR_RES, 30);
    lv_obj_align(banner, LV_ALIGN_TOP_MID, 0, 0);

    // Style bannière
    lv_obj_set_style_bg_color(banner, lv_palette_main(LV_PALETTE_BLUE), 0);
    lv_obj_set_style_bg_opa(banner, LV_OPA_COVER, 0);
    lv_obj_set_style_border_width(banner, 0, 0);
    lv_obj_set_style_radius(banner, 0, 0);
    lv_obj_set_style_pad_all(banner, 0, 0);
    lv_obj_clear_flag(banner, LV_OBJ_FLAG_SCROLLABLE);

    // Texte PHASE centré
    lv_obj_t * label_banner = lv_label_create(banner);
    lv_label_set_text(label_banner, "PHASE");
    lv_obj_set_style_text_color(label_banner, lv_color_white(), 0);
    lv_obj_set_style_text_font(label_banner, &lv_font_montserrat_14, 0);
    lv_obj_center(label_banner);
}

/*====================*/
/*   BUTTONS          */
/*====================*/
void create_bottom_buttons(void)
{
    btn_mode = lv_button_create(lv_screen_active());
    lv_obj_align(btn_mode, LV_ALIGN_BOTTOM_MID, 0, -5);
    lv_obj_set_size(btn_mode, 100, 35);

    btn_mode = lv_button_create(lv_screen_active());
    lv_obj_align(btn_mode, LV_ALIGN_BOTTOM_MID, 0, -5);
    lv_obj_set_size(btn_mode, 100, 35);

    lv_obj_t * label_mode = lv_label_create(btn_mode);
    lv_label_set_text_fmt(label_mode, "Mode: %d", control_mode_pwm);
    lv_obj_center(label_mode);

    btn_minus = lv_button_create(lv_screen_active());
    lv_obj_align(btn_minus, LV_ALIGN_BOTTOM_LEFT, 40, -5);
    lv_obj_set_size(btn_minus, 50, 35);

    lv_obj_t * label_minus = lv_label_create(btn_minus);
    lv_label_set_text(label_minus, "-");
    lv_obj_set_style_text_font(label_minus, &lv_font_montserrat_24, 0);
    lv_obj_center(label_minus);

    btn_plus = lv_button_create(lv_screen_active());
    lv_obj_align(btn_plus, LV_ALIGN_BOTTOM_RIGHT, -40, -5);
    lv_obj_set_size(btn_plus, 50, 35);

    lv_obj_t * label_plus = lv_label_create(btn_plus);
    lv_label_set_text(label_plus, "+");
    lv_obj_set_style_text_font(label_plus, &lv_font_montserrat_24, 0);
    lv_obj_center(label_plus);
}

//timer
#include <esp_timer.h>
const int pin = 5;
bool state = false;
esp_timer_handle_t timer;

void toggle_pwm(void *arg) {
  state = !state;

  if (state) {
    analogWrite(pin, 40);
  } else {
    analogWrite(pin, 0);
  }
}

void setup()
{
    M5.begin();

  /*const esp_timer_create_args_t timer_args = {
    .callback = &toggle_pwm,
    .arg = NULL,
    .dispatch_method = ESP_TIMER_TASK,
    .name = "pwm_timer"
  };

  esp_timer_create(&timer_args, &timer);
  esp_timer_start_periodic(timer, 500000); // 100 ms*/


    lv_init();
    lv_tick_set_cb(my_tick_function);

    display = lv_display_create(HOR_RES, VER_RES);
    lv_display_set_flush_cb(display, my_display_flush);

    static lv_color_t buf1[HOR_RES * 30];
    lv_display_set_buffers(display, buf1, nullptr, sizeof(buf1), LV_DISPLAY_RENDER_MODE_PARTIAL);

    Serial.begin(115200);

    pinMode(PWM_PIN_PAD, OUTPUT);
    pinMode(5, OUTPUT);

    create_top_banner();
    create_ui();           
    create_bottom_buttons();
}

uint8_t linearization_pwm_cpu_load(uint8_t max_val_pwm, uint8_t pwm_threshold_min, double cpu_value_to_normalize){
    return pwm_threshold_min + (cpu_value_to_normalize/100.0) * (max_val_pwm- pwm_threshold_min);
}

uint8_t log_pwm_cpu_load(uint8_t max_val_pwm, uint8_t pwm_threshold_min, double cpu_value_to_normalize)
{

    double x = cpu_value_to_normalize / 100.0;

    // Facteur logarithmique (plus grand = plus doux au début)
    const double k = 9.0;

    // Loi logarithmique normalisée
    double y = log(1.0 + k * x) / log(1.0 + k);

    // Mise à l'échelle PWM
    double pwm = pwm_threshold_min + y * (max_val_pwm - pwm_threshold_min);

    return (uint8_t)(pwm + 0.5); // arrondi
}

void enter_mode_cyclo_complexity(void)
{
    if(mode3_active) return;
    mode3_active = true;

    // Cacher chart et image
    chart_set_visible(false);
    lv_obj_add_flag(img_obj, LV_OBJ_FLAG_HIDDEN);

    // Cacher labels mode 0
    lv_obj_add_flag(label_cpu,            LV_OBJ_FLAG_HIDDEN);
    //lv_obj_add_flag(label_pwm,            LV_OBJ_FLAG_HIDDEN);
    //lv_obj_add_flag(label_energy_wh,      LV_OBJ_FLAG_HIDDEN);
    //lv_obj_add_flag(label_energy_wh_value,LV_OBJ_FLAG_HIDDEN);

    LV_IMAGE_DECLARE(code_img);
    lv_img_set_src(img_obj, &code_img);
    lv_obj_remove_flag(img_obj, LV_OBJ_FLAG_HIDDEN);

    // Conteneur colonne droite — évite d'écraser l'image à gauche
    col = lv_obj_create(lv_screen_active());
    lv_obj_set_size(col, 190, 160);                        // largeur limitée côté droit
    lv_obj_align(col, LV_ALIGN_RIGHT_MID, -15, -10);
    // Fond carte
    lv_obj_set_style_bg_color(col, lv_color_white(), 0);
    lv_obj_set_style_bg_opa(col, LV_OPA_90, 0);
    lv_obj_set_style_radius(col, 12, 0);

    // Bordure fine
    lv_obj_set_style_border_color(col, lv_palette_lighten(LV_PALETTE_GREY, 2), 0);
    lv_obj_set_style_border_width(col, 1, 0);
    lv_obj_set_style_border_opa(col, LV_OPA_50, 0);

    // Ombre
    lv_obj_set_style_shadow_color(col, lv_color_black(), 0);
    lv_obj_set_style_shadow_width(col, 20, 0);
    lv_obj_set_style_shadow_opa(col, LV_OPA_30, 0);
    lv_obj_set_style_shadow_offset_x(col, 4, 0);
    lv_obj_set_style_shadow_offset_y(col, 4, 0);

    // Padding intérieur
    lv_obj_set_style_pad_all(col, 8, 0);
    lv_obj_set_flex_flow(col, LV_FLEX_FLOW_COLUMN);        // empilage vertical auto
    lv_obj_set_flex_align(col,
        LV_FLEX_ALIGN_START,
        LV_FLEX_ALIGN_START,
        LV_FLEX_ALIGN_START);
    lv_obj_clear_flag(col, LV_OBJ_FLAG_SCROLLABLE);

    label_class = lv_label_create(col);
    lv_label_set_text(label_class, "Class:");
    lv_label_set_long_mode(label_class, LV_LABEL_LONG_WRAP); 
    lv_obj_set_width(label_class, 152);                       

    label_method = lv_label_create(col);
    lv_label_set_text(label_method, "Method: ");
    lv_label_set_long_mode(label_method, LV_LABEL_LONG_WRAP);
    lv_obj_set_width(label_method, 152);

    label_cyclo_complexity = lv_label_create(col);
    lv_label_set_text(label_cyclo_complexity, "Cyclomatic Complexity:");
    lv_label_set_long_mode(label_cyclo_complexity, LV_LABEL_LONG_WRAP);
    lv_obj_set_width(label_cyclo_complexity, 152);
}

void exit_mode_cyclo_complexity(void)
{
    if(!mode3_active) return;
    mode3_active = false;

    // Supprimer le conteneur — supprime aussi label_class/2/3 qui sont ses enfants
    if(col){ 
        lv_obj_delete(col); 
        col = NULL; 
    }
    label_class = NULL;
    label_method = NULL;
    label_cyclo_complexity = NULL;

    // Restaurer chart et image
    chart_set_visible(true);
    LV_IMAGE_DECLARE(cpu_img);
    lv_img_set_src(img_obj, &cpu_img);
    lv_obj_remove_flag(img_obj, LV_OBJ_FLAG_HIDDEN);

    // Restaurer labels mode 0
    lv_obj_remove_flag(label_cpu,            LV_OBJ_FLAG_HIDDEN);
    lv_obj_remove_flag(label_pwm,            LV_OBJ_FLAG_HIDDEN);
    lv_obj_remove_flag(label_energy_wh,      LV_OBJ_FLAG_HIDDEN);
    lv_obj_remove_flag(label_energy_wh_value,LV_OBJ_FLAG_HIDDEN);
}

struct Mode {
    void (*on_enter)();
    void (*on_exit)();
    void (*on_loop)();
};


void handle_mode0() {
    if (Serial.available()){
        String json_string = Serial.readStringUntil('\n');
        json_string.trim();

        JsonDocument json_doc;
        deserializeJson(json_doc, json_string);
        if(json_doc["cpu-load"].is<float>()){
            cpu_load_percent    = json_doc["cpu-load"].as<float>();
            memory_load_percent = json_doc["memory-load"].as<double>();
            energy_cpu_wh       = json_doc["cpu-energy"].as<float>();

            pwm_value = log_pwm_cpu_load(max_pwm_value, min_pwm_value, cpu_load_percent);
            analogWrite(PWM_PIN_PAD, pwm_value);

            lv_label_set_text_fmt(label_cpu,              "CPU: %d%%", (int)cpu_load_percent);
            lv_label_set_text_fmt(label_pwm,              "PWM: %d",   pwm_value);
            lv_label_set_text_fmt(label_energy_wh_value,  "%.2f Wh",   energy_cpu_wh);
            chart_add_value((uint8_t)cpu_load_percent);
        }
    }
}

void handle_mode1() {
    if (M5.BtnA.isPressed() && pwm_value > min_pwm_value) {
        lv_obj_add_state(btn_minus, LV_STATE_PRESSED);
        pwm_value--;
        lv_label_set_text_fmt(label_pwm, "PWM: %d", pwm_value);
    }
    if (M5.BtnC.isPressed() && pwm_value < max_pwm_value) {
        lv_obj_add_state(btn_plus, LV_STATE_PRESSED);
        pwm_value++;
        lv_label_set_text_fmt(label_pwm, "PWM: %d", pwm_value);
    }
    analogWrite(PWM_PIN_PAD, pwm_value);
}

void enter_mode2() {
    pwm_value = 0;
    analogWrite(PWM_PIN_PAD, 0);
}

void handle_mode3() { /* lecture passive, UI déjà en place via on_enter */
    if(Serial.available())
    {
        String json_string = Serial.readStringUntil('\n');
        json_string.trim(); // supprimer \r éventuels

        JsonDocument json_doc;
        DeserializationError erreur = deserializeJson(json_doc, json_string);
        if(json_doc["class-name"].is<String>()){
            class_name           = json_doc["class-name"].as<String>();
            method_name          = json_doc["method-name"].as<String>();
            cyclomatic_complexity = json_doc["cyclomatic-complexity"].as<int>();
            pwm_value_cyclo_complex_thermal = json_doc["pwm-value-thermal"].as<int>();
            pwm_value_cyclo_complex_erm = json_doc["pwm-value-thermal"].as<int>();

            lv_label_set_text_fmt(label_class,            "Class: %s", class_name.c_str());
            lv_label_set_text_fmt(label_method,           "Method: %s", method_name.c_str());
            lv_label_set_text_fmt(label_cyclo_complexity, "Cyclomatic Complexity:% d", cyclomatic_complexity);
        }
    }
}

/*====================*/
/*   TABLE DES MODES  */
/*====================*/

const Mode modes[] = {
    { nullptr,                      nullptr,                       handle_mode0 },
    { nullptr,                      nullptr,                       handle_mode1 },
    { enter_mode2,                  nullptr,                       nullptr      },
    { enter_mode_cyclo_complexity,  exit_mode_cyclo_complexity,    handle_mode3 },
};

//taille du tableau / taille d'un mode
constexpr uint8_t MODE_COUNT = sizeof(modes) / sizeof(modes[0]);


void switch_mode(uint8_t next) {
    if (modes[control_mode_pwm].on_exit)
        modes[control_mode_pwm].on_exit();

    control_mode_pwm = next % MODE_COUNT;

    if (modes[control_mode_pwm].on_enter)
        modes[control_mode_pwm].on_enter();

    lv_label_set_text_fmt(
        lv_obj_get_child(btn_mode, 0),
        "Mode: %d",
        control_mode_pwm
    );
}

void loop() {
    M5.update();
    lv_timer_handler();

    // Dispatcher
    if (modes[control_mode_pwm].on_loop)
        modes[control_mode_pwm].on_loop();

    if (M5.BtnB.wasPressed() && !buttonBPressed) {
        if (millis() - lastPressTime > debounceDelay) {
            switch_mode(control_mode_pwm + 1);
            buttonBPressed = true;
            lastPressTime  = millis();
        }
    }

    // Release btn
    if(M5.BtnA.wasReleased()){ 
        buttonAPressed = false; 
        lv_obj_clear_state(btn_minus, LV_STATE_PRESSED); 
    }
    if (M5.BtnB.wasReleased()){
        buttonBPressed = false;
        lv_obj_clear_state(btn_mode,  LV_STATE_PRESSED); 
    }
    if(M5.BtnC.wasReleased()){
        buttonCPressed = false; 
        lv_obj_clear_state(btn_plus,  LV_STATE_PRESSED); 
    }
}