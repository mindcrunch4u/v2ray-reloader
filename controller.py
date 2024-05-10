import json
import signal
import sys
import time
import os
import traceback
from datetime import datetime
from subprocess import Popen, PIPE, STDOUT
from fetcher import build_curl_command, fetch_base64_config_list, convert_base64_list_to_json_list, load_template, load_indexed_config_to_memory
from configuration import default_config

controller_log_file = "./log_controller_file.txt"

def find_v2ray_pids():
    pid_list = []
    command = "ps -A | grep v2ray | awk -F ' ' '{print $1}'"
    process = Popen(command , stdout=PIPE, stderr=STDOUT, shell=True)
    with process.stdout:
        for line in iter(process.stdout.readline, b''): # b'\n'-separated lines
            decoded_line = ""
            try:
                decoded_line = line.decode()
            except:
                decoded_line = str(line)
            pid_list.append(decoded_line.strip())
    exitcode = process.wait()
    return pid_list


def start_v2ray_daemon(configuration_path, log_file_path=None):
    if not log_file_path:
        log_file_path = "log_{}_file.txt".format(os.path.basename(configuration_path))
    command = "nohup {} run -c {} 2>&1 >> {} &".format(
            default_config.v2ray_binary_path,
            configuration_path,
            log_file_path)
    if default_config.verbose:
        print(command)
    # if the controller.py script exists, then its children processes (v2ray) will also be killed
    os.system(command)


def kill_pids(pid_list):
    for pid in pid_list:
        if default_config.verbose:
            print("Kill: {}".format(pid))
        os.kill(int(pid), signal.SIGKILL)


def is_proxy_valid():
    curl_command = build_curl_command(
            default_config.connectivity_check_proxy,
            default_config.connectivity_check_url)
    process = Popen(curl_command , stdout=PIPE, stderr=STDOUT, shell=True)
    exitcode = process.wait()
    return exitcode == 0


def refresh_configuration():

    curl_proxy = default_config.subscription_fetch_proxy
    curl_target = default_config.subscription_url
    curl_command = build_curl_command(curl_proxy, curl_target)
    base64_list = fetch_base64_config_list(curl_command)
    if len(base64_list) == 1 and len(base64_list[0]) == 0:
        print("Cannot fetch configurations from url.")
        sys.exit(1)

    json_list = convert_base64_list_to_json_list(base64_list)

    if default_config.verbose:
        for index, dict_item in enumerate(json_list):
            print("Retrieved Configuration: {}".format(index))
            for dict_key in dict_item:
                print("\t{}: {}".format(dict_key, dict_item[dict_key]))

    template_dict = default_config.template_dict
    for template_key in template_dict:
        print("Handling {}".format(template_key))
        v2ray_vnext_index = template_dict[template_key]["v2ray_vnext_index"]
        output_file       = template_dict[template_key]["output_file"]
        server_index      = template_dict[template_key]["server_index"]
        res = ""
        try:
            if server_index == None:
                # use the original configuration
                # donot update it with the retrieved proxies
                with open(template_key, "r") as f:
                    res = f.read()
            else:
                template = load_template(template_key)
                res = load_indexed_config_to_memory(template, json_list, 
                                                    server_index, v2ray_vnext_index)
                res = str(json.dumps(res, indent=2))

            if output_file == None:
                # edit in-place
                with open(template_key, "w") as f:
                    f.write(res)
            else:
                with open(output_file, "w") as f:
                    f.write(res)
            # in-place update default_config member
            template_dict[template_key]["successful"] = True
        except Exception:
            print("\tError Occurred:")
            print("\t\t{}:{}".format(template_key, template_dict[template_key]))
            for line in traceback.format_exc().split(os.linesep):
                print("\t\t{}".format(line.strip()))
            # in-place update default_config member
            template_dict[template_key]["successful"] = False


def main():

    def start_all_refreshed_configs():
        # restart all successfully refreshed configuration
        template_dict = default_config.template_dict
        for item in template_dict:
            if template_dict[item]["successful"] == False:
                continue
            elif template_dict[item]["output_file"] == None:
                start_v2ray_daemon(item)
            elif template_dict[item]["output_file"] != None:
                start_v2ray_daemon(template_dict[item]["output_file"])

    def refresh_and_restart_configs():
        refresh_configuration()
        pid_list = find_v2ray_pids()
        kill_pids(pid_list)
        start_all_refreshed_configs()


    refresh_and_restart_configs()
    time.sleep(5) # allow v2ray to fully start
    while True:
        if is_proxy_valid():
            print("Proxy Check Passed.")
            time.sleep(default_config.wait_time_default)
            continue
        else:
            print("Proxy Check Failed. Refreshing ...")
            with open(controller_log_file, "a+") as log:
                logstring = "Failed At: {}".format(datetime.now().strftime("%m/%d/%Y  %H:%M:%S"))
                log.write(logstring + os.linesep)
            refresh_and_restart_configs()
            time.sleep(default_config.wait_time_impatient)

if __name__ == "__main__":
    main()
