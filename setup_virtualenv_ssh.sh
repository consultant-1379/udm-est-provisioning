#!/bin/bash
rm -rf venv/e3tools-ansible2.6.2
virtualenv -p python3.6 venv/e3tools-ansible2.6.2
echo $PWD
activate () {
    . $PWD/venv/e3tools-ansible2.6.2/bin/activate
}
activate
#source venv/e3tools-ansible2.6.2/bin/activate
pip install --upgrade pip && pip install -r requirements_ssh.txt
