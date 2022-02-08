# Covid-19 Bangladesh: District-wise data

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

> **NOTICE: This project is no longer maintained**

This is a public REST API for accessing district-wise data and daily stats for Covid-19 in Bangladesh. This data is periodically pulled from the IEDCR reports, which is generally published after evening in Bangladesh (UTC+6) time. Stats are pulled from official government website for Corona.

## Usage Permissions

As it is public API, you're free to use it for your projects. In your work, you must explicitly provide credits and also a link to this repository. For more detailed information please check LICENSE file.

## Documentation

### Caching

Developers should cache the last successful response. Because the server will be occassionally disabled to save minutes of free-tier Heroku dyno. If I get enough support, I will be able to migrate to a premium server and thus eliminate this issue.

### Stats

> GET: https://corona-bd.herokuapp.com/stats

The success response returns data (JSON) in the following format:

```
{
    "death": {
        "last24": 4,
        "total": 131
    },
    "positive": {
        "last24": 503,
        "total": 4689
    },
    "recovered": {
        "last24": 191,
        "total": 2101
    },
    "test": {
        "last24": 4,
        "total": 112
    },
    "updated_on": "Fri, 24 Apr 2020 18:20:59 GMT"
}

```

The field `updated_on` shows time in UTC/GMT

### District Counts

> GET: https://corona-bd.herokuapp.com/district

The success response returns data (JSON) in the following format:

```
{
    "data": [
        ...
        {
            "id": 1,
            "name": "Dhaka",
            "count": 700,
            "prev_count": 600
        }
        ...
    ],
    "updated_on": "Fri, 24 Apr 2020 18:20:59 GMT"
}
```

> **WARNING**: Do not depend on the `id` field, as it might change over time. You're advised to work with `name` directly.

The `prev_count` (previous count) keeps track of the last record before updating to the new counts. The `updated_on` field is recorded based on UTC time (not Bangladesh time which is UTC+6)

More features such as area-wise report for Dhaka city might be added later

## Development

Feel free to contribute and make the API feature-rich. For this to work, you have to have Python buildpack.

Install the Python requirements `pip install -r requirements.txt` and you're good to go. You also have to set some environment variables in `.env` file in the root directory. Please check the `provider` module to know more about these variables.

## Donate

Currently this service is hosted in free servers. To provide uninterrupted service, I need to migrate to a premium plan and also buy a domain.

Many of you are using this service. If you can contribute I will be grateful from the bottom of my heart. I have calculated that I would need around 8\$ per month to bear the server costs. Just click the button below to donate.

<a href="https://www.buymeacoffee.com/ahmedsadman" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174"></a>

If you want to donate using some local payment gateways like bKash, just drop an email at ahmedsadman.211@gmail.com.
