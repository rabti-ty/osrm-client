# osrm-client

Minimal client for a self-hosted [OSRM](http://project-osrm.org/) instance's `/table`
endpoint (driving distance matrix). Shared by TGSRTCEngine and MetroEngine so both talk
to the same OSRM instance through the same code, rather than each keeping its own copy.

## Usage

```python
from osrm_client import OSRMError, get_driving_distances

try:
    results = get_driving_distances(
        base_url="http://127.0.0.1:5001",
        origin_lat=17.393,
        origin_lon=78.473,
        destinations=[(17.4034712, 78.4652095)],
    )
except OSRMError as e:
    ...  # bad/unreachable base_url, malformed response, etc.

# results is one (distance_m, duration_minutes) tuple per destination, in order,
# or None for a destination OSRM couldn't route to.
```

No dependency on either app's own config/settings - the caller resolves its own
`OSRM_BASE_URL` and passes it in explicitly.

## Consuming this package

Add as a git dependency in `pyproject.toml`:

```toml
osrm-client = { git = "https://github.com/rabti-ty/osrm-client.git" }
```

then `poetry lock && poetry install`.
