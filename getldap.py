#!/usr/bin/env python3
# 
# NAME: Ldap Tool Script
# DESC: Script to get an ldif from an LDAP Directory where uids are filtered by CSV file
# AUTHOR: Florentin PERRIER
# VERSION: 1.0

from ldap3 import Server, Connection, ALL
from ldap3.core.exceptions import LDAPSocketOpenError
from argparse import ArgumentParser
import csv
import os.path

class pcolors:
    ERROR = '\033[91m'
    WARNING = '\033[93m'
    CYAN = '\033[96m'
    END = '\033[0m'
    GREEN = '\033[92m'
    BOLD = '\033[1m'

def hello ():
    print("LDAP TOOL SCRIPT")
    print("Transfert from LDAP to LDIF")

def info(msg):
    print("[INFO] " + pcolors.CYAN + msg + pcolors.END)
def warn (msg):
    print("[WARNING] " + pcolors.WARNING + msg + pcolors.END)
def error (msg):
    print("[ERROR] " + pcolors.ERROR + msg + pcolors.END)

def getFilter(file):
    uids=[]
    with open(file) as csvfile:
        reader=csv.reader(csvfile, delimiter=';')
        i=None
        for row in reader:
            if(i is None):
                i=row.index('login')
            else:
                uids.append(row[i])
    return uids

def ldapToLdif(url,dn,password,filter,out):
    
    ldif="version: 1\n"
    
    try:
        file=open(out, "x")
        file.write(ldif)

        srv = Server(url, get_info=ALL)
        conn = Connection(srv, dn, password)
        conn.bind()

        cok=0
        cwarn=0

        if (filter == []):
            file.write("# Nothing to show")
        else:
            for uid in filter:
                conn.search('OU=people,DC=agroparistech,DC=FR','(uid='+uid+')',attributes = ['*'])
                tmp=conn.response_to_ldif()
                for line in tmp.splitlines():
                    if "version:" in line:
                        tmp=tmp.replace(line,'')
                    elif "# total number of entries: 1" in line:
                        tmp=tmp.replace(line,'')
                if(len(tmp.splitlines())>5):
                    info("UID="+uid+": OK")
                    cok=cok+1
                else:
                    warn("UID="+uid+": ??")
                    cwarn=cwarn+1
                file.write(tmp)
        
        print('\n'+pcolors.BOLD+pcolors.GREEN+"Ok: "+str(cok)+pcolors.WARNING+"\nWarn: "+str(cwarn)+pcolors.END+pcolors.BOLD+"\nTotal: "+str(cok+cwarn)+pcolors.END+'\n')

        file.close()

    except FileExistsError:
        error("Le fichier "+out+" existe déjà")
        exit(1)
    except LDAPSocketOpenError:
        error("Le script n'arrive pas à se connecter au serveur LDAP")
        if (os.path.isfile(out)):
            os.remove(out)
        exit(1)

def run(args):

    out="out.ldif"

    if(args.ldap_to_ldif is None):
        error("--ldap-to-ldif necessary")
        exit(1)
    if(args.out is not None):
        out=args.out

    hello()
    ldapToLdif(args.ldap_to_ldif[0],args.ldap_to_ldif[1],args.ldap_to_ldif[2], getFilter(args.filter), out)
    info(out+" saved!\n[END]")
    exit(0)

parser = ArgumentParser(description="By Florentin PERRIER\nv1.0.0")
parser.add_argument('--ldap-to-ldif', nargs=3, metavar=("HOST_URL", "DN", "PASSWORD"),help="Get entity from ldap directory server.\nHost URL can be: - ldap[s]://HOSTNAME.DOMAIN:PORT")
parser.add_argument('-f','--filter', metavar="CSV_FILE_IN", help="Filtre UID uniquement ! Nécessite un fichier CSV : Délimiteur ';' , Une colonne avec comme 1ere valeur le mot login suivi de tout les uid.")
parser.add_argument('-o', '--out', metavar='OUT_FILE', help='Specify output file (For --X-to-ldif) - default: out.ldif')
args = parser.parse_args()

run(args)





