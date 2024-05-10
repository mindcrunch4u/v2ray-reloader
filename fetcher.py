from configuration import default_config
import shlex
import json
import subprocess
import base64
import sys
import copy
import os

curl_proxy = default_config.subscription_fetch_proxy
curl_target = default_config.subscription_url

def build_curl_command(curl_proxy, curl_target):
# make sure that cURL has Silent mode (--silent) activated
# otherwise we receive progress data inside err message later
    if curl_proxy and len(curl_proxy.strip()) > 0:
        # has proxy
        curl_command = r"""curl -x {} --silent {}""".format(curl_proxy, curl_target)
    else:
        # no proxy configured
        curl_command = r"""curl --silent {}""".format(curl_target)
    return curl_command

def load_template(template_path):
    ret = None
    with open(template_path, "r") as f:
        ret = json.load(f)
    return ret

def fetch_base64_config_list(cURL):
    lCmd = shlex.split(cURL) # Splits cURL into an array
    p = subprocess.Popen(lCmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate() # Get the output and the err message
    coded_string = out.decode("utf-8")
    decoded_strings = base64.b64decode(coded_string).decode("utf-8")
    decoded_string_list = decoded_strings.split("vmess://")
    return decoded_string_list

def convert_base64_list_to_json_list(base64_string_list):
    list_of_json = []
    for item in base64_string_list:
        item = item.strip()
        if item == "":
            continue
        try:
            item = base64.b64decode(item + '==').decode("utf-8")
            json_data = json.loads(item)
        except:
            continue
        list_of_json.append(json_data)
    return list_of_json

def load_indexed_config_to_memory(template_dict, list_of_json, server_index, v2ray_at_index=1):

    config_in_memory = copy.deepcopy(template_dict)
    var_address = list_of_json[server_index]['add']
    var_port = list_of_json[server_index]['port']
    var_id = list_of_json[server_index]['id']

    config_in_memory["outbounds"][v2ray_at_index]['settings']['vnext'][0]['address'] = var_address
    config_in_memory["outbounds"][v2ray_at_index]['settings']['vnext'][0]['port'] = int(var_port)
    config_in_memory["outbounds"][v2ray_at_index]['settings']['vnext'][0]['users'][0]['id'] = var_id

    if default_config.verbose:
        print("Loaded: {} - {} - {}".format(var_address, var_port, var_id))

    return config_in_memory

def main():
    print("Stage 1 ------------------")
    print("base64-encoded config list received:")
    curl_command = build_curl_command(curl_proxy, curl_target)
    base64_list = fetch_base64_config_list(curl_command)
    print(base64_list)
    print("Stage 2 ------------------")
    print("converted to json-encoded config list:")
    json_list = convert_base64_list_to_json_list(base64_list)
    print(json_list)
    print("Stage 3 ------------------")
    print("generating config files using templates:")

    print("RAW")
    template_path = "./template_raw_first.json"
    template = load_template(template_path)
    res = load_indexed_config_to_memory(template, json_list, 0, v2ray_at_index=0)
    res = str(json.dumps(res, indent=2))
    config_path = "./tmp_first.json"
    with open(config_path, "w") as f:
        f.write(res)

    print("US")
    template_path = "./template_us.json"
    template = load_template(template_path)
    res = load_indexed_config_to_memory(template, json_list, 1)
    res = str(json.dumps(res, indent=2))
    config_path = "./tmp_second.json"
    with open(config_path, "w") as f:
        f.write(res)

    print("DE")
    template_path = "./template_de.json"
    template = load_template(template_path)
    res = load_indexed_config_to_memory(template, json_list, 2)
    res = str(json.dumps(res, indent=2))
    config_path = "./tmp_third.json"
    with open(config_path, "w") as f:
        f.write(res)

if __name__ == '__main__':
    main()
    sys.exit()

