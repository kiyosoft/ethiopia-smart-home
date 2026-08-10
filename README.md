# Ethiopian Smart Home

A Home Assistant custom-integration ecosystem for Ethiopian homes.

> A smart home system that understands Ethiopian life.

## Independently installable

Each folder under `custom_components/` is **self-contained**:

| Integration | Install alone? | Notes |
|-------------|----------------|-------|
| `ethiopia_core` | Yes | Calendar + holidays |
| `ethiopia_religion` | Yes | Bundles its own calendar math + Sinksar data |
| `ethiopia_power` | Yes | Link any grid/battery/solar entities |
| `ethiopia_water` | Yes | Optional grid entity; works without Power |
| `ethiopia_voice` | Yes | Needs HA `conversation` only; optional date/grid links |

They may *optionally* reference each other's entities (e.g. water → `binary_sensor.grid_available`), but never import each other's Python packages.

### Install one integration

```bash
INTEGRATIONS=ethiopia_power HA_HOST=192.168.100.245 HA_USER=root ./scripts/install-to-ha.sh
```

### Install several

```bash
INTEGRATIONS="ethiopia_core ethiopia_religion" HA_HOST=192.168.100.245 HA_USER=root ./scripts/install-to-ha.sh
```

### Install all

```bash
HA_HOST=192.168.100.245 HA_USER=root ./scripts/install-to-ha.sh
ssh root@192.168.100.245 'ha core restart'
```

## Enable

Settings → Devices & services → Add Integration → pick only what you installed.

## Entities (summary)

- **core:** `sensor.ethiopian_date`, day/month/year, `sensor.ethiopian_time`, `next_holiday`, `calendar.ethiopian_holidays`
- **religion:** Sinksar, fast, feast, `calendar.orthodox_feasts_fasts`, Hijri, prayer times
- **power:** `binary_sensor.grid_available`, outage / battery sensors, load-shedding schedule restore estimate, 30-day outage stats
- **water:** tank level, pump switch, `ethiopia_water.run_pump_cycle`
- **voice:** Amharic Assist sentences (`ሳሎን መብራት አብራ`, `ቤቱን ሁሉ አጥፋ`, `ዛሬ ቀኑ ስንት ነው፧`, `መብራት አለ፧`) — STT is separate (Wyoming)

### Amharic voice pipeline (HA Green / OS)

`ethiopia_voice` only installs Assist **sentences + intents**. Microphone speech-to-text uses the official **Whisper** app (Wyoming), not a pip package inside this integration.

1. Add **Ethiopia Voice** (Settings → Devices & services).
   Sentences are installed under `custom_sentences/en/` as well as `am/`,
   because Assist has no built-in Amharic intent language — keep the default
   English Assist pipeline and type/speak the Amharic phrases.
2. Settings → **Apps** → Install **Whisper** → Start it.
3. Whisper configuration (Amharic):
   - **Model:** `custom`
   - **Custom model:** `chappM/whisper-amharic-small-v2` (or another Amharic Whisper model ID)
   - **Language:** `am` if the option is available; otherwise leave default and rely on the fine-tuned model
4. Accept the **Wyoming Protocol** discovery (or Add integration → Wyoming).
5. Settings → Voice assistants → your Assist pipeline:
   - **Speech-to-text:** the Whisper / Wyoming service
   - **Language:** Amharic (`am`) where offered
6. Test typed Assist first (`ሳሎን መብራት አብራ`), then microphone.

On HA Green, prefer a **small** Amharic model; larger Whisper models may be slow or OOM on the device.

## Develop

```bash
cd ~/Projects/HomeAssistant/ethiopia-smart-home
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest tests/ -v
```

## License

Apache-2.0
