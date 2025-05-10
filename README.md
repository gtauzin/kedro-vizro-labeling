# Kedro Vizro Labeling

[![Powered by Kedro](https://img.shields.io/badge/powered_by-kedro-ffc900?logo=kedro)](https://kedro.org)

This repository is a WIP example project integrating [Vizro](https://vizro.mckinsey.com/) into [Kedro](https://kedro.org/) for creating a time-series labeling dashboard.

## Running the Dashboard

This project uses [uv](https://docs.astral.sh/uv/) for packaging, and managing dependencies and environments.
To install it, follow the [uv installation instructions](https://docs.astral.sh/uv/getting-started/installation/).

To run the dashboard, you can do:

```bash
uv run --extra dashboards src/kedro_vizro_labeling/dashboards/iris/app.py
```

and connect to the dashboard on [http://127.0.0.1:8050](http://127.0.0.1:8050/).

You may user the following credentials to connect:

```bash
Username=user1
Password=user1
```

or

```bash
Username=admin1
Password=admin1
```

where `user_1` has the `Viewer` group permissions and `admin_1` has both the `Viewer` and `Admin` permissions.

If you click, on the "Show histogram" button with only the `Viewer` permissions, it will open a Modal and you won't see the histogram.
