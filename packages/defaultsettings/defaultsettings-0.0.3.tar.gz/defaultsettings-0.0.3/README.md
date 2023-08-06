# defaultsettings - Handle settings with default for python. Serialized to JSON 
Handle settings files in python. Serialize to JSON.


## Usage
```python
import defaultsettings

# Create new settings template
settings = defaultsettings.Settings()

# Set default values
Settings.default("key", "one")
settings.default("key2", range(5))

# Save settings to file
settings.save("pathname.json")

# Load settings
settings.load("pathname.json")

# Current settings, default and loaded config
print settings.data

# Change data
settings.data["key"] = "two"

# Save config file with new data
settings.save("pathname.json")
```

