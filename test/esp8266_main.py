# ==============================================================================
#   Bootstrap para o ESP8266 (vai para a placa como "main.py")
#   O firmware de teste em si vai como modulo pre-compilado
#   (ignitor_teste.mpy, gerado com mpy-cross): o parser do ESP8266 nao
#   aguenta compilar os ~19 KB de fonte em RAM, mas carrega o .mpy numa boa
#   (o boot so executa automaticamente o "main.py"; este arquivo e ele).
#
#   Geracao/deploy (a partir de test/):
#     mpy-cross -march=xtensa -o ignitor_teste.mpy mp_teste_hardware_esp8266.py
#     mpremote connect COMx fs cp esp8266_main.py :main.py
#     mpremote connect COMx fs cp ignitor_teste.mpy :ignitor_teste.mpy
# ==============================================================================

import gc

gc.collect()

from ignitor_teste import executar

executar()
