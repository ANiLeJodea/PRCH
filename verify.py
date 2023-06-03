# Python default packages
import time
import os
from concurrent.futures import ThreadPoolExecutor

# External packages
import requests

# Project packages
from helpers import exc_to_str, form_an_output

def verify_proxy_on_ipinfo(
        proxy_data: str, timeout: float
) -> tuple[bool, str, str]:
    try:
        r = requests.get(
            "https://ipinfo.io/ip", proxies={"http": proxy_data, "https": proxy_data}, timeout=timeout
        )
        time_taken = round(r.elapsed.total_seconds(), 4)
        if r.status_code == 200:
            if r.text in proxy_data:
                return True, f"Fully worked;Time taken: {time_taken};Showed a p ip: {r.text}", proxy_data
            return False, f"Worked;Time taken: {time_taken};Didnt show a p ip. THIS_IP: {os.environ['THIS_IP']}\n" \
                          f"r.text: {r.text}", proxy_data
        return False, f"Didnt work;Time taken: {time_taken};Invalid r.status_code: {r.status_code}", proxy_data

    except Exception as e:
        return False, f"Didnt work;Got an exception;{exc_to_str(e, title='')}", proxy_data

def verify_proxy_on_site_list(
        proxy_ip_port: str, timeout: float, site_list: list, delay_between: int = 0
) -> dict:
    test_results = {}
    proxies_data = {"http": proxy_ip_port, "https": proxy_ip_port}
    for site in site_list:
        try:
            r = requests.get(site, proxies=proxies_data, timeout=timeout)
            time_taken = round(r.elapsed.total_seconds(), 4)
            if r.status_code == 200:
                test_results[site] = (True, f"Fully worked;Time taken: {time_taken}")
            else:
                test_results[site] = (False, f"Didnt work;Time taken: {time_taken};"
                                             f"Invalid r.status_code: {r.status_code}")
        except Exception as e:
            test_results[site] = (False, f"Didnt work;Got an exception;{exc_to_str(e, title='')}")

        time.sleep(delay_between)

    return test_results

def check_proxies_from_document(
        checked_file_name: str, raw_file_path: str, timeout: float, mode: int,
        portion: int = 100, not_desired: bool = None
) -> tuple[bool, str]:
    try:
        path_with_date = f"{checked_file_name}_{time.strftime('%H:%M:%S %d-%m-%Y')}.txt"
        with open(raw_file_path, 'r') as fr, \
                open(checked_file_name + ".txt", 'w') as fw, \
                ThreadPoolExecutor(max_workers=portion) as executor:
            proxies = [p for p in fr.read().splitlines() if ':' in p]
            fw.write("\n\n".join(f"{proxy} -> {form_an_output(text, mode)}"
                                 for bool_result, text, proxy in
                                 executor.map(verify_proxy_on_ipinfo, proxies, [timeout] * len(proxies))
                                 if bool_result is not not_desired))

    except Exception as e:
        return False, exc_to_str(e)

    return True, path_with_date


