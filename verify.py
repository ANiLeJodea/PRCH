# Python default packages
import time
import os
from concurrent.futures import ThreadPoolExecutor

# External packages
import requests

# Project packages
from data import save_data as data
from helpers import exc_to_str

def verify_proxy_on_ipinfo(
        proxy_data: str
) -> tuple[bool, str, str]:
    try:
        # t = time.time()
        r = requests.get(
            "https://ipinfo.io/ip", proxies={"http": proxy_data, "https": proxy_data}, timeout=data['timeout']
        )
        # time_taken = round(time.time() - t, 4)
        time_taken = r.elapsed.total_seconds()
        if r.status_code == 200:
            if r.text in proxy_data:
                return True, f"Fully worked;Showed a pr ip: {r.text}\nTime taken: {time_taken}", proxy_data
            return False, f"Worked;Didnt show a pr ip\nthis_ip: {os.environ['THIS_IP']}" \
                          f"\nr.text: {r.text}\nTime taken: {time_taken}", proxy_data
        return False, \
               f"Didnt work;Invalid r.status_code: {r.status_code}\nTime taken: {time_taken}", \
               proxy_data

    except Exception as e:
        return False, f"Didnt work;{exc_to_str(e)}", proxy_data

def verify_proxy_on_ipinfo_w_time_time(
        proxy_data: str
) -> tuple[bool, str, str]:
    try:
        t = time.time()
        r = requests.get(
            "https://ipinfo.io/ip", proxies={"http": proxy_data, "https": proxy_data}, timeout=data['timeout']
        )
        time_taken_t = round(time.time() - t, 4)
        time_taken_r = r.elapsed.total_seconds()
        if r.status_code == 200:
            if r.text in proxy_data:
                return True, f"Fully worked;Showed a pr ip: {r.text}\nTime taken t: {time_taken_t}\nTime taken r: {time_taken_r}", proxy_data
            return False, f"Worked;Didnt show a pr ip\nthis_ip: {os.environ['THIS_IP']}" \
                          f"\nr.text: {r.text}\nTime taken t: {time_taken_t}\nTime taken r: {time_taken_r}", proxy_data
        return False, \
               f"Didnt work;Invalid r.status_code: {r.status_code}\nTime taken t: {time_taken_t}\nTime taken r: {time_taken_r}", \
               proxy_data

    except Exception as e:
        return False, f"Didnt work;{exc_to_str(e)}", proxy_data

def verify_proxy_on_site_list(
        proxy_ip: str, proxy_port: str, site_list: list, delay_between: int = 0
) -> dict:
    test_results = {}
    proxy_ip_port = f"{proxy_ip}:{proxy_port}"
    for site in site_list:
        try:
            # t = time.time()
            r = requests.get(site, proxies={"http": proxy_ip_port, "https": proxy_ip_port}, timeout=data['timeout'])

            # time_taken = round(time.time() - t, 4)
            time_taken = r.elapsed.total_seconds()
            if r.status_code == 200:
                test_results[site] = (True, f"Fully worked;Time taken: {time_taken}")
            else:
                test_results[site] = (False, f"Didnt work;Invalid r.status_code: {r.status_code}\n"
                                      f"\nTime taken: {time_taken}")
        except Exception as e:
            test_results[site] = (False, exc_to_str(e))

        time.sleep(delay_between)

    return test_results

def check_proxies_from_document(
        raw_file_path: str, portion: int = 100, condition: bool = None
) -> tuple:
    name_with_date = data['checked_file_name'] + f"_{time.strftime('%H:%M:%S %d/%m/%Y')}.txt"
    try:
        with open(raw_file_path, 'r') as fr, \
                open(data['checked_file_name'] + ".txt", 'w') as fw, \
                ThreadPoolExecutor(max_workers=portion) as executor:
            if condition is not None:
                fw.write("\n\n".join(f"{proxy} -> {text}"
                                     for bool_result, text, proxy in
                                     executor.map(verify_proxy_on_ipinfo_w_time_time, fr.read().splitlines())
                                     if bool_result is condition))
            else:
                fw.write("\n\n".join(f"{proxy} -> {text}"
                                     for bool_result, text, proxy in
                                     executor.map(verify_proxy_on_ipinfo_w_time_time, fr.read().splitlines())))
    except Exception as e:
        return e, name_with_date
    return name_with_date,


