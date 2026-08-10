# Changelog and GitHub release notes

## CHANGELOG.md layout

Keep a single root `CHANGELOG.md`. Newest version at the top.

```markdown
# Changelog

All notable changes to Ethiopian Smart Home are documented here.

## [0.1.2] - 2026-08-10

### Added
- `sensor.ethiopian_time` with day/night Ethiopian clock
- `calendar.orthodox_feasts_fasts` for major Orthodox fasts and feasts
- Power load-shedding schedule and 30-day outage history sensors

### Changed
- `sensor.next_power_estimate` uses schedule windows instead of a duration heuristic

### Fixed
- (omit section if empty)
```

## Bullet rules

- Write for Home Assistant users, not commit dumps.
- Name entities/services when relevant (`sensor.ethiopian_time`, `ethiopia_water.run_pump_cycle`).
- Group under Added / Changed / Fixed / Removed only as needed.
- One idea per bullet; no PR numbers required.

## Mapping commits → sections

| Change type | Section |
|-------------|---------|
| New entity, service, calendar, blueprint | Added |
| Behavior change, estimate logic, options | Changed |
| Bug fix, incorrect fast day, crash | Fixed |
| Deleted entity/API | Removed |

## GitHub Release body

Mirror the version’s CHANGELOG section under `## What's changed`. Optional footer:

```markdown
## Install

HACS or copy the relevant folders from `custom_components/`, then restart Home Assistant.
```
