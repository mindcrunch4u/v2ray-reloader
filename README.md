
## Server Downtime Visualized

```
cp log_controller_file.txt visualize/
cd visualize/
python server_downtime.py
```

![server downtime](https://github.com/mindcrunch4u/v2ray-reloader/blob/main/visualize/demo.png)

## Configuration Options

All configuration options are controlled by the `default_config` object.

- `v2ray_binary_path`: where the `v2ray` binary is located.
- `subscription_url`: obtained from the exported environment variable `V2RAY_SUB_URL`, it is used to fetch v2ray configurations from the provider.
- (optional) `subscription_fetch_proxy`: obtain the v2ray configurations from the provider using this proxy, this is handy when the subscription URL is blocked by your ISP.
- `connectivity_check_url`: the controller tries to query the given URL, if the query fails, the controller will immediately refresh the configuration (from the `subscription_url`), and restart v2ray services.
- `connectivity_check_proxy`: this should point to a locally opened (proxy) port (which passes traffic to the v2ray application), the controller uses this proxy to access `connectivity_check_url`.
- `template_dict`: each dictionary entry points to a v2ray configuration.
    - the key of each entry is the path to a template file.
    - after obtaining the configurations from `subscription_url`, the template file is loaded into the memory, and the v2ray-related fields in the template are replaced by the obtained configurations.
    - if `output_file` is specified, a temporary configuration will be written to the given path, and the v2ray instance will be started using the `output_file` configuration.
    - if the `output_file` is `None`, then a v2ray instance will be started using the template configuration (the key of a dictionary entry).
    - `v2ray_vnext_index` helps the controller to locate the position of the v2ray configuration in the configuration file. Since v2ray supports chaining, a `shadowsocks --> v2ray` configuration instructs v2ray to first encrypt the packets using `shadowsocks` and then `v2ray`, in this case, the `v2ray_vnext_index` is `1`; while a `v2ray --> shadowsocks` configuration, which tells v2ray to first encrypt the packets using `v2ray` and then `shadowsocks`, means the `v2ray_vnext_index` is `0`.
    - `server_index`: there are usually multiple servers in a single subscription URL, this selects which server to use. `None` means the configuration in the template will not be updated, if an out-of-range index is used, the controller will see an error and skip this template.

For more details and how the controller works, visit [my website](https://icandothese.com/docs/tech/my_projects/#v2ray-reloader).

## Steps to Follow

1. Configure the `template_dict` dictioanry in `configuration.py`, format:

    ```
    ["path to template.json"] = {
        "v2ray_vnext_index": position of the to-be-updated v2ray entry in the template (start from 0),
        "output_file": temporary configuration generated from the template,
        "server_index": index of the server from the subscription URL (start from 0),
        }
    ```

2. Export your v2ray subscription URL: `export V2RAY_SUB_URL="..."`

3. Launch the controller script: `python controller.py`

## Using a Service File

All the logs will be stored under `/<path to>/v2ray-reloader/`.

```
# vim /etc/systemd/system/reload-config.service

[Unit]
Description=Reload Proxy Configuration Service
Wants=network-online.target
After=network-online.target

[Service]
Type=simple
WorkingDirectory=/<path to>/v2ray-reloader/
Environment="V2RAY_SUB_URL=<https URL>"
ExecStart=/usr/bin/python /<path to>/v2ray-reloader/controller.py

[Install]
WantedBy=default.target
```
