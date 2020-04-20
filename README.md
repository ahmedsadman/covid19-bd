# Covid-19 Bangladesh: District-wise data

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

This is a REST-based public API for accessing district-wise data for Covid-19 in Bangladesh. This data is periodically pulled from the IEDCR reports, which is generally published after evening in Bangladesh (UTC+6) time.

## Usage Permissions

As it is public API, you're free to use it for your projects. In your work, you must explicitly provide credits and also a link to this repository - this would be more than enough for most of you folks. For more detailed information please check LICENSE file.

## Documentation

It's pretty simple for now, you just have to hit the following URL to get the latest data:

```
https://corona-bd.herokuapp.com/district
```

The success response returns data in the following format:

```
data: [
    ...
    {
        id: 1,
        name: "Dhaka",
        count: 700,
        prev_count: 600
    }
    ...
]
```

The `prev_count` (previous count) keeps track of the last record before updating to the new counts

More features such as area-wise report for Dhaka city might be added later

## Development

Feel free to contribute and make the API for feature-rich. For this to work, you have to have the following Buildpacks:

-   Python
-   Java (required by some dependencies)

Install the Python requirements `pip install -r requirements.txt` and you're good to go.
