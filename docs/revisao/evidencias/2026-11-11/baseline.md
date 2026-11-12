# Baseline de Auditoria — Ignição SMD / PTH

- Gerado: 2026-11-11 15:59:24
- Branch: main
- HEAD: 5783c468103373a8fd0e3520fb89a02dc12da596 fix(repo): recupera esquemas do historico do KiCad
- Snapshot: C:\Users\italo\AppData\Local\Temp\opencode\ignitor-audit-2026-11-11

## git status (working tree auditado)
```
M .gitignore
 M CHANGELOG.md
 M README.md
 M docs/ARQUITETURA.md
 M docs/ENCLOSURES.md
 M docs/INSTALL.md
 M docs/README_API.md
 M docs/troubleshooting.md
 M firmware/micropython/README.md
 M firmware/micropython/estacao_comando_esp.py
 M firmware/micropython/estacao_ignicao_esp.py
 M hardware/kicad/placas/ignicao_pth/ignicao_pth.kicad_pcb
 M hardware/kicad/placas/ignicao_pth/jlcpcb/gerber/ignicao_pth-CuBottom.gbr
 M hardware/kicad/placas/ignicao_pth/jlcpcb/gerber/ignicao_pth-CuTop.gbr
 M hardware/kicad/placas/ignicao_pth/jlcpcb/gerber/ignicao_pth-EdgeCuts.gbr
 M hardware/kicad/placas/ignicao_pth/jlcpcb/gerber/ignicao_pth-MaskBottom.gbr
 M hardware/kicad/placas/ignicao_pth/jlcpcb/gerber/ignicao_pth-MaskTop.gbr
 M hardware/kicad/placas/ignicao_pth/jlcpcb/gerber/ignicao_pth-NPTH-drl_map.pdf
 M hardware/kicad/placas/ignicao_pth/jlcpcb/gerber/ignicao_pth-NPTH.drl
 M hardware/kicad/placas/ignicao_pth/jlcpcb/gerber/ignicao_pth-PTH-drl_map.pdf
 M hardware/kicad/placas/ignicao_pth/jlcpcb/gerber/ignicao_pth-PTH.drl
 M hardware/kicad/placas/ignicao_pth/jlcpcb/gerber/ignicao_pth-PasteBottom.gbr
 M hardware/kicad/placas/ignicao_pth/jlcpcb/gerber/ignicao_pth-PasteTop.gbr
 M hardware/kicad/placas/ignicao_pth/jlcpcb/gerber/ignicao_pth-SilkBottom.gbr
 M hardware/kicad/placas/ignicao_pth/jlcpcb/gerber/ignicao_pth-SilkTop.gbr
 M hardware/kicad/placas/ignicao_pth/jlcpcb/production_files/BOM-ignicao_pth.csv
 M hardware/kicad/placas/ignicao_pth/jlcpcb/production_files/CPL-ignicao_pth.csv
 M hardware/kicad/placas/ignicao_pth/jlcpcb/production_files/GERBER-ignicao_pth.zip
 M test/test_firmware.py
?? firmware/micropython/protocolo_lora.py
```

## Configuração strict aplicada nas cópias
```
courtyards_overlap: error
missing_courtyard: warning
pth_inside_courtyard: warning
footprint_type_mismatch: warning
isolated_copper: error
track_not_centered_on_via: warning
footprint_filters_mismatch: warning
```

## Hashes SHA-256

