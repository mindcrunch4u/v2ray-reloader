import os
import sys

class DefaultConfiguration:
    def __init__(self):
        self.v2ray_binary_path="./v2ray"
        self.template_dict=dict()
        self.subscription_url=""
        self.subscription_fetch_proxy=""

default_config = DefaultConfiguration()
try:
    default_config.subscription_url = os.environ["V2RAY_SUB_URL"]
except:
    print("export your subscription url and then run the script.")
    print("export V2RAY_SUB_URL=\"...\"")
    sys.exit(1)

# { "output_file":None, "server_index":None } means that the configuration file doesnt not need to be touched, and a v2ray instance should be run directly usin this configuration
# { "output_file":"copy.json", "server_index":None } means that the configuration should be copied to "copy.json" and a v2ray instance should run using "copy.json"
# { "output_file":None, "server_index":3 } means that the configuration should be modified in-place, and a v2ray instance shold be run using the template itself.

# when there are multiple vnext (proxy chain), then update v2ray_vnext_index to match your setup.

default_config.template_dict["./template_A.json"] = {"v2ray_vnext_index": 0, "output_file":"output_A.json", "server_index":0}
default_config.template_dict["./template_B.json"] = {"v2ray_vnext_index": 1, "output_file":"output_B.json", "server_index":3}
default_config.template_dict["./template_C.json"] = {"v2ray_vnext_index": 0, "output_file":None, "server_index":None}
default_config.template_dict["./template_C.json"] = {"v2ray_vnext_index": 0, "output_file":"copy_of_C.json", "server_index":None}
default_config.template_dict["./template_D.json"] = {"v2ray_vnext_index": 0, "output_file":"error.json", "server_index":999}

default_config.verbose = True
default_config.subscription_fetch_proxy = "http://10.10.0.21:59001"
default_config.connectivity_check_proxy = "http://127.0.0.1:59001"
default_config.connectivity_check_url = "https://google.com"

# wait_time_default:
#   <= 0: no proxy check
#   >  0: sleep for n seconds before proxycheck
#   avoid setting the wait time too short (like 1 second),
#   allow v2ray to start which takes a few seconds.
default_config.wait_time_default = 60 # seconds
default_config.wait_time_impatient = 20
default_config.v2ray_binary_path = "./v2ray"

for item in default_config.template_dict:
    default_config.template_dict[item]["successful"] = False
