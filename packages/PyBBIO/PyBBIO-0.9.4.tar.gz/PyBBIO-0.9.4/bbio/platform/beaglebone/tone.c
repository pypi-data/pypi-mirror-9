/*
  Extension('bbio.platform.beaglebone.tone',
            ['bbio/platform/beaglebone/tone.c',
             'bbio/platform/beaglebone/gpio.c'],
            include_dirs=['bbio/platform/util']),
*/

#include "Python.h"
#include "gpio.h"
#include <pthread.h>
#include <stdint.h>
#include <unistd.h>
#include <time.h>

typedef struct _thread_config {
  FILE *state_fd;
  char *gpio_pin;
  int gpio_num;
  float frequency;
  uint8_t update_flag;
  uint8_t kill_flag;
} thread_config;

static thread_config *_thread_configs[MAX_GPIO_NUM];
static pthread_t _thread_ids[MAX_GPIO_NUM];

static uint64_t time_since_epoch_us(void) {
  // based on http://stackoverflow.com/a/1861493/3856924
  struct timeval now;
  gettimeofday(&now, NULL);
  return  now.tv_usec + (uint64_t) now.tv_sec * 1000000;
}

static void *toneThread(void *args) {
  thread_config *config;
  char state_str[2];
  float period;
  uint32_t half_period_us, remainder_us, half_remainder_us;
  uint8_t state;
  uint64_t start_us, next_us, end_us, elapsed_us, now_us;
  //PyGILState_STATE gstate;
  //gstate = PyGILState_Ensure();
  // setup
  config = (thread_config *) args;
  //PyGILState_Release(gstate);
  state = 0;
  half_period_us = 100;
  while (!config->kill_flag) {
    //start_us = time_since_epoch_us();
    //next_us = start_us + half_period_us;
    //printf("start %llu us\n", start_us);
    //printf("next %llu us\n", next_us);
    if (config->update_flag) {
      //gstate = PyGILState_Ensure();
      period = 1.0 / config->frequency;
      half_period_us = (uint32_t) (1000000.0 * period / 2.0);
      config->update_flag = 0;
      //PyGILState_Release(gstate);
    }
    snprintf(state_str, 2, "%i", state^=1);
    fseek(config->state_fd, 0, SEEK_SET);    
    fprintf(config->state_fd, "%s", state_str);
    fflush(config->state_fd);
    
    usleep(half_period_us);
    continue;
    while (!(config->kill_flag || config->update_flag)) {
      now_us = time_since_epoch_us();
      //printf("now %llu us\n", now_us);
      if (now_us > next_us) break;
      remainder_us = (uint32_t) (next_us - now_us);
      //printf("remainder %u us\n", remainder_us);
      if (remainder_us < 100) break;
      half_remainder_us = remainder_us >> 2;
      //printf("half remainder %llu us\n", half_remainder_us);
      usleep(half_remainder_us);
    }
    /*
    end_us = time_since_epoch_us();
    elapsed_us = end_us - start_us;
    if (elapsed_us < half_period_us) {
      remainder_us = (uint32_t) (half_period_us - elapsed_us);
      //printf("start %llu us\n", start_us);
      //printf("end_us %llu us\n", end_us);
      //printf("elapsed_us %llu us\n", elapsed_us);
      //printf("remainder_us %u us\n", remainder_us);
      usleep(remainder_us);
    }
    */
  }
  return NULL;
} 

void cleanupToneConfig(int gpio_num) {
  PyGPIO_unlockStateFile(_thread_configs[gpio_num]->gpio_pin);
  free(_thread_configs[gpio_num]->gpio_pin);
  free(_thread_configs[gpio_num]);
  _thread_configs[gpio_num] = NULL;
}

void killToneThread(int gpio_num) {
  thread_config *config;
  int ret;
  config = _thread_configs[gpio_num];
  if (config) {
    config->kill_flag = 1;
    pthread_join(_thread_ids[gpio_num], (void**)&ret);
  }
}