| Placa | Arquivo | Bytes | mtime | SHA-256 |
|---|---|---:|---|---|
| ignicao_smd | alimentacao.kicad_sch | 46618 | 2026-11-04 11:10:30 | `19249506D48E7A4A67D90BDEC89CECA6A3BADBD343303E9B9EB7DF450434BDB8` |
| ignicao_smd | botao.kicad_sch | 20321 | 2026-11-04 11:10:30 | `70011D66A0ADD392A92077385A5A0C8D1BDDB3AF388F897FCC2253367CDC2A1B` |
| ignicao_smd | BUZZER.kicad_sch | 19486 | 2026-11-04 11:10:30 | `3968FB105338E3646AC29F28E2BCFBC8E28EF8BDD5D010FF7C89A8797925CBAD` |
| ignicao_smd | EXPANSAO.kicad_sch | 10882 | 2026-11-04 11:10:30 | `71BD222F76C57EA95CA14EECBB874E6F9D83A59DEFE2077772DF08267D18562E` |
| ignicao_smd | ignicao_smd.kicad_pcb | 947173 | 2026-11-04 23:03:32 | `E568285FDEEDE17E08788F59B0F76CC994D52BA7A453B3F8E0146E8F1E039D90` |
| ignicao_smd | ignicao_smd.kicad_prl | 2625 | 2026-11-04 15:38:51 | `80300B3CC1566976594BA74A87F545306BBA4F32B52749EEB35CB27A185532BC` |
| ignicao_smd | ignicao_smd.kicad_pro | 19656 | 2026-11-04 11:19:32 | `7C3B4C3B90575153483F7AA4006E4D85B38D4419DE56FD33296A66A9EEFDDD96` |
| ignicao_smd | ignicao_smd.kicad_sch | 6057 | 2026-11-04 11:10:30 | `498801374BBCB5E1AD2D0B1A8B9D96B5EE512216709517C060A5FA47065AA0E6` |
| ignicao_smd | leds_oled.kicad_sch | 32790 | 2026-11-04 11:10:30 | `D380D924743B9987D4253276D647673B653ED5D55D7B8BD41863AEF0ADC759EB` |
| ignicao_smd | LORA.kicad_sch | 22420 | 2026-11-04 11:10:30 | `BF96B79FA65D3703D0A36F8B37021E4756E49C670DE701476964237DDAE67E5B` |
| ignicao_smd | mcu_esp32.kicad_sch | 44996 | 2026-11-04 11:10:30 | `B334E8E0D74492CFBEB4C2BC89BEFEE3463AA00AD85AF27DFA3DDBB3600B83F1` |
| ignicao_smd | protecao.kicad_sch | 44739 | 2026-11-04 11:10:30 | `55A8B2D11F984BC2AB3123DF325F60A52CA2F93D6EEC742A2F6FA0BFE3E06F68` |
| ignicao_smd | rele.kicad_sch | 57563 | 2026-11-04 11:10:30 | `96493238EC77D393ADE2644E00F70471EDFFD06D8B168E95E71F4EDBE7F3BCEF` |
| ignicao_smd | jlcpcb/gerber/ignicao_smd-CuBottom.gbr | 98333 | 2026-11-04 15:38:51 | `736C00FB2717CE8CBE75D54CD82CCCABC8C6E1BF8E76DA32B38A1E25F61F8036` |
| ignicao_smd | jlcpcb/gerber/ignicao_smd-CuTop.gbr | 129253 | 2026-11-04 15:38:51 | `DD04A7AC05D728D279E5B73D5EC46AC7F004597C567E0CC2450554257A638932` |
| ignicao_smd | jlcpcb/gerber/ignicao_smd-EdgeCuts.gbr | 636 | 2026-11-04 15:38:51 | `40DBD75D2619B3237980505A295D0A0FF9D98F0A11C460449FB3BE893B01FA51` |
| ignicao_smd | jlcpcb/gerber/ignicao_smd-MaskBottom.gbr | 4438 | 2026-11-04 15:38:51 | `893EC88733B5D134479871A1B99A7EA2813C1C9FA5E8B1B97C68070D75B8702D` |
| ignicao_smd | jlcpcb/gerber/ignicao_smd-MaskTop.gbr | 5476 | 2026-11-04 15:38:51 | `A3129B57E5CB9BBAB758FA39F4980A51E3FC4677D4CBDA45AFF981EDB102CC71` |
| ignicao_smd | jlcpcb/gerber/ignicao_smd-NPTH-drl_map.pdf | 6110 | 2026-11-04 15:38:51 | `4CA78CDD7F305A54AFD01839AE7E1E72FB266B392BBBDC4E8DCC8F602F805AE4` |
| ignicao_smd | jlcpcb/gerber/ignicao_smd-NPTH.drl | 272 | 2026-11-04 15:38:51 | `2206A124B2090B13442C5AF73001F868D5FF54CBD4868F0383335AF4ABD788EC` |
| ignicao_smd | jlcpcb/gerber/ignicao_smd-PasteBottom.gbr | 471 | 2026-11-04 15:38:51 | `F5695CE4300120775397078B80782EFDEC6F705D75FF9619F5F369D672403980` |
| ignicao_smd | jlcpcb/gerber/ignicao_smd-PasteTop.gbr | 1497 | 2026-11-04 15:38:51 | `A1917AB561F0138D7891624A28980DE37DCED71756FE618E65181EEDBD9FC417` |
| ignicao_smd | jlcpcb/gerber/ignicao_smd-PTH-drl_map.pdf | 17290 | 2026-11-04 15:38:51 | `90942559DBEE3A5770DA52AC7DCDE6122F2FE39AC95C2A149736E980C517B80E` |
| ignicao_smd | jlcpcb/gerber/ignicao_smd-PTH.drl | 2309 | 2026-11-04 15:38:51 | `67015A29779CDE78EEF33A8AB318C28772CF0BF783759855845FAC4366133E3E` |
| ignicao_smd | jlcpcb/gerber/ignicao_smd-SilkBottom.gbr | 374027 | 2026-11-04 15:38:51 | `289D02A81AB62183E5B92CBCEE8009D5E3E38C6E6D396EDF3E169DE9AD3209AE` |
| ignicao_smd | jlcpcb/gerber/ignicao_smd-SilkTop.gbr | 145391 | 2026-11-04 15:38:51 | `26A5DF9C6FE168B850D42B08E91758DA854B1A3320DDF8057B9A650E448F7B51` |
| ignicao_smd | jlcpcb/production_files/BOM-ignicao_smd.csv | 987 | 2026-11-04 15:38:51 | `2D3C0CD48BC2AEE3CC003522C3193704C2290E6DE8520A5A24C0BD63569DEC73` |
| ignicao_smd | jlcpcb/production_files/CPL-ignicao_smd.csv | 1597 | 2026-11-04 15:38:51 | `31796066F1BD817157EB8AA0E2E6298B55F03D0FEB89F63A3C3B5F2754DADA53` |
| ignicao_smd | jlcpcb/production_files/GERBER-ignicao_smd.zip | 216082 | 2026-11-04 15:38:51 | `1F7E6AD4422480E2D4EECAEAAF3FB12C2C246F821F1C0B77147C234673090CED` |
| ignicao_smd | jlcpcb/project.db | 20480 | 2026-11-04 15:38:51 | `FCFD64E213DA3FA934B91F84E9F45299A0DB7B67157F30B322F04C39FB0B90DF` |
| ignicao_pth | alimentacao.kicad_sch | 41669 | 2026-11-04 14:06:20 | `DA0BF9F2B7A215119428BBF6C874380AA0CFEB7C9B8631EB229EA55F2465AF7C` |
| ignicao_pth | botao.kicad_sch | 19392 | 2026-11-04 14:06:20 | `CB28FD8F4A91034E019399CD0C9B4B2D7530D5973ECEB96E2C09EF07E5514410` |
| ignicao_pth | BUZZER.kicad_sch | 19529 | 2026-11-04 14:06:20 | `D54FE3B3D1AB2D5EECBD4F8197287695C46F59535523CCA655EFD2CA089D430F` |
| ignicao_pth | EXPANSAO.kicad_sch | 10880 | 2026-11-04 14:06:20 | `7395BEDF0E8D6ED01E74617214D1123E7BE718C695A8B58A7E8A9A3122B9D56D` |
| ignicao_pth | ignicao_pth.kicad_pcb | 1543542 | 2026-11-11 15:34:58 | `1397C2A365C53807DF4D317DA69917C3BAD95A04DC8046171BFEB5D7C03E2F63` |
| ignicao_pth | ignicao_pth.kicad_prl | 2623 | 2026-11-11 15:38:10 | `7470CCF7411A4124366FE2F198105794F765967AAE06D87E4E601508890A21A9` |
| ignicao_pth | ignicao_pth.kicad_pro | 20319 | 2026-11-04 14:06:20 | `3CD55B51BA900CEF7DEDBC5DFE9FCB893E60384691965518308C22BCADFF92BA` |
| ignicao_pth | ignicao_pth.kicad_sch | 6057 | 2026-11-04 14:06:20 | `AA160B46C6413777D3BCBD756CBF221D67D1E48F5275374F482AB5387E36FCF8` |
| ignicao_pth | leds_oled.kicad_sch | 32161 | 2026-11-04 14:06:20 | `28323C33A2027DB174A8481DDE104FA8DCCF850BCAFD0B6B6B20933EAA21FF17` |
| ignicao_pth | LORA.kicad_sch | 22420 | 2026-11-04 14:06:20 | `DA2BBB8E5B3B6DF07A4CD79781B6FCB69E64EDA453C4C8A409F1B048864BB296` |
| ignicao_pth | mcu_esp32.kicad_sch | 44969 | 2026-11-04 14:06:20 | `1AB36706BEC7E4AF651C7733CEA4E7EA096F72722109B45AFD572075DBDADCC9` |
| ignicao_pth | rele.kicad_sch | 57070 | 2026-11-04 14:06:20 | `DB8F303DE1DEAF108EF6E42F691C74BE571FAA0A3FA6748A42C25BB3DCC2CFC2` |
| ignicao_pth | jlcpcb/gerber/ignicao_pth-CuBottom.gbr | 220747 | 2026-11-11 15:34:36 | `62EB41F60960C67206F113BA53378EB47568A5EDEC59B3FCA346FB1789A103AD` |
| ignicao_pth | jlcpcb/gerber/ignicao_pth-CuTop.gbr | 211608 | 2026-11-11 15:34:36 | `962370500C7DC0B11AB446C1E307D08D38C5549EAA847D49774321D70DFB6F7A` |
| ignicao_pth | jlcpcb/gerber/ignicao_pth-EdgeCuts.gbr | 720 | 2026-11-11 15:34:36 | `22F220F27EB34987572A2DCA345F21B36DF35814CAF43D9F9E684970F525442A` |
| ignicao_pth | jlcpcb/gerber/ignicao_pth-MaskBottom.gbr | 5842 | 2026-11-11 15:34:36 | `EE60857ECD379F63E4A9C34A64FDD1166E7CC4C8096D3A8271621540C9CDDFD0` |
| ignicao_pth | jlcpcb/gerber/ignicao_pth-MaskTop.gbr | 5626 | 2026-11-11 15:34:36 | `48A55EF9B61C7601D78F91DD74CBC62D2910AF13DDA1BFB709C9FCC8CF59F388` |
| ignicao_pth | jlcpcb/gerber/ignicao_pth-NPTH-drl_map.pdf | 12215 | 2026-11-11 15:34:36 | `A7F547A6044E838EADD2D3CF97D328EC0D2C941973CA97C9F565B03E0BC6A67A` |
| ignicao_pth | jlcpcb/gerber/ignicao_pth-NPTH.drl | 406 | 2026-11-11 15:34:36 | `79D54A823D086E1D71C156B6586DE04BE80637A1D0558C7EB198EA6A94A4FF55` |
| ignicao_pth | jlcpcb/gerber/ignicao_pth-PasteBottom.gbr | 471 | 2026-11-11 15:34:36 | `4D2C16A450C46FA921B488A871EB527FFA22D01BFC2545719F93673C72E6C200` |
| ignicao_pth | jlcpcb/gerber/ignicao_pth-PasteTop.gbr | 471 | 2026-11-11 15:34:36 | `732665A35E8D4EF80EE009FEB7BDE25ED480FBE4BD704049AC6816C0DB3EDE23` |
| ignicao_pth | jlcpcb/gerber/ignicao_pth-PTH-drl_map.pdf | 19085 | 2026-11-11 15:34:36 | `0BF3197FF3C5473927E156708636061F7CDB2867B4E1716190147044B761456C` |
| ignicao_pth | jlcpcb/gerber/ignicao_pth-PTH.drl | 2556 | 2026-11-11 15:34:36 | `767C7A8B4EA43F3704FA2F868DDBCD08689A072CB7B2505B9B6CC2B96A57DB7C` |
| ignicao_pth | jlcpcb/gerber/ignicao_pth-SilkBottom.gbr | 750395 | 2026-11-11 15:34:36 | `D6F9FAD1009A4EB66F1DCBFF65856EEA07F63649BE12DF0F45C4E87D46818E3B` |
| ignicao_pth | jlcpcb/gerber/ignicao_pth-SilkTop.gbr | 167228 | 2026-11-11 15:34:36 | `7506AAAC86081D9A71CF9E1A6AF0558AB6A8E32EE249B405540EE23CB3D25A15` |
| ignicao_pth | jlcpcb/production_files/BOM-ignicao_pth.csv | 1467 | 2026-11-11 15:34:37 | `5790320FCF9AAA9ADE5C0BCA57301BC8F74AD5B22A3F4183DD263D644C491E81` |
| ignicao_pth | jlcpcb/production_files/CPL-ignicao_pth.csv | 2055 | 2026-11-11 15:34:37 | `7D5E4AC0ED4A0B23B79436FFC544CEE72EC4CB3A93518DEF60B0E64F57F92D93` |
| ignicao_pth | jlcpcb/production_files/GERBER-ignicao_pth.zip | 402806 | 2026-11-11 15:34:37 | `B5FDCCEC170BE2ECAAA5742904AACE0B103CB0A3322DDF2F64284199BC92FC73` |
| ignicao_pth | jlcpcb/project.db | 20480 | 2026-11-11 15:34:37 | `21261B86C6A816A9B755FF7503AA7176448E16643FDACD999A8F3D681CEAA65A` |

## Observações de baseline

- SMD: PCB de 2026-11-04 23:03; pacote JLCPCB de 2026-11-04 15:38 — gerbers/BOM/CPL anteriores à placa.
- PTH: PCB e pacote JLCPCB de 2026-11-11 15:34 — alinhados por mtime, a confirmar por conteúdo.
- PTH: `.kicad_pcb` alterado em 2026-11-11, mas os `.kicad_sch` são de 2026-11-04 — mudança somente de layout/zonas.
- `ignicao_cnc` fora de escopo.