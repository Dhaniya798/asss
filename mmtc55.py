#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mmtc2_full_multi.py
Original-style script with your numbers added + support for multiple ORDER_IDs.
NETWORK ACTIONS ARE DISABLED BY DEFAULT. Toggle ENABLE_NETWORK if you fully own/are authorized.

Usage flow:
1) Pick mobile
2) (If network enabled) Trigger -> Enter OTP -> then enter ORDER_IDs one by one
3) Leave ORDER_ID blank to stop the loop

DISCLAIMER: Enable network only for accounts/systems you own or have explicit permission to act on.
"""

import socket, ssl, re, sys, json, time
from typing import Tuple, List, Dict, Optional

# ----------------- SAFETY FLAG -----------------
ENABLE_NETWORK = True  # Set True only if you're authorized.

# ------- your frequently used numbers (edit anytime) -------
COMMON_MOBILES = [
    "9713936782",
    "7064699248",
    "9576817151",
    "7447402344",
    "8338092390",
    "8769170200",
    "9602258975",
    "7436858014",
    "8594917297",
    "9752984778",
    "8827436911",
    "7909855706",
    "7436857245",
    "7436853564",
    "8338091638",
    "7038250583",
    "8432925063",
    "9569955974",
    "6388791315",
]

# ----------------- RAW REQUESTS -----------------
RAW_TRIGGER = """POST /pvt/sendOtp HTTP/1.1
Host: cem.mmtcpamp.com
Connection: close
Content-Length: 1943
sec-ch-ua-platform: "Windows"
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36
Accept: application/json
sec-ch-ua: "Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"
Content-Type: application/json
DNT: 1
sec-ch-ua-mobile: ?0
Origin: https://www.mmtcpamp.com
Sec-Fetch-Site: same-site
Sec-Fetch-Mode: cors
Sec-Fetch-Dest: empty
Accept-Encoding: gzip, deflate
Accept-Language: en-US,en;q=0.9
Cookie: _gcl_au=1.1.261478789.1759404891; _ga=GA1.1.859209797.1759404891; _fbp=fb.1.1759404903588.64898692575041071; userLoggedIn=false; _ga_9LSF6MSSDZ=GS2.1.s1759777247$o6$g0$t1759777247$j60$l0$h0; _ga_QEH5V50FP3=GS2.1.s1759777247$o6$g0$t1759777247$j60$l0$h0; _ga_M47XQM4988=GS2.1.s1759777247$o6$g0$t1759777247$j60$l0$h0; _ga_GJXHT32TQD=GS2.1.s1759777258$o6$g1$t1759777270$j48$l0$h0; _ga_RXDVTDFTJ7=GS2.1.s1759777258$o6$g1$t1759777270$j48$l0$h0

