# Software

Esta pasta reúne software que **não é firmware embarcado**.

```text
software/
└── web/     # UI web legada (contador/temporizador) para experimentos locais
```

## web/

A pasta [`web/`](./web/) veio de `firmware/data/` e contém uma interface web
legada (`index.html`, `script.js`, `style.css`, `hammer.min.js`). Ela não é
gravada no Pico/ESP32 e não substitui os scripts MicroPython de operação.

## Firmware

O firmware oficial continua em [`../firmware/micropython/`](../firmware/micropython/).
Não adicione firmware novo aqui.
