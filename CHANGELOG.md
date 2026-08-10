# Changelog

All notable changes to Ethiopian Smart Home are documented here.

## [0.1.2] - 2026-08-10

### Added
- `sensor.ethiopian_time` with traditional dawn-based Ethiopian clock (day/night)
- Full Orthodox fasting model (Hudadi, Nenewie, Hawariat, Filseta, Nebiyat, Gahad, Wed/Fri)
- `calendar.orthodox_feasts_fasts` for major Orthodox fasts and feasts
- Power load-shedding schedule (days + window) with schedule-based restore estimates
- 30-day outage history sensors: count, total duration, longest outage
- Project `/release` skill for versioned shipping

### Changed
- `sensor.orthodox_fast` now exposes `key`, `start`, `end`, and `days_remaining`
- `sensor.next_power_estimate` uses configured schedule windows instead of a duration heuristic
