import itertools
import os
import subprocess
import sys
import tempfile
import time
import client

def find_name_in_logs(log_entry):
    splices = log_entry.split('name')
    if len(splices) > 1:
        return splices[1][1:-2]

    return ''

def find_app_id_in_logs(log_entry):
    splices = log_entry.split('<parameter name="app_id">')
    if len(splices) > 1:
        return splices[1][:12]

    return ''

def process_emails(read_type):
    # read emails from gmail account
    messages = client.read_emails(read_type)

    temp = tempfile.NamedTemporaryFile('w', delete=False)
    out_file = '%s-%s.txt' % (
        'payarena' if read_type == client.READ_PAYARENA else 'npp', time.time()
    )
    out_file = os.path.join(os.path.dirname(__file__), out_file)

    with temp.file as f:
        f.write('\n###################################################\n'.join(messages))

    # grep out lines with the transaction IDs from the emails
    lines = subprocess.check_output('grep DOES %s' % temp.name, shell=True)
    os.remove(temp.name) # delete temp file

    # get the transaction IDs
    trans_id_dict = {}
    for line in lines.split('\n'):
        ids = filter(lambda s: s.startswith('['), line.split())
        if len(ids):
            for i in ids:
                trans_id_dict[i[1:-1]] = ''

    trans_ids = trans_id_dict.keys()
    if read_type == client.READ_PAYARENA:
        with open(out_file, 'w') as o:
            o.write('\n'.join(trans_ids))

        return

    # print output to file
    log_files = os.path.join(os.path.dirname(__file__), 'NetPostPay/orders.*')
    out = []
    for id_ in trans_ids:
        log_entries = subprocess.check_output('grep %s %s' % (id_, log_files), shell=True)

        if len(log_entries.split('\n')):
            log_entry = log_entries.split('\n')[0]
            out.append(' '.join([
                id_, find_app_id_in_logs(log_entry), find_name_in_logs(log_entry)
            ]))
        else:
            out.append(id_)

    with open(out_file, 'w') as o:
        o.write('\n'.join(out))

    return

if __name__ == '__main__':
    try:
        map(process_emails, [client.READ_NETPOSTPAY, client.READ_PAYARENA])
        sys.exit(0)
    except:
        # @todo: log error
        sys.exit(1)
