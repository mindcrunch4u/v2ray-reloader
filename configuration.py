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
default_config.subscription_fetch_proxy = "http://10.10.0.21:59001"

default_config.template_dict["./template_A.json"] = {"output_file":"output_A.json", "server_index":0}
default_config.template_dict["./template_B.json"] = {"output_file":"output_B.json", "server_index":3}
default_config.template_dict["./template_C.json"] = {"output_file":None, "server_index":None}
default_config.template_dict["./template_D.json"] = {"output_file":"error.json", "server_index":999}

default_config.verbose = True
