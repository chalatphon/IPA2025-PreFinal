import os
import re # Import regular expressions
import subprocess
from ruamel.yaml import YAML # *** เพิ่ม: import ruamel.yaml ***

# *** แก้ไข: ย้ายตัวแปรที่ใช้ร่วมกันมาไว้ข้างบนเป็นค่าคงที่ ***
INVENTORY_FILE = 'hosts'
HOSTNAME_TO_UPDATE = 'CSR1kv' #
PLAYBOOK_MOTD = 'playbook_motd.yaml'

def changehost(ip):
    """
    Overwrites the 'hosts' file by replacing the IP in 'ansible_host=...'
    with the new IP.
    """
    try:
        # 1. อ่านเนื้อหาไฟล์ hosts เดิม
        with open(INVENTORY_FILE, 'r') as f:
            lines = f.readlines()

        new_lines = []
        
        # 2. ค้นหาบรรทัดที่มี 'ansible_host=' และแทนที่ IP
        for line in lines:
            new_line = re.sub(
                r'ansible_host=\S+',      # Pattern ที่จะค้นหา
                f'ansible_host={ip}',     # ข้อความที่จะแทนที่
                line                      
            )
            new_lines.append(new_line)

        # 3. เขียนทับไฟล์ hosts ด้วยเนื้อหาใหม่
        with open(INVENTORY_FILE, 'w') as f:
            f.writelines(new_lines)
        
        print(f"Successfully updated {INVENTORY_FILE} with new IP {ip}")
        return True # คืนค่าว่าสำเร็จ

    except FileNotFoundError:
        print(f"Error: Inventory file '{INVENTORY_FILE}' not found.")
        return False
    except Exception as e:
        print(f"Error writing to inventory file: {e}")
        return False

def showrun(ip):
    """
    Calls changehost() to update the IP, then runs 'playbook.yaml'.
    """
    if not changehost(ip):
        return {"status": "FAIL", "msg": "Error: Ansible (Could not update hosts file)"}

    try:
        command = ['ansible-playbook', 'playbook.yaml', '-i', INVENTORY_FILE] #
        result = subprocess.run(command, capture_output=True, text=True)
        run_stdout = result.stdout
        print(run_stdout)
        
        if 'failed=0' in run_stdout and 'unreachable=0' in run_stdout:
            return {"status": "OK", "msg":"ok", "hostname": HOSTNAME_TO_UPDATE}
        else:
            return {"status": "FAIL", "msg":"Error: Ansible (Playbook failed)"}

    except Exception as e:
        print(f"Error running subprocess: {e}")
        return {"status": "FAIL", "msg": f"Error: Ansible (Subprocess failed: {e})"}
    

# *** เพิ่ม: ฟังก์ชัน Helper ใหม่สำหรับเขียนทับ YAML ***
def _overwrite_playbook_motd_text(motd_text):
    """
    Internal function to overwrite the 'text' field in playbook_motd.yaml
    using ruamel.yaml to preserve formatting.
    """
    yaml = YAML()
    yaml.preserve_quotes = True
    
    try:
        with open(PLAYBOOK_MOTD, 'r') as f:
            data = yaml.load(f)
        
        # เข้าถึง text:
        # data[0] คือ Play แรก
        # ['tasks'][0] คือ Task แรก
        # ['cisco.ios.ios_banner']['text'] คือ key ที่เราต้องการ
        data[0]['tasks'][0]['cisco.ios.ios_banner']['text'] = motd_text
        
        with open(PLAYBOOK_MOTD, 'w') as f:
            yaml.dump(data, f)
        
        print(f"Successfully overwrote {PLAYBOOK_MOTD} with new text.")
        return True
    except Exception as e:
        print(f"Error overwriting YAML file {PLAYBOOK_MOTD}: {e}")
        return False


# *** แก้ไข: ฟังก์ชัน confmotd ให้รับ motd_text ***
def confmotd(ip, motd_text):
    """
    Calls _overwrite_playbook_motd_text() and changehost(), 
    then runs 'playbook_motd.yaml'.
    """
    # 1. เขียนทับ MOTD text ในไฟล์ .yaml ก่อน
    if not _overwrite_playbook_motd_text(motd_text):
        return {"status": "FAIL", "msg": "Error: Ansible (Could not overwrite playbook_motd.yaml)"}

    # 2. เรียกฟังก์ชันเปลี่ยน IP
    if not changehost(ip):
        return {"status": "FAIL", "msg": "Error: Ansible (Could not update hosts file)"}

    # 3. รัน Playbook ที่แก้ไขแล้ว
    try:
        command = ['ansible-playbook', PLAYBOOK_MOTD, '-i', INVENTORY_FILE]
        result = subprocess.run(command, capture_output=True, text=True)
        run_stdout = result.stdout
        print(run_stdout)
        
        if 'failed=0' in run_stdout and 'unreachable=0' in run_stdout:
            return {"status": "OK", "msg":"ok", "hostname": HOSTNAME_TO_UPDATE}
        else:
            return {"status": "FAIL", "msg":"Error: Ansible (Playbook failed)"}

    except Exception as e:
        print(f"Error running subprocess: {e}")
        return {"status": "FAIL", "msg": f"Error: Ansible (Subprocess failed: {e})"}
    
if __name__ == "__main__":
    # ทดสอบ confmotd
    response = confmotd("10.0.15.63", "This is a test from __main__") 
    print("Function response (confmotd):", response)
    
    # ทดสอบ showrun
    response_show = showrun("10.0.15.63")
    print("Function response (showrun):", response_show)