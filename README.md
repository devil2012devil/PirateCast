# PirateCast

Пиратская интеграция для Home Assistant: сенсоры изменения атмосферного
давления за 1 и 3 часа + карточка тенденции давления (регистрируется
автоматически).

## Установка через HACS

1. HACS → Integrations → `⋮` → **Custom repositories**.
2. URL: `https://github.com/devil2012devil/PirateCast`
3. Category: **Integration**.
4. Установите **PirateCast**, перезапустите Home Assistant.
5. Настройки → Устройства и службы → **Добавить интеграцию** → PirateCast.
6. Укажите исходный сенсор давления (например, `sensor.atmosfernoe_davlenie`).

Карточка `custom:piratecast-card` станет доступна автоматически.

## Конфигурация карточки

```yaml
type: custom:piratecast-card
entity: sensor.piratecast_pressure_change_3h
title: Изменение давления за 3 часа
min: -4
max: 4