from fetcher import build_curl_command, fetch_base64_config_list, convert_base64_list_to_json_list, load_template, load_indexed_config_to_memory
from configuration import default_config

def main():

    curl_proxy = default_config.subscription_fetch_proxy
    curl_target = default_config.subscription_url
    curl_command = build_curl_command(curl_proxy, curl_target)
    base64_list = fetch_base64_config_list(curl_command)

    json_list = convert_base64_list_to_json_list(base64_list)

    if default_config.verbose:
        for index, dict_item in enumerate(json_list):
            print("Retrieved Configuration: {}".format(index))
            for dict_key in dict_item:
                print("\t{}: {}".format(dict_key, dict_item[dict_key]))

    template_dict = default_config.template_dict
    for template_key in template_dict:
        try:
            template = load_template(template_key)
            res = load_indexed_config_to_memory(template, json_list, template_dict[template_key]["server_index"])
            res = str(json.dumps(res, indent=2))
            config_path = template_dict[template_key]["output_file"]
            with open(config_path, "w") as f:
                f.write(res)
        except Exception as e:
            print(e)
            print("\t{}:{}".format(template_key, template_dict[template_key]))

if __name__ == "__main__":
    main()
