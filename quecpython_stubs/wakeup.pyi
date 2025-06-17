"""
Function:
Module feature: WakeUp interrupt for enabling edge-triggered interrupts and module wake-up from sleep state.
Currently supported modules: EC600E Series, EC800E Series, EC800Z Series.
Note: WakeUp provides interrupt capabilities not available on standard GPIOs, including dual-edge triggering and wake-up from sleep mode.

Descriptions taken from:
https://developer.quectel.com/doc/quecpython/API_reference/en/pm/WakeUp.html
"""
class WakeUp(object):
    """WakeUp Interrupt

    Class feature: Provides edge-triggered interrupts and wake-up capability from sleep mode.
    Note: Standard GPIOs on EC600/EC800E series don't support dual-edge interrupts or wake-up from sleep.
    Descriptions: https://developer.quectel.com/doc/quecpython/API_reference/en/pm/WakeUp.html
    
    WakeUp Pin Mapping:
    | Module   | WAKEUP0 | WAKEUP2 | WAKEUP3 | WAKEUP4 | WAKEUP5 |
    |----------|---------|---------|---------|---------|---------|
    | EC800E   | -       | Pin79   | Pin109* | Pin108* | Pin19   |
    | EC600E   | -       | Pin9    | Pin51   | Pin50   | Pin39   |
    | EC800Z   | Pin87   | Pin79   | Pin109  | Pin108  | Pin19   |
    * Not available on EC800ECN_LE/LQ/LC variants
    """
    
    def __init__(self, WakeupID, pull, edge=IRQ_RISING_FALLING):
        """Creates a WakeUp interrupt object.

        :param WakeupID: Integer type. WakeUp pin identifier. Use class constants: WAKEUP0, WAKEUP2, WAKEUP3, WAKEUP4, WAKEUP5.
        :param pull: Integer type. Pull mode configuration. Use class constants: PULL_DISABLE, PULL_PU, PULL_PD.
        :param edge: Integer type. Edge trigger configuration (EC800Z only). Default: dual-edge. Use class constants: IRQ_RISING, IRQ_FALLING, IRQ_RISING_FALLING.
        """
    
    def enable(self):
        """Enables the WakeUp interrupt.
        
        When enabled, edge detection will trigger the registered callback function.
        
        :return: Integer. 0 - Success, -1 - Failure.
        """
    
    def disable(self):
        """Disables the WakeUp interrupt.
        
        :return: Integer. 0 - Success, -1 - Failure.
        """
    
    def read(self):
        """Reads current pin level.
        
        :return: Integer. 0 - Low level, 1 - High level.
        """
    
    def deinit(self):
        """Deinitializes and disables WakeUp functionality.
        
        :return: Integer. 0 - Success, -1 - Failure.
        """
    
    def set_callback(self, fun):
        """Sets the interrupt callback function.
        
        :param fun: Callback function. Function prototype: fun(level)
        Callback Parameter:
            level: Integer. 0 = Low level, 1 = High level
        """