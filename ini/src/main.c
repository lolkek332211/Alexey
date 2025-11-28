// Простейший код без SystemInit
int main(void) {
    // Адреса регистров STM32F103
    volatile unsigned int* RCC_APB2ENR = (unsigned int*)0x40021018;
    volatile unsigned int* GPIOA_CRH = (unsigned int*)0x40010804;
    volatile unsigned int* USART1_BRR = (unsigned int*)0x40013808;
    volatile unsigned int* USART1_CR1 = (unsigned int*)0x4001380C;
    volatile unsigned int* USART1_SR = (unsigned int*)0x40013800;
    volatile unsigned int* USART1_DR = (unsigned int*)0x40013804;
    
    // Включаем тактирование
    *RCC_APB2ENR |= (1<<2) | (1<<14);
    
    // Настраиваем PA9 как TX
    *GPIOA_CRH = (*GPIOA_CRH & ~0xFF0) | 0x490;
    
    // Настраиваем USART1
    *USART1_BRR = 0x0341;
    *USART1_CR1 = (1<<13) | (1<<3);
    
    char message[] = "alexey\n";
    
    while(1) {
        for(int i = 0; message[i] != 0; i++) {
            while(!(*USART1_SR & (1<<7)));
            *USART1_DR = message[i];
        }
        for(volatile int j = 0; j < 1000000; j++);
    }
}