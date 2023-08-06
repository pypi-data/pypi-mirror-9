"""
Flash LEDS of the router(s).
"""

import argparse
import sys
import time

MIN_FLASH_DELAY = 0.200

parser = argparse.ArgumentParser(add_help=False)


def command(api, args, routers=None):
    ids = []
    print("Flashing LEDS for:")
    for rinfo in routers:
        print("    %s (%s)" % (rinfo['name'], rinfo['id']))
        ids.append(rinfo['id'])
    rfilter = {
        "id__in": ','.join(ids),
        "timeout": 0
    }
    leds = dict.fromkeys((
        "LED_ATTENTION",
        "LED_SS_1",
        "LED_SS_2",
        "LED_SS_3",
        "LED_SS_4"
    ), 0)
    print()
    while True:
        for k, v in leds.items():
            leds[k] = state = not v
        start = time.time()
        api.put('remote/control/gpio', leds, **rfilter)
        print("\rLEDS State: %s" % ('ON ' if state else 'OFF'), end='')
        sys.stdout.flush()
        time.sleep(max(0, MIN_FLASH_DELAY - (time.time() - start)))
