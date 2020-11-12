import sys
import argparse
import json
import base64

from admin import add_credential, add_provider_device, set_db , add_dog_breeds

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', action='store', help='json file to load db entities from')

    args = parser.parse_args()

    with open(args.data, 'r') as f:
        data = json.load(f)

    set_db()

    for u in data['users']:
        add_credential(u['email'], u['password'])

    for p in data['providerdevice']:
        add_provider_device(p['device_name'], p['memory_limit'], p['net_limit'],p['cpu_limit'],
                            p['up_time_limit'], p['cpu_price'],p['ram_price'], p['net_price']  )


         