{"mobileNumber":"__MOBILE__","email":"","tncAgreeement":true,"recieveUpdates":true,"token":"0cAFcWeA5febb7yYNQUeuxAGS5MoZOPIXB89G9YSKahlqqV6qWzNePCD55Ac06eUMYLV6LIcDvsH0Ote7cp7NicMgcZ5sVMMvABB7jFs8RL7JS_UJQf77yaJlPCzXyxlTd9_2A3uP0m4W72O2G8faJYfmY6aiZFDlgngbagjKP6BgPsRLIrjch2Ku-vxbSJ4ovVd8p40W4SoTwRCCGzn9An2R2KueMWXjYbt86fl2Yto9G2z2gWmOTIajxNxpPhTmpVVGXkw1aspt_gTEAr9AAGrHVDC6hHuqy-SOExfX60t1AEVN7-XY3CiHzHfjJU4KQS21g0-ndK3GxeL397S3aa8h2mT2JdF-NpJkNHao8l8ANvOMAKQ3vr66nkVi1Tr-W7zopMTu_tAXe9dpwrwGeaH-Ff1iEGrkwAKdC6lPgbpYtqDAzXQlT0BUR3XzKEQMr0cuoAqlvl1L2UeveZMGAvG5ZV5csVp46S2evVgeP9Z0Q3Im1HQX0Yeu9qbAYRJhs-6FL0CfjO_WAo_FUmaRg_rlPlVa5luzpd1qlAfnLGbFsD8GzNa0dQPeNm02EBmE1bF0cjzbUtwwG4hwVf6B3CfpNS0uc5I3zSMOyUwjXxaHpw_AKVTaDc1AofgLzQpZ1adfDZ-tP7JmxVS3xDrFNzJUuB6_z-CzuXQJHeDK_M9a9x7u9lo1YAE0XTA_csuI9xTllZzbAWqYLcC7c_nrWYG3fKnyrY7W62BlhbM18wzuiN-tK9YDK1l2y_sh3E7LFxstbdt92aLenIjtSezkLZoAszQ3qShPhQbZ-7dRhQAn4L5Lah0FSHdzYuP_wfwSQwzaRttoOMDRlhZJZIHbQXTqxaW7vYyqx3AZrdKG3rO2mQNAYkU0KYwHFfqwy2czhhkrfwoR0UymM_igooxTAW2FS5AEot5bBB8k"}"""

RAW_VERIFY = """POST /pvt/verifyOtpForAuth?transport=cookie HTTP/1.1
Host: cem.mmtcpamp.com
Connection: close
Content-Length: 85
sec-ch-ua-platform: "Windows"
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36
Accept: application/json
sec-ch-ua: "Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"
Content-Type: application/json
DNT: 1
sec-ch-ua-mobile: ?0
Origin: https://www.mmtcpamp.com
Sec-Fetch-Site: same-site
Sec-Fetch-Mode: cors
Sec-Fetch-Dest: empty
Accept-Encoding: gzip, deflate
Accept-Language: en-US,en;q=0.9
Cookie: _gcl_au=1.1.261478789.1759404891; _ga=GA1.1.859209797.1759404891; _fbp=fb.1.1759404903588.64898692575041071; userLoggedIn=false; _ga_9LSF6MSSDZ=GS2.1.s1759777247$o6$g0$t1759777247$j60$l0$h0; _ga_QEH5V50FP3=GS2.1.s1759777247$o6$g0$t1759777247$j60$l0$h0; _ga_M47XQM4988=GS2.1.s1759777247$o6$g0$t1759777247$j60$l0$h0; _ga_GJXHT32TQD=GS2.1.s1759777258$o6$g1$t1759777270$j48$l0$h0; _ga_RXDVTDFTJ7=GS2.1.s1759777258$o6$g1$t1759777270$j48$l0$h0

{"mobileNumber":"__MOBILE__","otp":"__OTP__","platform":"dgsWeb","sendPromotions":"Y"}"""

RAW_CANCEL = """POST /redeem/cancelOrder HTTP/1.1
Host: cem.mmtcpamp.com
Connection: close
Content-Type: application/json
Accept: application/json
credentials: include
sec-ch-ua-platform: "Windows"
Authorization: Bearer __SESSION_ID__
sec-ch-ua: "Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"
sec-ch-ua-mobile: ?0
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36
DNT: 1
sessionId: undefined
Origin: https://www.mmtcpamp.com
Sec-Fetch-Site: same-site
Sec-Fetch-Mode: cors
Sec-Fetch-Dest: empty
Referer: https://www.mmtcpamp.com/
Accept-Encoding: gzip, deflate
Accept-Language: en-US,en;q=0.9
Cookie: _ga=GA1.1.2037018994.1754920141; _gcl_au=1.1.1554511401.1754920142

