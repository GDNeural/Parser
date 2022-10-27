import xml.etree.ElementTree as tree
import os
import re
import shutil
import secrets


def main():

    doc = tree.parse("Sessions.xml")
    root = doc.getroot()
    cur_dir = os.getcwd()
    values = list(secrets.secret.values())
    if os.path.isdir(os.getcwd() + "\configuration"):
        shutil.rmtree(cur_dir + '\configuration')
        os.mkdir('.\configuration')
    else:
        os.mkdir('.\configuration')

    for elem in root.iter('SessionData'):
        print(elem.get('SessionId'))

        fix = elem.get('SessionId').split('/')
        i = 0
        for e in fix:
            if e == 'Imported':
                i += 1
        del fix[0:i]

        new_line = '/'.join(fix)
        print(new_line)
        elem.set('SessionId', new_line)
        ip = elem.get('Host')
        service_name = elem.get('Username')
        session = elem.get('SessionId')
        
	  if re.search("{environment_name}", session):
#Add mirror route + configure spls_config_file
            if not re.search("@", ip):
                elem.set('Host', '%s@{user_role}@%s@{mirror_ip}' % (values[0], ip))
            spsl_config = open('./configuration/%s.spsl' % service_name, 'w')
            spsl_config.write('#!/bin/spsl\nSENDLINE %s\nSLEEP 12000\nSENDLINE su %s\nSLEEP 2000'
                              '\nSENDLINE 17asurfr\nSLEEP 2000\nSENDLINE cd ~\nSLEEP 2000\nSENDLINE mgmt status'
                              % (values[1], service_name))
            spsl_config.close()
            elem.set('SPSLFileName', '%s\\configuration\\%s.spsl' % (cur_dir, service_name))
    doc.write('New_Sessions.xml')


if __name__ == "__main__":
    main();
