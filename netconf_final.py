from ncclient import manager
import xmltodict
studentID = "66070041"

def create(ip):
    m = manager.connect(
    host= ip,
    port=830,
    username="admin",
    password="cisco",
    hostkey_verify=False
    )
    netconf_config = """
    <config>
     <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
      <interface>
      <Loopback>
        <name>66070041</name>
        <description>66070041</description>
        <ip>
          <address>
            <primary>
              <address>172.0.41.1</address>
              <mask>255.255.255.0</mask>
            </primary>
          </address>
        </ip>
       </Loopback>
      </interface>
     </native>
    </config>
    """

    try:
        netconf_reply = m.edit_config(target="running",config=netconf_config)
        xml_data = netconf_reply.xml
        print(xml_data)
        if '<ok/>' in xml_data:
            return "Interface loopback 66070041 is created successfully using Netconf"
    except:
        return f"Cannot create: Interface loopback {studentID} using Netconf"

def delete(ip):
    m = manager.connect(
    host= ip,
    port=830,
    username="admin",
    password="cisco",
    hostkey_verify=False
    )
    current_status = status(ip) 
    if "No Interface" in current_status:
        return f"Cannot delete: Interface loopback {studentID} using Netconf"
    netconf_config = """
    <config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
     <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
      <interface>
        <Loopback xc:operation="delete">
            <name>66070041</name>
        </Loopback>
     </interface>
     </native>
    </config>
    """

    try:
        netconf_reply = m.edit_config(target="running",config=netconf_config)
        xml_data = netconf_reply.xml
        print(xml_data)
        if '<ok/>' in xml_data:
            return "Interface loopback 66070041 is delete successfully using Netconf"
    except:
        return f"Cannot delete: Interface loopback {studentID} using Netconf"
def disable(ip):
    current_status = status(ip) 
    if "No Interface" in current_status:
        return f"Cannot shutdown: Interface loopback {studentID} using Netconf"
    
    m = manager.connect(
    host= ip,
    port=830,
    username="admin",
    password="cisco",
    hostkey_verify=False
    )
    
    netconf_config = """
    <config>
     <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
      <interface>
       <Loopback>
        <name>66070041</name>
        <shutdown/>
       </Loopback>
      </interface>
     </native>
    </config>
    """

    try:
        netconf_reply = m.edit_config(target="running",config=netconf_config)
        xml_data = netconf_reply.xml
        print(xml_data)
        if '<ok/>' in xml_data:
            return "Interface loopback 66070041 is disable successfully using Netconf"
    except:
        return f"Cannot shutdown: Interface loopback {studentID} using Netconf"

def enable(ip):
    m = manager.connect(
    host= ip,
    port=830,
    username="admin",
    password="cisco",
    hostkey_verify=False
    )
    netconf_config = """
    <config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
     <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
      <interface>
       <Loopback>
        <name>66070041</name>
        <shutdown xc:operation="delete"/>
       </Loopback>
      </interface>
     </native>
    </config>
    """

    try:
        netconf_reply = m.edit_config(target="running",config=netconf_config)
        xml_data = netconf_reply.xml
        print(xml_data)
        if '<ok/>' in xml_data:
            return "Interface loopback 66070041 is enable successfully using Netconf"
    except:
        return f"Cannot enable: Interface loopback {studentID} using Netconf"


def status(ip):
    m = None 
    
    # *** นี่คือ Filter ที่แก้ไขแล้ว ***
    netconf_filter = f"""
    <filter>
      <interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
          <name>Loopback{studentID}</name> 
        </interface>
      </interfaces-state>
    </filter>
    """

    try:
        print(f"Connecting to {ip} for STATUS...")
        m = manager.connect(
            host=ip,
            port=830,
            username="admin",
            password="cisco",
            hostkey_verify=False,
            device_params={'name': 'iosxe'} 
        )
        print("Connection successful!")

        netconf_reply = m.get(filter=netconf_filter)
        print("Reply received.")

        # 1. แปลง XML เป็น Dictionary
        data_dict = xmltodict.parse(netconf_reply.data_xml)


        if "data" not in data_dict or not data_dict["data"] or "interfaces-state" not in data_dict["data"]:
             print("Interface not found or no state data returned.")
             return f"No Interface Loopback{studentID} found."
        interface_data = data_dict["data"]["interfaces-state"]["interface"]
        admin_status = interface_data["admin-status"]
        oper_status = interface_data["oper-status"]
        if admin_status == 'up' and oper_status == 'up':
            return f"Interface loopback {studentID} is enabled (checked by Netconf)"
        elif admin_status == 'down' and oper_status == 'down':
            return f"Interface loopback {studentID} is disabled (checked by Netconf)"
    except:
        return f"Undefined Error"