{"orderId":"__ORDER_ID__","type":"CANCEL","reason":"Not interested in product anymore","customerRefNo":"__CUSTOMER_REF_NO__"}"""

# -------------- Network config --------------
PROXY = None  # e.g. ('127.0.0.1', 8080) for Burp
SOCKET_TIMEOUT = 2.0

# ---------- low-level helpers ----------
def split_head_body(raw: str):
    if "\r\n\r\n" in raw: return raw.split("\r\n\r\n", 1)
    if "\n\n" in raw:     return raw.split("\n\n", 1)
    return raw, ""

def norm_head(head: str): 
    return "\r\n".join(re.split(r'\r\n|\r|\n', head))

def build_bytes(head: str, body: str) -> bytes: 
    return (norm_head(head)+"\r\n\r\n"+body).encode("utf-8")

def host_port_from_head(head: str):
    m=re.search(r'Host:\s*([^\r\n]+)', head, re.I)
    if not m: raise RuntimeError("Host header missing")
    host=m.group(1).strip()
    return (host.split(":",1)[0], int(host.split(":",1)[1]) if ":" in host else 443)

def recv_all(sock):
    sock.settimeout(SOCKET_TIMEOUT); bufs=[]
    try:
        while True:
            c=sock.recv(4096)
            if not c: break
            bufs.append(c)
    except Exception: pass
    return b"".join(bufs)

def send_connect_tls(host,port,raw_bytes,proxy=None)->bytes:
    """
    Low-level TLS connector. Guarded by ENABLE_NETWORK in call-sites.
    """
    if proxy:
        ph,pp=proxy
        s=socket.create_connection((ph,pp),10)
        s.sendall(f"CONNECT {host}:{port} HTTP/1.1\r\nHost: {host}:{port}\r\n\r\n".encode())
        resp=s.recv(4096)
        if b"200" not in resp.split(b"\r\n")[0]:
            raise RuntimeError("Proxy CONNECT failed:\n"+resp.decode("utf-8","ignore"))
        ctx=ssl.create_default_context(); ss=ctx.wrap_socket(s,server_hostname=host)
    else:
        s=socket.create_connection((host,port),10); ctx=ssl.create_default_context(); ss=ctx.wrap_socket(s,server_hostname=host)
    ss.sendall(raw_bytes); data=recv_all(ss); ss.close(); return data

def parse_http_response(resp: bytes):
    head_b,_,body_b = resp.partition(b"\r\n\r\n")
    head_t=head_b.decode("utf-8","ignore")
    lines=re.split(r'\r\n|\n|\r', head_t)
    status=lines[0] if lines else ""
    hdrs=[(k.strip(),v.strip()) for l in lines[1:] if ":" in l for k,v in [l.split(":",1)]]
    return status,hdrs,body_b

# ---------- cookie/header utils ----------
def collect_set_cookies(headers):
    jar={}
    for k,v in headers:
        if k.lower()=="set-cookie":
            nv=v.split(";",1)[0].strip()
            if "=" in nv: 
                n,val=nv.split("=",1); jar[n.strip()]=val.strip()
    return jar

def parse_cookie_header(line:str):
    jar={}
    for part in line.split(";"):
        if "=" in part:
            n,v=part.strip().split("=",1); jar[n.strip()]=v.strip()
    return jar

def merge_cookie_headers(orig_cookie:str, new_jar:Dict[str,str])->str:
    base=parse_cookie_header(orig_cookie) if orig_cookie else {}
    base.update(new_jar)
    return "; ".join(f"{k}={v}" for k,v in base.items())

def replace_or_add_header(head:str,key:str,value:str)->str:
    pat=re.compile(rf'(?im)^{re.escape(key)}\s*:\s*.*$', re.M)
    if pat.search(head): 
        return pat.sub(f"{key}: {value}", head, count=1)
    lines=re.split(r'\r\n|\n|\r', head)
    lines.insert(1, f"{key}: {value}")
    return "\r\n".join(lines)

def set_content_length(head:str, body:str)->str:
    return replace_or_add_header(head,"Content-Length", str(len(body.encode("utf-8"))))

# ---------- number picker ----------
def normalize_mobile(s: str) -> str:
    return re.sub(r'\D', '', s)

def pick_mobile() -> str:
    print("\nChoose mobile number:")
    for i, num in enumerate(COMMON_MOBILES, start=1):
        print(f" {i}) {num}")
    print(" 0) Enter another number")
    while True:
        choice = input("Select (0-"+str(len(COMMON_MOBILES))+"): ").strip()
        if choice.isdigit():
            idx = int(choice)
            if idx == 0:
                custom = input("Enter mobile number: ").strip()
                mob = normalize_mobile(custom)
                if len(mob) == 10 and mob[0] in "6789":
                    return mob
                else:
                    print("! invalid mobile. must be 10 digits starting 6/7/8/9")
            elif 1 <= idx <= len(COMMON_MOBILES):
                return COMMON_MOBILES[idx-1]
        print("Invalid choice. Try again.")

# ---------- cancel helper (for multiple IDs) ----------
def do_cancel(order_id: str, session_id: Optional[str], customer_ref: Optional[str], verify_cookies: Dict[str,str]):
    c_head,c_body = split_head_body(RAW_CANCEL)
    c_body = c_body.replace("__ORDER_ID__", order_id)
    if customer_ref:
        c_body = c_body.replace("__CUSTOMER_REF_NO__", customer_ref)

    # Authorization + sessionId header fix
    if session_id:
        c_head = c_head.replace("__SESSION_ID__", session_id)
        if not re.search(r'(?im)^Authorization\s*:', c_head):
            c_head = replace_or_add_header(c_head, "Authorization", f"Bearer {session_id}")
        c_head = re.sub(r'(?im)^sessionId\s*:\s*undefined\s*$', f"sessionId: {session_id}", c_head)

    # Merge cookies
    m = re.search(r'(?im)^Cookie\s*:\s*(.*)$', c_head)
    orig_cookie = m.group(1).strip() if m else ""
    if verify_cookies:
        merged_cookie = merge_cookie_headers(orig_cookie, verify_cookies)
        c_head = replace_or_add_header(c_head, "Cookie", merged_cookie)

    c_head = set_content_length(c_head, c_body)
    chost,cport = host_port_from_head(c_head)
    c_req = build_bytes(c_head, c_body)
    c_resp = send_connect_tls(chost,cport,c_req, PROXY)
    # Save per-order logs
    open(f"cancel_{order_id}.raw","wb").write(c_resp)

    c_status,c_hdrs,c_body_bytes = parse_http_response(c_resp)
    print(f"[*] Cancel status for {order_id}:", c_status)
    try:
        parsed = json.loads(c_body_bytes.decode("utf-8","ignore"))
        print("[i] Cancel JSON:", json.dumps(parsed, indent=2))
    except Exception:
        preview = c_body_bytes.decode("utf-8","ignore")[:800]
        print("[i] Cancel body preview:", preview)

# ---------- main ----------
def main():
    print("[*] OTP flow + multi-cancel")

    if not ENABLE_NETWORK:
        print("[!] Network execution is DISABLED (ENABLE_NETWORK=False).")
        print("[!] Safe mode: will skip actual network actions.\n")

    # Pick mobile once
    mobile = pick_mobile()
    print(f"[i] Using mobile: {mobile}")

    if not ENABLE_NETWORK:
        print("[i] Network disabled — exiting before trigger/verify/cancel.")
        return

    # 1) Trigger (inject mobile)
    t_head,t_body = split_head_body(RAW_TRIGGER)
    t_body = t_body.replace("__MOBILE__", mobile)
    t_head = set_content_length(t_head, t_body)
    thost,tport = host_port_from_head(t_head)
    t_req = build_bytes(t_head, t_body)
    t_resp = send_connect_tls(thost,tport,t_req, PROXY)
    open("trigger_response.raw","wb").write(t_resp)
    print("[+] trigger_response.raw saved")

    # 2) Verify (inject mobile + OTP)
    otp = input("Enter OTP: ").strip()
    if not otp:
        print("No OTP. Exiting.")
        return
    v_head,v_body = split_head_body(RAW_VERIFY)
    v_body = v_body.replace("__MOBILE__", mobile)
    v_body = v_body.replace("__OTP__", otp) if "__OTP__" in v_body else re.sub(r'("otp"\\s*:\\s*")\\d+(")', r'\\1'+otp+r'\\2', v_body)
    v_head = set_content_length(v_head, v_body)
    vhost,vport = host_port_from_head(v_head)
    v_req = build_bytes(v_head, v_body)
    v_resp = send_connect_tls(vhost,vport,v_req, PROXY)
    open("verify_response.raw","wb").write(v_resp)
    print("[+] verify_response.raw saved")

    # Parse verify for sessionId/customerRefNo + cookies
    status,hdrs,v_body_bytes = parse_http_response(v_resp)
    verify_cookies = collect_set_cookies(hdrs)
    session_id = None; customer_ref = None
    try:
        v_json = json.loads(v_body_bytes.decode("utf-8","ignore"))
        session_id   = v_json.get("sessionId") or v_json.get("jwt") or v_json.get("token")
        customer_ref = v_json.get("customerRefNo") or v_json.get("dgCustomerRefNo")
        print("[i] verify JSON:", {"sessionId": bool(session_id), "customerRefNo": customer_ref})
    except Exception as e:
        print("[!] verify JSON parse failed:", e)

    # 3) Cancel — MULTI ORDER LOOP
    print("\n--- Multi-Cancel Mode ---")
    print("Enter ORDER_ID one by one. Leave blank and press Enter to finish.\n")
    while True:
        order_id = input("ORDER_ID: ").strip()
        if not order_id:
            print("No more ORDER_IDs. Done.")
            break
        try:
            do_cancel(order_id, session_id, customer_ref, verify_cookies)
        except Exception as e:
            print(f"[!] Error cancelling {order_id}: {e}")
        # Small pause between calls (optional)
        time.sleep(0.5)

if __name__ == "__main__":
    main()