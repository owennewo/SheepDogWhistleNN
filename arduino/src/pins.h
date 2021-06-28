#include <Arduino.h>

// MOT0
#define M0_A              PB1  
#define M0_B              PB0  
#define M0_C              PA7  
// MOT1
#define M1_A              PA6  
#define M1_B              PA3  
#define M1_C              PA2  
// MOT2
#define M2_A              PB9  
#define M2_B              PA1  
#define M2_C              PB8  

// can control sony/canon and Panasonic cameras
#define IR              PA0
// through 10K / 1.5K voltage divider
#define LIPO            PA5
#define BOOT1           PB2

// #define USB_D           PB5

// I2C 1 & 2
#define I2C2_SCL        PB6
#define I2C2_SDA        PB7
#define I2C1_SCL        PB10
#define I2C1_SDA        PB11

#define LED0            PB12
#define LED_GREEN       PB12 
#define LED_BUILTIN     PB12 

// EITHER SPI (requires desolder RED LED)
#define SPI2_SCK        PB13
#define SPI2_MISO       PB14
#define SPI2_MOSI       PB15

#define PIN_SPI_SS      AUX2
#define PIN_SPI_SS1     AUX1
#define PIN_SPI_SS2     AUX0
#define PIN_SPI_MOSI    SPI2_MOSI
#define PIN_SPI_MISO    SPI2_MISO
#define PIN_SPI_SCK     SPI2_SCK

// OR 
#define LED1            PB13
#define LED_RED         PB13
#define AUX0            PB14
#define AUX1            PB15

#define RC2             PA8
// EITHER
#define RC1             PA9
#define RC0             PA10
// OR
#define USART1_TX       PA9
#define USART1_RX       PA10

#define RC0             PA10
// #define USB_DM          PA11
// #define USB_DP          PA12
#define SWDIO           PA13
#define SWDCL           PA14
#define AUX2            PA15

#define POT0            PC0
#define POT1            PC1
#define POT2            PC2

#define BUT             PC3
#define XOR             PC4

// Could be connected RC Input  PWM (mapped to TIM8 for interrupts)
#define RC2_0           PC6
#define RC2_1           PC7
#define RC2_2           PC8
#define RC2_3           PC9

#define USART3_TX       PC10
#define USART3_RX       PC11

// On-board user button
#ifndef USER_BTN
  #define USER_BTN      BUT
#endif

// Timer Definitions
#ifndef TIMER_SERVO
  #define TIMER_SERVO   TIM2
#endif

// #define Serial SerialUSB

// UART Definitions
// Define here Serial instance number to map on Serial generic name
// #ifndef SERIAL_UART_INSTANCE
//   #define SERIAL_UART_INSTANCE  3
// #endif

// // Serial1 is not marked on board (shared with RC1 anf RC2 pins) 
// #define ENABLE_HWSERIAL1

void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {};
  RCC_PeriphCLKInitTypeDef PeriphClkInit = {};

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
  RCC_OscInitStruct.HSEState = RCC_HSE_ON;
  RCC_OscInitStruct.HSEPredivValue = RCC_HSE_PREDIV_DIV1;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
  RCC_OscInitStruct.PLL.PLLMUL = RCC_PLL_MUL9;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK) {
    Error_Handler();
  }
  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK | RCC_CLOCKTYPE_SYSCLK
                                | RCC_CLOCKTYPE_PCLK1 | RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV2;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_2) != HAL_OK) {
    Error_Handler();
  }
  PeriphClkInit.PeriphClockSelection = RCC_PERIPHCLK_USB;
  PeriphClkInit.UsbClockSelection = RCC_USBCLKSOURCE_PLL_DIV1_5;
  if (HAL_RCCEx_PeriphCLKConfig(&PeriphClkInit) != HAL_OK) {
    Error_Handler();
  }
}

#ifdef HAL_UART_MODULE_ENABLED
const PinMap PinMap_UART_TX[] = {
  // {PA_2,       USART2, STM_PIN_DATA(STM_MODE_AF_PP, GPIO_PULLUP, AFIO_USART2_DISABLE)},
  {PA_9,       USART1, STM_PIN_DATA(STM_MODE_AF_PP, GPIO_PULLUP, AFIO_USART1_DISABLE)},
  // {PB_6,       USART1, STM_PIN_DATA(STM_MODE_AF_PP, GPIO_PULLUP, AFIO_USART1_ENABLE)},
  // {PB_10,      USART3, STM_PIN_DATA(STM_MODE_AF_PP, GPIO_PULLUP, AFIO_NONE)},
  // {PC_10,      UART4,  STM_PIN_DATA(STM_MODE_AF_PP, GPIO_PULLUP, AFIO_NONE)},
  {PC_10, USART3, STM_PIN_DATA(STM_MODE_AF_PP, GPIO_PULLUP, AFIO_USART3_PARTIAL)},
  // {PC_12,      UART5,  STM_PIN_DATA(STM_MODE_AF_PP, GPIO_PULLUP, AFIO_NONE)},
  {NC,         NP,     0}
};
#endif

#ifdef HAL_UART_MODULE_ENABLED
const PinMap PinMap_UART_RX[] = {
  // {PA_3,       USART2, STM_PIN_DATA(STM_MODE_INPUT, GPIO_PULLUP, AFIO_USART2_DISABLE)},
  {PA_10,      USART1, STM_PIN_DATA(STM_MODE_INPUT, GPIO_PULLUP, AFIO_USART1_DISABLE)},
  // {PB_7,       USART1, STM_PIN_DATA(STM_MODE_INPUT, GPIO_PULLUP, AFIO_USART1_ENABLE)},
  // {PB_11,      USART3, STM_PIN_DATA(STM_MODE_INPUT, GPIO_PULLUP, AFIO_NONE)},
  // {PC_11,      UART4,  STM_PIN_DATA(STM_MODE_INPUT, GPIO_PULLUP, AFIO_NONE)},
  {PC_11, USART3, STM_PIN_DATA(STM_MODE_INPUT, GPIO_PULLUP, AFIO_USART3_PARTIAL)},
  // {PD_2,       UART5,  STM_PIN_DATA(STM_MODE_INPUT, GPIO_PULLUP, AFIO_NONE)},
  {NC,         NP,     0}
};
#endif
