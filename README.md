# Home Assistant Redmine Integration

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/mensfeld/homeassistant-redmine/actions/workflows/ci.yml/badge.svg)](https://github.com/mensfeld/homeassistant-redmine/actions/workflows/ci.yml)

A Home Assistant custom integration for creating issues in Redmine via actions. Perfect for home automation scenarios like "Create an issue to buy salt when salt level drops below 15%".

## Features

- Create Redmine issues from Home Assistant automations
- Two-step config flow with automatic discovery of projects, trackers, and priorities
- Default project with per-call override support
- No need to look up numeric IDs - select from dropdown menus

## Installation

### HACS (Recommended)

1. Open HACS in your Home Assistant instance
2. Click the three dots menu in the top right corner
3. Select **Custom repositories**
4. Add this repository URL: `https://github.com/mensfeld/homeassistant-redmine`
5. Select **Integration** as the category
6. Click **Add**
7. Find "Redmine" in the integrations list and click **Download**
8. Restart Home Assistant

### Manual Installation

1. Download the latest release from the [releases page](https://github.com/mensfeld/homeassistant-redmine/releases)
2. Extract and copy the `custom_components/redmine` folder to your Home Assistant `config/custom_components/` directory
3. Restart Home Assistant

## Configuration

1. Go to **Settings** > **Devices & Services**
2. Click **+ Add Integration**
3. Search for **Redmine**
4. **Step 1 - Connection**: Enter your Redmine credentials:
   - **Redmine URL**: Full URL to your Redmine instance (e.g., `https://redmine.example.com`)
   - **API Key**: Your Redmine API key (found in My Account > API access key)
5. **Step 2 - Defaults**: Select default values from dropdown menus (automatically fetched from your Redmine instance):
   - **Default Project**: Project to use when not specified in action calls
   - **Default Tracker**: Tracker to use by default (e.g., Bug, Feature)
   - **Default Priority**: Priority to use by default

## Usage

### Action: `redmine.create_issue`

Create a new issue in Redmine.

| Field | Required | Description |
|-------|----------|-------------|
| `subject` | Yes | Issue title |
| `project_id` | No | Project identifier (uses default if not specified) |
| `description` | No | Issue description (supports templates) |
| `tracker_id` | No | Tracker ID (uses default if not specified) |
| `priority_id` | No | Priority ID (1=Low, 2=Normal, 3=High) |

### Example Automations

**Create issue when salt level is low:**

```yaml
automation:
  - alias: "Low salt alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.salt_level
        below: 15
    action:
      - service: redmine.create_issue
        data:
          subject: "Buy salt for desalination unit"
          description: "Salt level dropped below 15%. Current level: {{ states('sensor.salt_level') }}%"
          priority_id: 3
```

**Create issue when washer is done:**

```yaml
automation:
  - alias: "Washer done reminder"
    trigger:
      - platform: state
        entity_id: sensor.washer_state
        to: "idle"
        from: "running"
    action:
      - service: redmine.create_issue
        data:
          subject: "Move laundry to dryer"
          project_id: "household-tasks"
          priority_id: 2
```

**Create issue from a button press:**

```yaml
automation:
  - alias: "Report broken appliance"
    trigger:
      - platform: device
        device_id: your_button_device_id
        type: single
    action:
      - service: redmine.create_issue
        data:
          subject: "Appliance needs repair"
          description: "Reported via button press at {{ now() }}"
          tracker_id: 2
```

## Finding Your API Key

Log into Redmine > My Account > API access key (right sidebar)

Note: Projects, trackers, and priorities are automatically discovered from your Redmine instance during setup.

## Troubleshooting

### Connection Failed
- Verify the Redmine URL is accessible from your Home Assistant instance
- Ensure the URL includes the protocol (http:// or https://)
- Check if Redmine API is enabled (Administration > Settings > API)

### Invalid API Key
- Regenerate your API key in Redmine (My Account > API access key)
- Ensure the API key has permissions for the projects you want to access

### Issue Creation Failed
- Verify the project_id exists and you have permission to create issues
- Check that the tracker_id and priority_id are valid for your Redmine instance

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
