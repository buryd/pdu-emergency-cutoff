# Wiring sketch (text)

```
                         APC UPS Pro 1500VA
                                  |
                                  v
                    +-----------------------------+
                    |     DLI IoT Power Relay     |
                    |  Always On --> Pico 5V PSU  |
                    |  Norm On  --> PDU inlet     |
                    |  Switch   <-- Pico GP15     |
                    +-----------------------------+
                                  |
                                  v
                    PDU (2-post rack) --> loads
                         ^
                         | SCT-013-005 on HOT
                         v
                    CT Bias Adapter --> Pico GP26 (ADC0)

    [Learn] GP10   [Save] GP11   [Reset] GP12
    [Armed] GP16   [Tripped] GP17   [Learn LED] GP18
```
