# Database Migration Instructions

## New Fields Added

### accounts.User Model
- `year_level` - CharField (choices: 1, 2, 3, 4)
- `date_of_birth` - DateField (for age calculation)

### wellness.Alert Model
- `severity` - CharField (choices: critical, high, medium, low)

## Run Migrations

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

## Update Existing Data (Optional)

After running migrations, you may want to update existing records:

```python
# In Django shell (python manage.py shell)
from wellness.models import Alert

# Set default severity for existing alerts
Alert.objects.filter(severity__isnull=True).update(severity='medium')
```

## Notes
- All new fields have default values or are nullable
- Existing data will not be affected
- Year level and date of birth are optional for users
- Alert severity defaults to 'medium' for new alerts