static PyObject* tone(PyObject *self, PyObject *args) {
  char error_msg[EXCEPTION_STRING_LEN];
  const char *gpio_pin;
  FILE *state_fd;
  float frequency;
  int gpio_num, thread_error;
  thread_config *config;
  if(!PyArg_ParseTuple(args, "sf", &gpio_pin, &frequency)) {
    Py_INCREF(Py_None);
    return Py_None;
  }
  gpio_num = PyGPIO_getGPIONum(gpio_pin);
  if (gpio_num < 0) {
    snprintf(error_msg, EXCEPTION_STRING_LEN, "Invalid GPIO pin: %s", gpio_pin);
    PyErr_SetString(PyExc_ValueError, error_msg);
    return NULL;
  }
  if (!_thread_configs[gpio_num]) {
    state_fd = PyGPIO_getStateFileLock(gpio_pin);
    if (!state_fd) {
      snprintf(error_msg, EXCEPTION_STRING_LEN, 
               "Could not open state file for %s", gpio_pin);
       PyErr_SetString(PyExc_ValueError, error_msg);
      return NULL;
    }
    config = (thread_config *) malloc(sizeof(thread_config));
    config->state_fd = state_fd;
    config->gpio_pin = calloc(strlen(gpio_pin), sizeof(char));
    config->gpio_num = gpio_num;
    config->update_flag = 1;
    config->kill_flag = 0;
    config->frequency = frequency;
    _thread_configs[gpio_num] = config;
    
    thread_error = pthread_create(&(_thread_ids[gpio_num]), NULL, toneThread,
                                  config);
    if (thread_error) {
      cleanupToneConfig(gpio_num);
      snprintf(error_msg, EXCEPTION_STRING_LEN, 
               "Could not create tone thread for %s", gpio_pin);
       PyErr_SetString(PyExc_ValueError, error_msg);
      return NULL;
    }
  }
  else {
    config = _thread_configs[gpio_num];
    while (config->update_flag) {}; // Wait for it to read the last frequency
    config->frequency = frequency;
    config->update_flag = 1;
  }
  Py_INCREF(Py_None);
  return Py_None;
}



static PyObject* noTone(PyObject *self, PyObject *args) {
  char error_msg[EXCEPTION_STRING_LEN];
  const char *gpio_pin;
  int gpio_num;
  
  if(!PyArg_ParseTuple(args, "s", &gpio_pin)) {
    Py_INCREF(Py_None);
    return Py_None;
  }
  gpio_num = PyGPIO_getGPIONum(gpio_pin);
  if (gpio_num < 0) {
    snprintf(error_msg, EXCEPTION_STRING_LEN, "Invalid GPIO pin: %s", gpio_pin);
    PyErr_SetString(PyExc_ValueError, error_msg);
    return NULL;
  }
  if (_thread_configs[gpio_num]){
    killToneThread(gpio_num);
    cleanupToneConfig(gpio_num);
  }
  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject* toneInit(PyObject *self, PyObject *args) {
  if (import_gpio() < 0) return NULL;
  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject* toneCleanup(PyObject *self, PyObject *args) {
  int gpio_num;
  for (gpio_num=0; gpio_num<MAX_GPIO_NUM; gpio_num++) {
    if (_thread_configs[gpio_num]){
      killToneThread(gpio_num);
      cleanupToneConfig(gpio_num);
    }
  }
  Py_INCREF(Py_None);
  return Py_None;
}

static PyMethodDef toneMethods[]=
{
	{ "tone", tone, METH_VARARGS, "" },
	{ "noTone", noTone, METH_VARARGS, "" },
	{ "toneInit", toneInit, METH_VARARGS, "" },
	{ "toneCleanup", toneCleanup, METH_VARARGS, "" },
  { NULL, NULL },
};

PyMODINIT_FUNC inittone(void) {
  PyObject *m;
  m = Py_InitModule("tone", toneMethods);
  if (m == NULL) return;
}