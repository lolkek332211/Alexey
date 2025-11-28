Проект: Создание прошивки для STM32 с выводом строк в эмуляторе Renode
Содержание
Введение

Требования

Структура проекта

Реализация

Сборка и запуск

Тестирование

Заключение

Введение
Renode - это фреймворк для эмуляции embedded-систем, который позволяет разрабатывать и тестировать прошивки без физического оборудования. В данном проекте мы создадим минимальную прошивку для STM32F4, которая выводит текстовые сообщения через UART и тестируем ее в эмуляторе Renode.

Цель проекта: освоить процесс создания embedded-прошивок с использованием эмуляции для отладки и тестирования.

Требования
Аппаратные требования
Микроконтроллер: STM32F407VG

Периферия: UART2 (PA2 - TX, PA3 - RX)

Тактовая частота: 168 МГц

Программные требования
Компилятор: ARM GCC Toolchain

Эмулятор: Renode 1.13+

Система сборки: CMake 3.16+

Операционная система: Linux/Windows/macOS

Функциональные требования
Инициализация системы тактирования

Настройка UART2 для передачи данных

Реализация функции вывода строк

Циклический вывод сообщений с задержкой

Совместимость с эмулятором Renode

Структура проекта
text
stm32-renode-uart/
├── CMakeLists.txt
├── linker.ld
├── renode_config.resc
└── src/
    ├── main.c
    └── system.c
Реализация
main.c
c
#include <stdint.h>

#define RCC_BASE    0x40023800
#define GPIOA_BASE  0x40020000
#define USART2_BASE 0x40004400

#define RCC_AHB1ENR  *(volatile uint32_t*)(RCC_BASE + 0x30)
#define RCC_APB1ENR  *(volatile uint32_t*)(RCC_BASE + 0x40)

#define GPIOA_MODER  *(volatile uint32_t*)(GPIOA_BASE + 0x00)
#define GPIOA_AFRL   *(volatile uint32_t*)(GPIOA_BASE + 0x20)

#define USART2_BRR   *(volatile uint32_t*)(USART2_BASE + 0x08)
#define USART2_CR1   *(volatile uint32_t*)(USART2_BASE + 0x0C)
#define USART2_SR    *(volatile uint32_t*)(USART2_BASE + 0x00)
#define USART2_DR    *(volatile uint32_t*)(USART2_BASE + 0x04)

void uart_init(void) {
    // Enable clocks
    RCC_AHB1ENR |= 1;  // GPIOA
    RCC_APB1ENR |= (1 << 17);  // USART2
    
    // Configure PA2 as AF7 (USART2_TX)
    GPIOA_MODER |= (2 << 4);  // Alternate function
    GPIOA_AFRL |= (7 << 8);   // AF7
    
    // Configure UART
    USART2_BRR = 0x082D;  // 115200 @ 8MHz
    USART2_CR1 = (1 << 13) | (1 << 3);  // UE + TE
}

void uart_send_char(char c) {
    while (!(USART2_SR & (1 << 7)));  // Wait for TXE
    USART2_DR = c;
}

void uart_send_string(const char* str) {
    while (*str) {
        uart_send_char(*str++);
    }
}

void delay(void) {
    for (volatile int i = 0; i < 1000000; i++);
}

int main(void) {
    uart_init();
    
    while (1) {
        uart_send_string("Hello Renode!\r\n");
        uart_send_string("STM32 UART Working\r\n\r\n");
        delay();
    }
}
system.c
c
#include <stdint.h>

uint32_t SystemCoreClock = 8000000;

void SystemInit(void) {
    // Minimal initialization for Renode
}
linker.ld
ld
MEMORY {
    FLASH (rx) : ORIGIN = 0x08000000, LENGTH = 1024K
    RAM (rwx)  : ORIGIN = 0x20000000, LENGTH = 128K
}

SECTIONS {
    .text : {
        *(.text*)
    } > FLASH
    
    .data : {
        *(.data*)
    } > RAM
}
CMakeLists.txt
cmake
cmake_minimum_required(VERSION 3.16)
project(stm32-renode-uart)

set(CMAKE_C_COMPILER arm-none-eabi-gcc)
set(CMAKE_C_FLAGS "-mcpu=cortex-m4 -mthumb -specs=nosys.specs")

add_executable(${PROJECT_NAME} 
    src/main.c
    src/system.c
)

set_target_properties(${PROJECT_NAME} PROPERTIES
    SUFFIX ".elf"
)

add_custom_command(TARGET ${PROJECT_NAME} POST_BUILD
    COMMAND arm-none-eabi-objcopy -O binary ${PROJECT_NAME}.elf ${PROJECT_NAME}.bin
    COMMAND arm-none-eabi-size ${PROJECT_NAME}.elf
)
Сборка и запуск
Установка зависимостей
bash
# Ubuntu/Debian
sudo apt install gcc-arm-none-eabi cmake renode

# Windows (using chocolatey)
choco install gcc-arm-embedded cmake renode
Сборка проекта
bash
mkdir build && cd build
cmake ..
make
Конфигурация Renode (renode_config.resc)
resc
using sysbus
mach create "STM32F4"
machine LoadPlatformDescription @platforms/cpus/stm32f4.repl

sysbus LoadBinary $bin@0x08000000
cpu PC 0x08000000

showAnalyzer uart2
logFile "uart_output.log" uart2

echo "STM32 UART Demo loaded"
start
Запуск в Renode
bash
renode renode_config.resc
# В консоли Renode:
(monitor) set bin "build/stm32-renode-uart.bin"
(monitor) start
Тестирование
Ожидаемый вывод
После запуска в анализаторе UART2 Renode должен отображаться следующий вывод:

text
Hello Renode!
STM32 UART Working

Hello Renode!
STM32 UART Working

Hello Renode!
STM32 UART Working
Проверка работоспособности
Загрузка прошивки: Убедитесь, что бинарный файл загружается без ошибок

Вывод UART: Проверьте наличие ожидаемых сообщений в анализаторе UART2

Стабильность: Прошивка должна работать непрерывно без сбоев

Отладка в Renode
renode
# Полезные команды отладки:
(monitor) sysbus ReadWord 0x40023800  # Чтение RCC
(monitor) cpu PrintRegisters          # Регистры CPU
(monitor) uart2 WaitFor "Hello"       # Ожидание строки
Заключение
В данном проекте была успешно создана минимальная прошивка для STM32F4, демонстрирующая вывод текстовых сообщений через UART в эмуляторе Renode. Проект включает:

Минимальный код для инициализации UART и вывода строк

Конфигурацию сборки с использованием CMake

Сценарий эмуляции для Renode

Инструкции по сборке и тестированию

Преимущества подхода:

Быстрая разработка без физического hardware

Легкая отладка и тестирование

Возможность автоматизации

Низкий порог входа для начинающих
