import os
import logging
from . import VCPKG_ROOT_FOLDER, logger
from model import Port
from tools import new_template_to, temp_folder, process_port
from os import getenv

ports_dir = os.path.join(VCPKG_ROOT_FOLDER, "ports")
ports = [port for port in os.listdir(ports_dir) if os.path.isdir(os.path.join(ports_dir, port))]
num_pages = int(getenv("CONAN_TOTAL_PAGES", 10))
current_page = int(getenv("CONAN_CURRENT_PAGE", 1))

tmp_folder = temp_folder()
# tmp_folder = "./.tmp"
try:
    shutil.rmtree(tmp_folder)
except Exception:
    pass

print("Working in folder: %s" % tmp_folder)

visual_versions=[14, ]
sorted(ports)
ports.reverse()
to_upload = []

counter = 0
# Compile ports
for visual_version in visual_versions:
    for port_name in ports:
        if counter % num_pages == (current_page - 1):
            port = Port(port_name, os.path.join(ports_dir, port_name))
            ok = process_port(port, tmp_folder, visual_version)
            if ok:
                to_upload.append("%s/%s@lasote/vcpkg" % (port.name, port.version))
        counter +=1

# Upload packages
if getenv("CONAN_PASSWORD", None):
    os.system("conan user lasote -p %s" % getenv("CONAN_PASSWORD"))
    for ref in to_upload:
        ret = os.system("conan upload %s --all -r local" % str(ref))
        if ret != 0:
            raise Exception("Error uploading!")
        
