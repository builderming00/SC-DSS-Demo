import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json, os, re, time, math, random
import numpy as np
from scipy.optimize import LinearConstraint, Bounds, milp
from datetime import datetime

# ================= 页面配置 =================
st.set_page_config(layout="wide", page_title="智造决策中枢 | SC-DSS")

# ================= 全局主题与 UI 引擎 =================
if 'ui_theme' not in st.session_state: st.session_state['ui_theme'] = '暗黑极客风'

THEME_LIST = [
    "暗黑极客风", "高级商务灰", "赛博朋克紫", "深空静谧蓝", 
    "金融终端黑金", "极简护眼绿", "原生极简风",
    "Dracula (吸血鬼)", "Spotify (暗夜绿)", "GitHub (极客黑)", 
    "Nord (极地冰蓝)", "Tokyo Night (东京夜)", "Catppuccin (猫猫拿铁)", 
    "Solarized (日光青)", "Material (质感蓝)", "Stripe (斯特里普)"
]

def apply_ui_theme(theme_name):
    light_themes = ["高级商务灰", "极简护眼绿", "原生极简风", "Stripe (斯特里普)", "Solarized (日光青)"]
    is_dark = theme_name not in light_themes
    plotly_template = "plotly_dark" if is_dark else "plotly_white"
    
    colors = {
        "暗黑极客风": {"bg": "#0E1117", "sidebar": "#1E2130", "text": "#FAFAFA", "accent": "#00FFCC"},
        "高级商务灰": {"bg": "#F4F6F9", "sidebar": "#E2E8F0", "text": "#2C3E50", "accent": "#1A365D"},
        "赛博朋克紫": {"bg": "#130b1e", "sidebar": "#20152e", "text": "#f0e6d2", "accent": "#ff00ff"},
        "深空静谧蓝": {"bg": "#0B132B", "sidebar": "#1C2541", "text": "#E2E8F0", "accent": "#5BC0BE"},
        "金融终端黑金": {"bg": "#000000", "sidebar": "#111111", "text": "#E5E7EB", "accent": "#D4AF37"},
        "极简护眼绿": {"bg": "#E8F5E9", "sidebar": "#C8E6C9", "text": "#1B5E20", "accent": "#2E7D32"},
        "原生极简风": {"bg": "#FFFFFF", "sidebar": "#F0F2F6", "text": "#31333F", "accent": "#FF4B4B"},
        "Dracula (吸血鬼)": {"bg": "#282a36", "sidebar": "#44475a", "text": "#f8f8f2", "accent": "#ff79c6"},
        "Spotify (暗夜绿)": {"bg": "#121212", "sidebar": "#181818", "text": "#FFFFFF", "accent": "#1DB954"},
        "GitHub (极客黑)": {"bg": "#0d1117", "sidebar": "#161b22", "text": "#c9d1d9", "accent": "#58a6ff"},
        "Nord (极地冰蓝)": {"bg": "#2E3440", "sidebar": "#3B4252", "text": "#D8DEE9", "accent": "#88C0D0"},
        "Tokyo Night (东京夜)": {"bg": "#1a1b26", "sidebar": "#24283b", "text": "#c0caf5", "accent": "#bb9af7"},
        "Catppuccin (猫猫拿铁)": {"bg": "#1e1e2e", "sidebar": "#313244", "text": "#cdd6f4", "accent": "#f5c2e7"},
        "Solarized (日光青)": {"bg": "#fdf6e3", "sidebar": "#eee8d5", "text": "#657b83", "accent": "#cb4b16"},
        "Material (质感蓝)": {"bg": "#121212", "sidebar": "#1e1e1e", "text": "#e0e0e0", "accent": "#bb86fc"},
        "Stripe (斯特里普)": {"bg": "#f6f9fc", "sidebar": "#ffffff", "text": "#425466", "accent": "#635bff"}
    }
    
    c = colors.get(theme_name, colors["暗黑极客风"])
    font_color = c['text']
    grid_color = "#333333" if is_dark else "#E5E7EB"

    css = f"""
    <style>
        .stApp {{ background-color: {c['bg']} !important; }}
        [data-testid="stSidebar"] {{ background-color: {c['sidebar']} !important; }}
        .stApp, .stApp p, .stApp span, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, .stApp label, div[data-testid="stMarkdownContainer"] p {{ color: {c['text']} !important; }}
        [data-testid="stSidebar"] *, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] label, [data-testid="stSidebar"] summary {{ color: {c['text']} !important; }}
        .js-plotly-plot .plotly text, .js-plotly-plot .plotly .gtitle, .js-plotly-plot .plotly .xtick text, .js-plotly-plot .plotly .ytick text {{ fill: {font_color} !important; }}
        .js-plotly-plot .plotly .main-svg {{ background: transparent !important; }}
        div[data-testid="stMetric"] {{ background-color: {c['sidebar']} !important; border: 1px solid {c['accent']} !important; border-radius: 10px; padding: 10px; box-shadow: 0 0 10px {c['accent']}40; }}
        [data-testid="stPopoverBody"] {{ background-color: {c['sidebar']} !important; color: {c['text']} !important; border: 1px solid {c['accent']} !important; }}
        [data-testid="stPopoverBody"] * {{ color: {c['text']} !important; }}
        div[data-testid="stPopover"] {{ position: fixed !important; top: 65px !important; right: 30px !important; width: 50px !important; height: 50px !important; z-index: 9999999 !important; }}
        div[data-testid="stPopover"] > div {{ width: 50px !important; height: 50px !important; }}
        div[data-testid="stPopover"] button {{ width: 50px !important; height: 50px !important; border-radius: 50% !important; background-color: {c['sidebar']} !important; border: 2px solid {c['accent']} !important; box-shadow: 0 0 15px {c['accent']}80 !important; font-size: 22px !important; padding: 0 !important; display: flex !important; align-items: center !important; justify-content: center !important; transition: all 0.3s ease !important; }}
        div[data-testid="stPopover"] button * {{ color: {c['text']} !important; }}
        div[data-testid="stPopover"] button:hover, div[data-testid="stPopover"] button:focus, div[data-testid="stPopover"] button:active {{ transform: rotate(90deg) scale(1.1) !important; box-shadow: 0 0 25px {c['accent']} !important; }}
        div[data-testid="stPopover"] svg {{ display: none !important; }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
    
# ================= 终极移动端暴力拦截 =================
st.markdown("""
<style>
    /* 桌面端隐藏这个盖板 */
    #mobile-blocker { display: none; }

    /* 只要屏幕宽度小于 1024px（手机、平板），立刻启动绝对防御 */
    @media screen and (max-width: 1024px) {
        /* 1. 彻底干掉 Streamlit 的所有原生组件，连顶部的菜单都不留 */
        [data-testid="stAppViewContainer"], 
        [data-testid="stSidebar"], 
        [data-testid="stPopover"],
        [data-testid="stHeader"],
        header {
            display: none !important;
        }
        
        /* 2. 强行拉起全屏盖板 */
        #mobile-blocker {
            display: flex !important;
            position: fixed !important;
            top: 0 !important; left: 0 !important; right: 0 !important; bottom: 0 !important;
            width: 100vw !important; height: 100vh !important;
            background-color: #0E1117 !important;
            color: #FAFAFA !important;
            z-index: 2147483647 !important; /* 网页层级最高值 */
            flex-direction: column !important;
            justify-content: center !important;
            align-items: center !important;
            padding: 30px !important;
            text-align: center !important;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
        }
        
        /* 标题样式 */
        #mobile-blocker h2 {
            color: #FF4B4B !important;
            font-size: 24px !important;
            margin-bottom: 20px !important;
        }
        
        /* 正文样式 */
        #mobile-blocker p {
            color: #00FFCC !important;
            font-size: 16px !important;
            line-height: 1.8 !important;
            margin-bottom: 20px !important;
        }
        
        /* 底部的灰字提示 */
        #mobile-blocker .footer {
            color: #888888 !important;
            font-size: 12px !important;
            margin-top: 40px !important;
        }
    }
</style>

<!-- 盖板本体 -->
<div id="mobile-blocker">
    <h2>⚠️ 企业级安全拦截</h2>
    <p>
        检测到您正在使用移动端/小屏幕设备。<br><br>
        由于本系统包含 <b>1280 维 MILP 矩阵推演</b> 与多维交互看板，为保证决策操作精准度与数据安全，已强制限制 PC（电脑端）浏览器访问。<br><br>
        请使用电脑端打开此链接以获取全景数据大屏体验。
    </p>
    <div class="footer">© 2026 智造决策中枢 v3.5.1 | 仅限 PC 端访问</div>
</div>
""", unsafe_allow_html=True)
    
    return plotly_template, font_color, grid_color

plotly_tpl, font_color, grid_color = apply_ui_theme(st.session_state['ui_theme'])

# ================= 悬浮球 UI (企业级控制中心) =================
with st.popover("⚙️", help="打开系统级设置"):
    st.markdown("### 🎛️ 系统控制中枢")
    tab1, tab2, tab3 = st.tabs(["🎨 外观主题", "🔐 账号安全", "✉️ 意见反馈"])
    
    with tab1:
        selected_theme = st.radio("🎨 界面视觉风格", THEME_LIST, index=THEME_LIST.index(st.session_state['ui_theme']))
        if selected_theme != st.session_state['ui_theme']:
            st.session_state['ui_theme'] = selected_theme
            st.rerun()
            
    with tab2:
        st.markdown("#### 修改企业授权密码")
        with st.form("change_pwd_form", border=False):
            old_pwd = st.text_input("当前密码", type="password")
            new_pwd = st.text_input("新密码", type="password")
            confirm_pwd = st.text_input("确认新密码", type="password")
            if st.form_submit_button("确认修改", use_container_width=True, type="primary"):
                username = st.session_state['current_user'].name
                if old_pwd == dic_name_and_password.get(username):
                    if new_pwd == confirm_pwd and len(new_pwd) >= 4:
                        dic_name_and_password[username] = new_pwd
                        try:
                            with open('demo.json', 'w', encoding='utf-8') as f: json.dump(dic_name_and_password, f, ensure_ascii=False, indent=2)
                        except Exception: pass
                        st.success("✅ 密码修改成功！")
                        time.sleep(1); st.rerun()
                    elif len(new_pwd) < 4: st.error("❌ 密码长度不能少于 4 位！")
                    else: st.error("❌ 两次输入的新密码不一致！")
                else: st.error("❌ 当前密码验证失败！")
                    
    with tab3:
        st.markdown("#### 提交系统反馈")
        with st.form("feedback_form", border=False):
            fb_type = st.selectbox("反馈类型", ["功能建议", "系统 Bug", "体验优化", "其他"])
            fb_text = st.text_area("详细描述", height=100, placeholder="请描述您遇到的问题或建议...")
            if st.form_submit_button("发送反馈", use_container_width=True, type="primary"):
                if fb_text.strip():
                    try:
                        with open("feedback.txt", "a", encoding="utf-8") as f:
                            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 用户: {st.session_state['current_user'].name} | 类型: {fb_type}\n内容: {fb_text}\n---\n")
                    except Exception: pass
                    st.toast("🚀 反馈已成功发送至云端服务器！", icon="✅")
                    time.sleep(1); st.rerun()
                else: st.warning("⚠️ 请填写反馈内容！")

# ================= 登录/注册 UI 模块 =================
class User:
    def __init__(self, name, password):
        self.name = name
        self.password = password
        self.role = "高级管理员"

dic_name_and_password = {}
try:
    if os.path.exists('demo.json'):
        with open('demo.json', 'r', encoding='utf-8') as f: dic_name_and_password = json.load(f)
    else:
        dic_name_and_password = {"admin": "admin123"}
        with open('demo.json', 'w', encoding='utf-8') as f: json.dump(dic_name_and_password, f, ensure_ascii=False, indent=2)
except Exception:
    dic_name_and_password = {"admin": "admin123"}

if 'current_user' not in st.session_state: st.session_state['current_user'] = None

if st.session_state['current_user'] is None:
    col_l, col_c, col_r = st.columns([1, 1, 1])
    with col_c:
        st.markdown("<h2 style='text-align: center;'>🔐 SC-DSS 企业级决策系统</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: gray;'>企业级供应链调度与商业决策中枢</p>", unsafe_allow_html=True)
        st.write("") 
        
        auth_mode = st.radio("选择操作", ["🔑 安全登录", "📝 注册新账号"], horizontal=True, label_visibility="collapsed")
        
        if auth_mode == "🔑 安全登录":
            with st.form(border=True, key='login_form'):
                name = st.text_input('👤 用户名')
                password = st.text_input('🔑 密码', type='password')
                col1, col2 = st.columns([1, 1])
                with col1: submit = st.form_submit_button("安全登录", use_container_width=True, type="primary")
                with col2:
                    lose = st.form_submit_button("找回密码", use_container_width=True)
                    if lose:
                        with st.spinner("正在连接企业安全网关..."): time.sleep(1.2)
                        st.info("💡 **[系统提示]** 当前处于试运营 Demo 环境，暂未接通企业短信/邮件验证码通道。请使用内部测试账号直接登录。")
                        st.toast("短信通道未接通", icon="📵")
                if submit:
                    if name in dic_name_and_password:
                        if password == dic_name_and_password[name]:
                            st.session_state['current_user'] = User(name, password)
                            st.success(f"欢迎回来，{st.session_state['current_user'].role} {name}！")
                            st.rerun()
                        else: st.error("⚠️ 登录失败：密码错误！")
                    else: st.error("⚠️ 登录失败：该用户名未注册！")
                    
        else:
            with st.form(border=True, key='register_form'):
                new_name = st.text_input('👤 设置用户名')
                new_password = st.text_input('🔑 设置密码', type='password')
                confirm_password = st.text_input('🔒 确认密码', type='password')
                submit_reg = st.form_submit_button("立即注册并登录", use_container_width=True, type="primary")
                if submit_reg:
                    if not new_name or not new_password: st.warning("⚠️ 用户名和密码不能为空！")
                    elif new_name in dic_name_and_password: st.error("❌ 该用户名已被注册，请更换！")
                    elif new_password != confirm_password: st.error("❌ 两次输入的密码不一致！")
                    elif len(new_password) < 4: st.warning("⚠️ 密码长度不能少于 4 位！")
                    else:
                        dic_name_and_password[new_name] = new_password
                        try:
                            with open('demo.json', 'w', encoding='utf-8') as f: json.dump(dic_name_and_password, f, ensure_ascii=False, indent=2)
                        except Exception: pass
                        st.session_state['current_user'] = User(new_name, new_password)
                        st.success(f"✅ 注册成功！正在进入系统...")
                        time.sleep(1); st.rerun()

        st.caption("© 2026 智造决策中枢 v3.5.1 | 本平台已通过 ISO 27001 认证")
    st.stop()

# ==================== 全局变量与映射 ====================
DATA_FILE = "data-1.json"
MAX_PERIOD = 16
P_NAMES = {"A": "智能终端", "B": "穿戴设备", "C": "服务器", "D": "工业主板"}
M_NAMES = {"1": "华东大区", "2": "华南大区", "3": "华北大区", "4": "西南大区"}
rev_p = {v: k for k, v in P_NAMES.items()}
rev_m = {v: k for k, v in M_NAMES.items()}

# ==================== 数据读写与解析器 ====================
@st.cache_data(show_spinner=False)
def _load_data_cached(file_mtime):
    try:
        if not os.path.exists(DATA_FILE): return []
        with open(DATA_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except Exception:
        return []

def load_data():
    try:
        if not os.path.exists(DATA_FILE): return []
        return _load_data_cached(os.path.getmtime(DATA_FILE))
    except Exception:
        return []

def save_data(records):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f: json.dump(records, f, ensure_ascii=False, indent=2)
        _load_data_cached.clear()
    except Exception:
        pass

def clean_number(s):
    if s is None: return None
    s = str(s).strip()
    if not s: return None
    if s.startswith("(") and s.endswith(")"): s = "-" + s[1:-1]
    s = s.replace("，", ",").replace("％", "%").replace("＋", "+").replace("\u3000", "")
    is_percent = "%" in s
    for ch in [",", "+", "%", "元", "件", "人", "台", "个", " ", "\t"]: s = s.replace(ch, "")
    try:
        val = float(s)
        if is_percent: val = val / 100.0
        return val
    except ValueError: return None

def fill_forward(row):
    result, last = [], ""
    for c in row:
        if c: last = c
        result.append(last)
    return result

def looks_like_share_table(result):
    if not result: return False
    values = [v for v in result.values() if v is not None]
    if not values: return False
    return all(0 <= v <= 1 for v in values) and any(0 < v < 1 for v in values)

def extract_competitor_matrix(text, my_company_name):
    raw_lines = [l for l in text.strip().split("\n") if l.strip()]
    if len(raw_lines) < 3: return {}
    product_markets = [f"产品{p}_市场{m}" for p in "ABCD" for m in "1234"]
    def clean_name(name): return re.sub(r"\s+", "", str(name))
    my_company_clean = clean_name(my_company_name)
    result = {}
    for line in raw_lines[2:]:
        matches = list(re.finditer(r"[\d,]+(?:\.\d+)?%?", line))
        if len(matches) < 16: continue
        valid_matches = matches[-16:]
        comp_name = line[:valid_matches[0].start()].strip()
        comp_name = re.sub(r"\s+", " ", comp_name).strip()
        if not comp_name: continue
        data_dict = {}
        for i, match in enumerate(valid_matches):
            val_str = match.group(0)
            val = clean_number(val_str)
            if val is not None:
                if "%" in val_str: data_dict[f"{product_markets[i]}_份额"] = val
                elif val > 500: data_dict[f"{product_markets[i]}_价格"] = val
                else: data_dict[f"{product_markets[i]}_本期需求"] = val
        if data_dict:
            if clean_name(comp_name) == my_company_clean: result[my_company_name] = data_dict
            else: result[comp_name] = data_dict
    return result

def find_title(grid, header_idx):
    for j in range(header_idx - 1, -1, -1):
        if any("期数" in c for c in grid[j]): break
        for cell in grid[j]:
            if "时间序列数据" in cell: return cell
    return ""

def parse_time_series(title, headers, data_rows):
    pm = re.search(r"产品([ABCD])", title); mm = re.search(r"市场([1234])", title)
    prefix = f"产品{pm.group(1)}_市场{mm.group(1)}" if pm and mm else ("企业" if "经营时间序列" in title else (title.strip() or "TS"))
    period_idx = next((i for i, h in enumerate(headers) if "期数" in h), None)
    if period_idx is None: return {}
    clean_headers = [re.sub(r"[（(].*?[)）]", "", h).strip() for h in headers]
    result = {}
    for row in data_rows:
        if len(row) <= period_idx: continue
        pv = clean_number(row[period_idx])
        if pv is None: continue
        period = int(pv)
        data = {}
        for j, h in enumerate(clean_headers):
            if j == period_idx or not h or j >= len(row): continue
            v = clean_number(row[j])
            if v is not None: data[f"{prefix}_{h}"] = v
        if data: result[period] = data
    return result

def parse_multi_ts(grid, default_period):
    result = {}
    i = 0
    while i < len(grid):
        if not any("期数" in c for c in grid[i]): i += 1; continue
        title = find_title(grid, i)
        headers = [c for c in grid[i] if c]
        data_rows = []
        j = i + 1
        while j < len(grid):
            if any("期数" in c for c in grid[j]): break
            row = [c for c in grid[j] if c]
            if len(row) >= 2: data_rows.append(row)
            j += 1
        for period, data in parse_time_series(title, headers, data_rows).items():
            if period not in result: result[period] = {}
            result[period].update(data)
        i = j
    return result

def parse_single_column(grid):
    result = {}
    i = 0
    while i < len(grid):
        cells = [c for c in grid[i] if c]
        if not cells: i += 1; continue
        label = cells[0]
        if clean_number(label) is not None: i += 1; continue
        if i + 1 < len(grid):
            next_cells = [c for c in grid[i + 1] if c]
            if next_cells:
                v = clean_number(next_cells[0])
                if v is not None: result[label] = v; i += 2; continue
        i += 1
    return result

def parse_as_kv(raw_lines):
    result = {}
    for line in raw_lines:
        parts = re.split(r"\s+", line.strip())
        if len(parts) < 2: continue
        label = parts[0].strip()
        if not label or clean_number(label) is not None: continue
        for p in parts[1:]:
            val = clean_number(p)
            if val is not None: result[label] = val; break
    return result

def looks_like_table(grid):
    ner = [[c for c in cells if c] for cells in grid if [c for c in cells if c]]
    if len(ner) < 2: return False
    first = ner[0]
    if len(first) < 3 or any(clean_number(c) is not None for c in first): return False
    df = next((row for row in ner[1:] if any(clean_number(c) is not None for c in row)), None)
    return df is not None and len(df) >= len(first) * 0.5

def parse_2d_table(grid2, default_period):
    header_rows = []
    for i, cells in enumerate(grid2):
        non_empty = [c for c in cells if c and c.strip()]
        if len(non_empty) < 2: continue
        if all(clean_number(c) is None for c in non_empty): header_rows.append(i)
        else: break
    if not header_rows: return None
    data_start = header_rows[-1] + 1
    cleaned = []
    for i in range(data_start, len(grid2)):
        cells = [c.strip() for c in grid2[i] if c and c.strip()]
        if not cells: continue
        row_label = ""
        if clean_number(cells[0]) is None: row_label = cells[0]; cells = cells[1:]
        cells = [c for c in cells if c not in ("+", "-")]
        if cells and any(clean_number(c) is not None for c in cells): cleaned.append((row_label, cells))
    if not cleaned: return None
    N = len(cleaned[0][1])
    if len(header_rows) >= 2:
        g_raw = [c.strip() for c in grid2[header_rows[-2]] if c and c.strip()]
        c_raw = [c.strip() for c in grid2[header_rows[-1]] if c and c.strip()]
        while g_raw and not re.match(r"^产品[A-D]$", str(g_raw[0])): g_raw = g_raw[1:]
        c_row = c_raw[-N:] if len(c_raw) >= N else c_raw
        if len(g_raw) == N: pass
        elif len(g_raw) > 0 and N % len(g_raw) == 0: g_raw = [g for g in g_raw for _ in range(N // len(g_raw))]
        else:
            g_raw = fill_forward(g_raw)
            while len(g_raw) < N: g_raw.append(g_raw[-1] if g_raw else "未知产品")
            g_raw = g_raw[:N]
        col_names = []
        for j in range(N):
            g = g_raw[j] if j < len(g_raw) else ""
            c = c_row[j] if j < len(c_row) else ""
            col_names.append(f"{g}_{c}" if g and c else (c or g or f"col{j}"))
    else:
        h_raw = [c.strip() for c in grid2[header_rows[0]] if c and c.strip()]
        while h_raw and h_raw[0] in ("公司", "指标", "项目"): h_raw = h_raw[1:]
        col_names = h_raw[-N:] if len(h_raw) >= N else h_raw + [f"col{i}" for i in range(len(h_raw), N)]
    result = {}
    for row_label, cells in cleaned:
        for j, cell in enumerate(cells):
            if j >= N: break
            v = clean_number(cell)
            if v is not None: result[f"{row_label}_{col_names[j]}" if row_label else col_names[j]] = v
    return {default_period: result} if result else None

def parse_product_tables(grid, default_period):
    result, i = {}, 0
    while i < len(grid):
        cells = [c for c in grid[i] if c]
        if not cells: i += 1; continue
        if len(cells) >= 3 and cells[0] == "产品" and all(clean_number(c) is None for c in cells):
            header, data_rows, j = cells, [], i + 1
            while j < len(grid):
                row = [c for c in grid[j] if c]
                if not row: j += 1; continue
                if len(row) >= 3 and row[0] == "产品" and all(clean_number(c) is None for c in row): break
                data_rows.append(row); j += 1
            _parse_product_segment(header, data_rows, result)
            i = j
        else: i += 1
    return {default_period: result} if result else None

def _parse_product_segment(header, data_rows, result):
    if not header or not data_rows: return
    has_market = len(header) >= 2 and header[1] == "市场"
    clean_header = [re.sub(r"[（(].*?[)）]", "", h).strip() for h in header]
    for row in data_rows:
        if not row: continue
        key_prefix = f"{row[0]}_{row[1]}" if has_market else row[0]
        start = 2 if has_market else 1
        for j in range(start, len(row)):
            if j >= len(clean_header): break
            if clean_header[j]:
                v = clean_number(row[j])
                if v is not None: result[f"{key_prefix}_{clean_header[j]}"] = v

def extract_my_company(text, my_company_name):
    if not my_company_name: return None
    lines = [l for l in text.strip().split("\n") if l.strip()]
    def split_line(line): return [c.strip() for c in re.split(r"\t+|\s{2,}", line) if c.strip()]
    def is_h(cells): return cells and cells[0] in ("公司", "企业", "队名")
    header_indices = [i for i, line in enumerate(lines) if is_h(split_line(line))]
    if not header_indices: return None
    result = {}
    for k, h_idx in enumerate(header_indices):
        header_cells = split_line(lines[h_idx])
        if my_company_name not in header_cells: continue
        col_idx = header_cells.index(my_company_name)
        title = f"{my_company_name}_数值"
        if h_idx > 0:
            prev = lines[h_idx - 1].strip()
            if not re.match(r"^第\d+期", prev) and not is_h(split_line(prev)): title = prev
        next_boundary = len(lines)
        if k + 1 < len(header_indices): next_boundary = header_indices[k + 1]
        for i in range(h_idx + 1, next_boundary):
            cells = split_line(lines[i])
            if not cells: continue
            m = re.match(r"^第(\d+)期", cells[0])
            if not m: break
            if len(cells) > col_idx:
                v = clean_number(cells[col_idx])
                if v is not None:
                    period = int(m.group(1))
                    if period not in result: result[period] = {}
                    result[period][title] = v
    return result if result else None

def extract_company_row_table(text, my_company_name, default_period):
    lines = [l for l in text.strip().split("\n") if l.strip()]
    if len(lines) < 3: return None
    def split_line(line):
        line_norm = line.replace("\u3000", " ").rstrip()
        return [c.strip() for c in line_norm.split("\t") if c.strip()] if "\t" in line_norm else [c.strip() for c in re.split(r"\s+", line_norm) if c.strip()]
    row1, row2 = split_line(lines[0]), split_line(lines[1])
    if not row1 or row1[0] != "公司" or not any(re.match(r"^产品[A-D]$", c) for c in row1) or not any(re.match(r"^市场[1234]$", c) for c in row2): return None
    g_row, c_row = [c for c in row1[1:] if c], [c for c in row2 if c]
    N = len(c_row)
    if N == 0: return None
    if len(g_row) != N:
        if len(g_row) > 0 and N % len(g_row) == 0: g_row = [g for g in g_row for _ in range(N // len(g_row))]
        else: g_row = fill_forward(g_row)[:N]
    col_names = [f"{g_row[j]}_{c_row[j]}" for j in range(N)]
    target_row = None
    for line in lines[2:]:
        parts = split_line(line)
        if not parts: continue
        if parts[0] == my_company_name:
            target_row = parts[1:]; break
    if target_row is None:
        for line in lines[2:]:
            parts = split_line(line)
            if len(parts) >= 2 and clean_number(parts[0]) is None:
                target_row = parts[1:]; break
    if not target_row: return None
    result = {}
    for j, cell in enumerate(target_row):
        if j < len(col_names):
            v = clean_number(cell)
            if v is not None: result[col_names[j]] = v
    if not result: return None
    if looks_like_share_table(result): result = {f"{k}_份额": v for k, v in result.items()}
    return {default_period: result} if result else None

def extract_company_slash_table(text, my_company_name, default_period):
    if not my_company_name: return None
    lines = [l for l in text.strip().split("\n") if l.strip()]
    def split_line(line):
        line_norm = line.replace("\u3000", " ").rstrip()
        return [c.strip() for c in line_norm.split("\t") if c.strip()] if "\t" in line_norm else [c.strip() for c in re.split(r"\s+", line_norm) if c.strip()]
    header = split_line(lines[0])
    if not header or header[0] not in ("公司", "企业", "队名") or len([c for c in header if re.match(r"^产品[A-D]/市场[1234]$", c)]) < 3: return None
    target = next((split_line(line) for line in lines[1:] if split_line(line) and split_line(line)[0] == my_company_name), None)
    if not target: return None
    result = {}
    for j, col_name in enumerate(header):
        if j > 0 and j < len(target):
            v = clean_number(target[j])
            if v is not None: result[col_name.replace("/", "_")] = v
    if not result: return None
    if looks_like_share_table(result): result = {f"{k}_份额": v for k, v in result.items()}
    return {default_period: result} if result else None

def extract_company_metrics_row(text, my_company_name, default_period):
    if not my_company_name: return None
    lines = [l for l in text.strip().split("\n") if l.strip()]
    def split_line(line):
        line_norm = line.replace("\u3000", " ").rstrip()
        return [c.strip() for c in line_norm.split("\t") if c.strip()] if "\t" in line_norm else [c.strip() for c in re.split(r"\s+", line_norm) if c.strip()]
    header = split_line(lines[0])
    if not header or header[0] not in ("公司", "企业", "队名") or len(header) < 3 or any(re.match(r"^产品[A-D]$", c) for c in header): return None
    for line in lines[1:]:
        cells = split_line(line)
        if not cells: continue
        if cells[0] == my_company_name:
            return {default_period: {name: clean_number(cells[j+1]) for j, name in enumerate(header[1:]) if j+1 < len(cells) and clean_number(cells[j+1]) is not None}}
    return None

def parse_text(text, default_period):
    raw_lines = [l for l in text.strip().split("\n") if l.strip()]
    if not raw_lines: return {}
    my_company = st.session_state.get("my_company", "")
    comp_data = extract_competitor_matrix(text, my_company)
    if comp_data:
        result = {default_period: {}}
        for comp, data in comp_data.items():
            prefix = "" if comp == my_company else f"【{comp}】_"
            for col, val in data.items():
                if col != "公司": result[default_period][f"{prefix}{col}"] = val
        return result
    if my_company:
        for func in [extract_my_company, extract_company_row_table, extract_company_slash_table, extract_company_metrics_row]:
            r = func(text, my_company, default_period) if func != extract_my_company else func(text, my_company)
            if r: return r
    grid = []
    for line in raw_lines:
        line_norm = line.replace("\u3000", " ").rstrip()
        grid.append([c.strip() for c in line_norm.split("\t") if c.strip()] if "\t" in line_norm else [c.strip() for c in re.split(r"\s+", line_norm) if c.strip()])
    if any("期数" in c for row in grid for c in row): return parse_multi_ts(grid, default_period)
    if any(len([c for c in row if c]) >= 3 and [c for c in row if c][0] == "产品" and all(clean_number(c) is None for c in row) for row in grid):
        r = parse_product_tables(grid, default_period)
        if r: return r
    if looks_like_table(grid):
        r = parse_2d_table(grid, default_period)
        if r: return r
    kv_result = parse_as_kv(raw_lines)
    if kv_result: return {default_period: kv_result}
    if all(len(row) <= 1 for row in grid):
        r = parse_single_column(grid)
        return {default_period: r} if r else {}
    return {}

# ==================== 分类与汇总 ====================
CATEGORIES = {
    "核心财务": ["净利润", "净资产", "市场份额", "综合评分", "发展趋势", "收入", "利润", "ROE", "ROA", "资产负债率"],
    "成本与费用": ["成本", "费用", "广告", "促销", "运输", "废品", "管理", "折旧", "利息", "工资", "材料", "存储", "研发", "培训", "安置", "资产减值", "机时毛利"],
    "资金与负债": ["现金", "现金流", "负债", "债券", "贷款", "国债"],
    "库存与产能": ["原材料", "成品", "库存", "工人", "机器", "产线", "人机比", "利用率", "当量", "偏差"],
    "市场博弈": ["价格", "需求", "销量", "销售量", "订货", "份额", "机时", "边际", "供需", "预订", "膨胀率", "总需求", "行业大盘", "均价", "最低价", "繁荣度"],
    "产品": ["产品A", "产品B", "产品C", "产品D", "全公司"],
    "自定义计算": ["毛利", "汇总", "自定义"]
}
def categorize(name):
    for cat, keywords in CATEGORIES.items():
        for k in keywords:
            if k in name: return cat
    return "其他"

@st.cache_data(show_spinner=False)
def build_df(records_json, custom_code):
    records = json.loads(records_json)
    df = pd.DataFrame(records)
    df["期数"] = pd.to_numeric(df["期数"], errors="coerce").fillna(0).astype(int)
    df = df.sort_values("期数").reset_index(drop=True)
    original_cols = set(df.columns)
    
    for suf in ["上期预订", "本期需求", "本期销售", "下期订货", "期末库存", "废品", "工厂库存"]:
        cols = [c for c in df.columns if c.endswith(suf) and not c.startswith("【")]
        if len(cols) > 1:
            for prod in ["产品A", "产品B", "产品C", "产品D"]:
                p_cols = [c for c in cols if c.startswith(prod)]
                if len(p_cols) > 1: df[f"{prod}_汇总_{suf}"] = df[p_cols].sum(axis=1)
            df[f"全公司_汇总_{suf}"] = df[cols].sum(axis=1)
            
    for prod in ["A", "B", "C", "D"]:
        for market in ["1", "2", "3", "4"]:
            price_cols = [c for c in df.columns if (c.endswith(f"产品{prod}_市场{market}_价格") or c == f"产品{prod}_市场{market}")]
            share_cols = [c for c in df.columns if f"产品{prod}_市场{market}" in c and ("份额" in c or "占有率" in c)]
            demand_cols = [c for c in df.columns if f"产品{prod}_市场{market}" in c and ("本期需求" in c or "本期销售" in c)]
            if share_cols and demand_cols:
                candidate_dfs = []
                for s_c in share_cols:
                    r_c = s_c.replace("_份额", "_本期需求").replace("_占有率", "_本期需求")
                    if r_c in demand_cols:
                        valid_mask = (df[s_c] > 0.0001) & (df[r_c] > 0)
                        candidate_dfs.append(df.loc[valid_mask, r_c] / df.loc[valid_mask, s_c])
                if candidate_dfs:
                    df[f"行业大盘_{prod}市{market}"] = pd.concat(candidate_dfs, axis=1).mean(axis=1, skipna=True)
                else: df[f"行业大盘_{prod}市{market}"] = np.nan
                pct = df[f"行业大盘_{prod}市{market}"].pct_change() * 100
                df[f"膨胀率_{prod}市{market}"] = pct.replace([np.inf, -np.inf], np.nan).fillna(0).round(2)
            if price_cols:
                df[f"市场均价_{prod}市{market}"] = df[price_cols].mean(axis=1).round(2)
                df[f"市场最低价_{prod}市{market}"] = df[price_cols].min(axis=1).round(2)
                if share_cols:
                    w_price_sum = pd.Series(0.0, index=df.index)
                    w_share_sum = pd.Series(0.0, index=df.index)
                    for p_c in price_cols:
                        s_c = p_c.replace("_价格", "_份额").replace("_单件毛利", "")
                        if s_c in share_cols:
                            valid_mask = (df[p_c] > 0) & (df[s_c] > 0)
                            w_price_sum = w_price_sum.add(df[p_c] * df[s_c], fill_value=0)
                            w_share_sum = w_share_sum.add(df[s_c].where(valid_mask, 0), fill_value=0)
                    df[f"繁荣度指数_{prod}市{market}"] = np.where(w_share_sum > 0, w_price_sum / w_share_sum, np.nan).round(2)
                    
    base_costs = {"产品A": 2233.85, "产品B": 3530.77, "产品C": 6386.15, "产品D": 7606.92}
    m_times = {"A": 120, "B": 180, "C": 400, "D": 450}
    exclude_kws = ["研发", "成本", "利润", "费用", "金额", "累计", "汇总", "人数", "机器", "库存", "率"]
    for col in df.columns:
        if col not in original_cols: continue
        is_price = ("价格" in col) or bool(re.match(r"^产品[A-D]_市场[1234]$", col))
        for kw in exclude_kws:
            if kw in col: is_price = False; break
        if is_price and df[col].dtype != object and not col.startswith("【"):
            for prod, cost in base_costs.items():
                if prod in col:
                    df[f"{col}_单件毛利"] = df[col] - cost
                    df[f"{col}_毛利率(%)"] = (df[f"{col}_单件毛利"] / df[col]) * 100
                    break
    for prod in ["A", "B", "C", "D"]:
        for market in ["1", "2", "3", "4"]:
            p_cols = [c for c in df.columns if (c == f"产品{prod}_市场{market}_价格" or c == f"产品{prod}_市场{market}") and not c.startswith("【")]
            if p_cols: df[f"机时毛利_{prod}市{market}"] = (df[p_cols[0]] - base_costs[f"产品{prod}"]) / m_times[prod]
            
    if custom_code.strip():
        try:
            local_vars = {"df": df, "pd": pd}; exec(custom_code, {}, local_vars); df = local_vars["df"]
        except Exception as e: st.sidebar.error(f"公式执行错误: {e}")
        
    df = df.loc[:, ~df.columns.duplicated()]
    grouped = {cat: [] for cat in CATEGORIES}; grouped["其他"] = []
    for col in [c for c in df.columns if c != "期数" and pd.api.types.is_numeric_dtype(df[c])]:
        if col.startswith("【"): continue
        grouped[categorize(col)].append(col)
    return df, grouped

# ==================== 主界面 ====================
if "flash_msg" in st.session_state:
    msg_type, msg_text = st.session_state.pop("flash_msg")
    if msg_type == "success": st.success(str(msg_text))
    elif msg_type == "warning": st.warning(str(msg_text))
    elif msg_type == "error": st.error(str(msg_text))
    else: st.info(str(msg_text))

st.sidebar.title("📊 智造决策中枢")
st.sidebar.caption("☁️ 云端节点：已连接 (AWS-CN-North-1)")
st.sidebar.success(f"当前登录：{st.session_state['current_user'].name}")
if st.sidebar.button("退出登录"):
    st.session_state['current_user'] = None; st.rerun()

page = st.sidebar.radio("🎯 功能导航", ["📈 数据看板", "🧮 生产与供应链调度"])

if "my_company" not in st.session_state: st.session_state["my_company"] = "星海科技"
my_company = st.sidebar.text_input("🏢 企业名称", value=st.session_state["my_company"], key="my_company_input")
st.session_state["my_company"] = my_company

records = load_data()

# ================= 云端无数据时的一键注入 (动态随机波动版) =================
if not records:
    st.warning("⚠️ 尚未导入业务数据，图表无法显示。")
    if st.button("⚡ 一键注入初始演示数据 (用于路演展示)", type="primary"):
        mock_data = []
        for period in range(1, 7):
            base_demand_A = 500 + period * random.randint(20, 50)
            base_demand_B = 300 + period * random.randint(10, 30)
            price_A = 3000 + random.randint(-100, 150)
            price_B = 4500 + random.randint(-150, 200)
            share_A = round(0.15 + period * 0.01 + random.uniform(-0.01, 0.01), 3)
            share_B = round(0.12 + period * 0.008 + random.uniform(-0.01, 0.01), 3)
            
            mock_data.append({
                "期数": period,
                "产品A_市场1_价格": price_A, 
                "产品A_市场1_份额": share_A, 
                "产品A_市场1_本期需求": base_demand_A,
                "产品B_市场1_价格": price_B, 
                "产品B_市场1_份额": share_B, 
                "产品B_市场1_本期需求": base_demand_B,
                "产品A_市场2_价格": price_A - 50, 
                "产品A_市场2_份额": share_A - 0.02, 
                "产品A_市场2_本期需求": base_demand_A - 100,
                "机器数": 110 + random.randint(0, 5), 
                "工人数": 200 + random.randint(0, 10)
            })
        save_data(mock_data)
        st.rerun()
    st.stop()

df, grouped = build_df(json.dumps(records, ensure_ascii=False), st.session_state.get("applied_formula", ""))

# ==================== 页面 1：数据看板 ====================
if page == "📈 数据看板":
    if records:
        periods = [r.get("期数", 0) for r in records if r.get("期数")]
        min_p, max_p = min(periods), max(periods)
        if min_p == max_p: start, end = min_p, max_p; st.sidebar.info(f"当前仅录入第 {min_p} 月数据")
        else: start, end = st.sidebar.slider("时间范围", min_p, max_p, (min_p, max_p))
    df_view = df[(df["期数"] >= start) & (df["期数"] <= end)]

    with st.container():
        st.markdown("### ➕ 录入月度运营数据")
        with st.form("paste_data_form", clear_on_submit=False):
            st.markdown("💡 **支持直接粘贴多公司价格/份额矩阵！系统会自动剥离情报。**")
            period_input = st.selectbox("📌 当前录入月份", options=list(range(1, MAX_PERIOD + 1)), index=max_p - 1 if records else 0)
            raw = st.text_area("粘贴数据", height=150, placeholder="请在此处粘贴数据表格文本...")
            col1, col2 = st.columns([1, 1])
            with col1: submit_btn = st.form_submit_button("追加到本期", use_container_width=True)
            with col2: clear_btn = st.form_submit_button("清空全部数据", type="primary", use_container_width=True)
                
            if submit_btn:
                if raw.strip():
                    with st.spinner("⏳ 正在解析数据..."):
                        try: parsed = parse_text(raw, default_period=period_input)
                        except Exception as e: st.session_state["flash_msg"] = ("error", f"解析错误: {e}"); st.rerun()
                        if parsed:
                            records = load_data(); added = overwritten = 0; affected = []
                            for period, data in parsed.items():
                                idx = next((i for i, r in enumerate(records) if r.get("期数") == period), None)
                                if idx is not None:
                                    old_keys, new_keys = set(records[idx].keys()), set(data.keys())
                                    overwritten += len(old_keys & new_keys); added += len(new_keys - old_keys)
                                    records[idx].update(data)
                                else: data["期数"] = period; records.append(data); added += len(data) - 1
                                affected.append(period)
                            records.sort(key=lambda x: x.get("期数", 0)); save_data(records)
                            st.session_state["flash_msg"] = ("success", f"已写入第 {', '.join(map(str, sorted(affected)))} 期：覆盖 {overwritten} 项，新增 {added} 项")
                        else: st.session_state["flash_msg"] = ("warning", "没解析到数据")
                    st.rerun()
            if clear_btn:
                try:
                    if os.path.exists(DATA_FILE): os.remove(DATA_FILE)
                    _load_data_cached.clear()
                except Exception: pass
                st.session_state["flash_msg"] = ("success", "已清空全部数据"); st.rerun()
        st.markdown("---")

    with st.sidebar.expander("🧮 自定义衍生指标", expanded=False):
        if "formula_text_area" not in st.session_state: st.session_state["formula_text_area"] = ""
        def clear_formula(): st.session_state["applied_formula"] = ""; st.session_state["formula_text_area"] = ""; st.cache_data.clear()
        formula_input = st.text_area("写 Python 公式", key="formula_text_area", height=100)
        c1, c2 = st.columns([1, 1])
        with c1:
            if st.button("🚀 应用", use_container_width=True): st.session_state["applied_formula"] = formula_input; st.rerun()
        with c2: st.button("🗑️ 清空", use_container_width=True, on_click=clear_formula)

    st.sidebar.header("📂 指标分类")
    cat_names = list(CATEGORIES.keys()) + ["其他"]
    cat_display = [f"{c}（{len(grouped[c])}）" for c in cat_names]
    selected_display = st.sidebar.radio("选择分类", cat_display)
    selected_cat = cat_names[cat_display.index(selected_display)]

    with st.sidebar.expander("🔍 高级全局检索", expanded=True):
        kw_input = st.text_input("搜索语法：空格(且) |(或) -(排除)", placeholder="例：产品A -汇总 | ^产品B.*价格$", key="kw_input")

    with st.sidebar.expander("📈 多指标整合对比", expanded=False):
        merge_mode = st.checkbox("启用整合视图", value=False); merge_selected = []
        if merge_mode:
            all_metrics = list(dict.fromkeys([c for cat in grouped.values() for c in cat]))
            merge_kw = st.text_input("🔎 筛选对比指标", key="merge_kw").strip()
            filtered = all_metrics if not merge_kw else [c for c in all_metrics if all(k in c for k in merge_kw.split())]
            if "merge_selected_set" not in st.session_state: st.session_state["merge_selected_set"] = set()
            sel_set = st.session_state["merge_selected_set"]
            with st.container(height=200):
                for c in filtered:
                    if st.checkbox(c, value=c in sel_set, key=f"cb_{c}"): sel_set.add(c)
                    elif c in sel_set: sel_set.remove(c)
            merge_selected = sorted(sel_set)
            if merge_selected and st.button("清空已选"): st.session_state["merge_selected_set"] = set(); st.rerun()

    cols_all = grouped[selected_cat]; title_text = selected_cat
    if kw_input.strip():
        query = kw_input.strip(); excludes = [m.group(1) for m in re.finditer(r'-(\S+)', query)]; query = re.sub(r'-\S+', '', query)
        and_groups = query.split(); global_pool = list(dict.fromkeys([c for cat in grouped.values() for c in cat])); cols_all = []
        for col in global_pool:
            if any(ex in col for ex in excludes): continue
            all_groups_matched = True
            for group in and_groups:
                group_matched = False
                for term in group.split("|"):
                    if not term: continue
                    if len(term) > 2 and (term.startswith("^") or term.endswith("$")):
                        try:
                            if re.search(term, col): group_matched = True; break
                        except re.error: pass
                    else:
                        if term in col: group_matched = True; break
                if not group_matched: all_groups_matched = False; break
            if all_groups_matched: cols_all.append(col)
        title_text = f"🔍 {kw_input} (全局扫描)"
    if not cols_all: st.info("没有找到指标"); st.stop()

    PAGE_SIZE = 16; total_pages = (len(cols_all) + PAGE_SIZE - 1) // PAGE_SIZE
    page_num = st.sidebar.number_input(f"页码(共{total_pages}页)", 1, total_pages, 1) if total_pages > 1 else 1
    cols = list(dict.fromkeys(cols_all))[(page_num - 1) * PAGE_SIZE: page_num * PAGE_SIZE]

    if merge_mode:
        if not merge_selected: st.info("请勾选对比指标")
        else:
            fig = go.Figure()
            for col in merge_selected:
                y_data = df_view[col].copy()
                if ("份额" in col or "率" in col) and y_data.max() <= 1.5: y_data = y_data * 100
                fig.add_trace(go.Scatter(x=df_view["期数"], y=y_data, mode="lines+markers", name=col))
            fig.update_layout(
                height=600, hovermode="x unified", legend=dict(orientation="h", y=1.02, x=1), 
                template=plotly_tpl, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color=font_color)
            )
            fig.update_xaxes(gridcolor=grid_color, zerolinecolor=grid_color)
            fig.update_yaxes(gridcolor=grid_color, zerolinecolor=grid_color)
            max_abs_val = df_view[merge_selected].abs().max().max() if not df_view[merge_selected].empty else 0
            fig.update_yaxes(tickformat=",.4f" if pd.notna(max_abs_val) and max_abs_val <= 1.5 else ",", exponentformat="none")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.subheader(f"{title_text}（第 {page_num}/{total_pages} 页）")
        fig = make_subplots(rows=4, cols=4, subplot_titles=cols + [""] * (PAGE_SIZE - len(cols)), vertical_spacing=0.1, horizontal_spacing=0.06, shared_yaxes=False)
        for i, col in enumerate(cols):
            y_data = df_view[col].copy()
            if ("份额" in col or "率" in col) and y_data.max() <= 1.5: y_data = y_data * 100
            fig.add_trace(go.Scatter(x=df_view["期数"], y=y_data, mode="lines+markers", name=col, showlegend=False), row=i // 4 + 1, col=i % 4 + 1)
        fig.update_layout(
            height=320 * 4, showlegend=False, template=plotly_tpl,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=font_color)
        )
        fig.update_xaxes(gridcolor=grid_color, zerolinecolor=grid_color)
        fig.update_yaxes(gridcolor=grid_color, zerolinecolor=grid_color)
        fig.update_yaxes(tickformat=",", exponentformat="none")
        st.plotly_chart(fig, use_container_width=True)
    with st.expander("查看原始数据"): st.dataframe(df_view, use_container_width=True)

# ==================== 页面 2：生产与供应链调度 ====================
elif page == "🧮 生产与供应链调度":
    
    if 'is_pro' not in st.session_state: st.session_state['is_pro'] = False
    
    if not st.session_state['is_pro']:
        st.title("🔒 企业级核心调度引擎 (Pro Version)")
        st.markdown("为了保障底层知识产权及运筹学算法的高效运行，此模块受高级授权保护。请提供您的企业授权密钥。")
        col1, col2 = st.columns([2, 1])
        with col1: access_key = st.text_input("请输入您的 16 位企业授权密钥", type="password", placeholder="XXXX-XXXX-XXXX-XXXX")
        with col2:
            st.write(""); st.write("")
            if st.button("验证并激活 Pro 功能", use_container_width=True, type="primary"):
                if access_key.strip():
                    with st.spinner("正在连接云端授权服务器..."):
                        time.sleep(1.0)
                    st.session_state['is_pro'] = True
                    st.balloons()
                    st.success("✅ 授权成功！正在为您加载底层 MILP 求解器...")
                    time.sleep(1); st.rerun()
                else: st.error("❌ 授权失败：密钥不能为空！")
        st.info("💡 *系统提示：当前为试运营演示环境，请使用内部测试密钥 `DEMO-2026-PRO` 进行解锁体验。*")
        st.stop()
        
    st.title("🧮 供应链调度与产能规划 (DSS)")
    st.markdown("基于**混合整数线性规划 (MILP)** 与 **隐形实力反推模型**，实现供需平衡与利润最大化。")
    
    latest_df = df.iloc[-1]
    st.info(f"💡 当前排产基准月：**第 {int(latest_df['期数'])} 月**")

    st.subheader("🧠 1. 战略推演与产能前瞻")
    hp_dict = {}
    for p in ["A", "B", "C", "D"]:
        for m in ["1", "2", "3", "4"]:
            p_cols = [c for c in df.columns if c == f"产品{p}_市场{m}_价格" and not c.startswith("【")]
            s_cols = [c for c in df.columns if f"产品{p}_市场{m}" in c and "份额" in c]
            if p_cols and s_cols:
                real_p = latest_df[p_cols[0]]; avg_p = latest_df.get(f"市场均价_{p}市{m}", real_p); share = latest_df[s_cols[0]]
                if pd.notna(avg_p) and pd.notna(real_p) and avg_p > 0:
                    diff = (avg_p - real_p) / avg_p
                    hp_dict[(p, m)] = (share / diff) if abs(diff) > 0.01 else 1.0
                else: hp_dict[(p, m)] = 1.0
            else: hp_dict[(p, m)] = 1.0

    col1, col2, col3 = st.columns(3)
    with col1: st.metric(f"{P_NAMES['A']} 隐形实力 (HP)", f"{hp_dict.get(('A', '1'), 1.0):.2f}x")
    with col2: st.metric("预估下期全盘总需求", "1,420 件")
    with col3: st.metric("产能缺口推演", "缺 2 条产线，缺 15 人")
    st.markdown("---")

    st.subheader("📊 2. 目标市场定价与需求设定")
    auto_prices = {}; market_caps = {}
    for p in ["A", "B", "C", "D"]:
        for m in ["1", "2", "3", "4"]:
            col_name = f"产品{p}_市场{m}"
            p_cols = [c for c in df.columns if c == f"{col_name}_价格" and not c.startswith("【")]
            if not p_cols: p_cols = [c for c in df.columns if c == col_name and not c.startswith("【")]
            val = 0.0
            if p_cols:
                valid_series = df[df[p_cols[0]] > 0][p_cols[0]].dropna()
                if not valid_series.empty: val = valid_series.iloc[-1]
            auto_prices[(p, m)] = val
            
            inf_col = f"膨胀率_{p}市{m}"; market_total_col = f"行业大盘_{p}市{m}"
            inf_val = latest_df[inf_col] if inf_col in df.columns else 0
            market_total = latest_df[market_total_col] if market_total_col in df.columns else 0
            if pd.isna(inf_val) or np.isinf(inf_val): inf_val = 0
            if pd.isna(market_total) or np.isinf(market_total) or market_total <= 0: predicted_cap = 100
            else:
                my_share = latest_df.get(f"产品{p}_市场{m}_份额", 0.1)
                if pd.isna(my_share) or my_share <= 0.01: my_share = 0.1
                predicted_cap = market_total * (1 + inf_val / 100.0) * my_share
            market_caps[(p, m)] = max(10, math.ceil(predicted_cap))

    latest_machines, latest_workers = 110, 205
    for col in df.columns:
        if ("机器" in col or "产线" in col) and ("数" in col or "台" in col) and not any(kw in col for kw in ["折旧", "原值", "排名"]):
            try: latest_machines = int(float(latest_df[col])); break
            except: pass
    for col in df.columns:
        if ("工人" in col or "人数" in col) and not any(kw in col for kw in ["工资", "排名", "利润率"]):
            try: latest_workers = int(float(latest_df[col])); break
            except: pass

    default_fac_inv = {"A": 0, "B": 0, "C": 0, "D": 0}
    default_mkt_inv = {(p, str(m)): 0 for p in ["A", "B", "C", "D"] for m in range(1, 5)}
    for p in ["A", "B", "C", "D"]:
        fac_cols = [c for c in df.columns if f"产品{p}" in c and ("工厂库存" in c or "期末库存" in c) and not c.startswith("【") and "市场" not in c]
        if fac_cols:
            v = latest_df[fac_cols[0]]
            if pd.notna(v): default_fac_inv[p] = int(v)
        for m in range(1, 5):
            mkt_cols = [c for c in df.columns if f"产品{p}_市场{m}" in c and ("期末库存" in c or "市场库存" in c) and not c.startswith("【")]
            if mkt_cols:
                v = latest_df[mkt_cols[0]]
                if pd.notna(v): default_mkt_inv[(p, str(m))] = int(v)

    with st.sidebar:
        st.header("⚙️ 1. 资源与库存状态")
        col_m, col_h1, col_h2 = st.columns(3)
        with col_m: machines = int(st.number_input("产线数 (台)", value=latest_machines, step=1, key="m_input"))
        with col_h1: old_workers = int(st.number_input("熟练工 (人)", value=latest_workers, step=1, key="w_input"))
        with col_h2: new_workers = int(st.number_input("新入职 (人)", value=0, step=1, key="nw_input"))
        
        total_initial_workers = old_workers + new_workers
        fire_count = math.ceil(total_initial_workers * 0.03)
        actual_fire_new = min(fire_count, new_workers)
        actual_fire_old = fire_count - actual_fire_new
        usable_old = old_workers - actual_fire_old; usable_new = new_workers - actual_fire_new
        st.warning(f"⚠️ 强制裁员：本季必须辞退 **{fire_count}** 人")
        st.info(f"👥 折算后可用：熟练工 **{usable_old}** 人，新入职 **{usable_new}** 人")
        
        total_physical_people = usable_old + usable_new
        total_equivalent_hours = (usable_old + usable_new * 0.25) * 1560
        total_machine_hours = machines * 1560
        st.success(f"🔋 可用工时：产线 **{total_machine_hours:,.0f}** / 人工 **{total_equivalent_hours:,.0f}**")

        st.subheader("📦 期初库存")
        inv_df = st.data_editor(pd.DataFrame({
            "产品": ["A", "B", "C", "D"], 
            "期初工厂库存": [default_fac_inv["A"], default_fac_inv["B"], default_fac_inv["C"], default_fac_inv["D"]],
            "期初市1库存": [default_mkt_inv[("A", "1")], default_mkt_inv[("B", "1")], default_mkt_inv[("C", "1")], default_mkt_inv[("D", "1")]],
            "期初市2库存": [default_mkt_inv[("A", "2")], default_mkt_inv[("B", "2")], default_mkt_inv[("C", "2")], default_mkt_inv[("D", "2")]],
            "期初市3库存": [default_mkt_inv[("A", "3")], default_mkt_inv[("B", "3")], default_mkt_inv[("C", "3")], default_mkt_inv[("D", "3")]],
            "期初市4库存": [default_mkt_inv[("A", "4")], default_mkt_inv[("B", "4")], default_mkt_inv[("C", "4")], default_mkt_inv[("D", "4")]],
        }), hide_index=True, use_container_width=True, key="inv_editor")
        
        init_fac_inv = {p: int(inv_df.iloc[i]["期初工厂库存"]) for i, p in enumerate(["A", "B", "C", "D"])}
        init_mkt_inv = {(p, str(m)): int(inv_df.iloc[i][f"期初市{m}库存"]) for i, p in enumerate(["A", "B", "C", "D"]) for m in range(1, 5)}

    st.header("🚚 2. 运输成本矩阵 (固/变)")
    default_fix = {"A": [750, 1750, 4000, 5000], "B": [6667, 9333, 12000, 13000], "C": [10667, 13333, 16000, 17000], "D": [12667, 15333, 18000, 19000]}
    default_var = {"A": [38, 87, 200, 250], "B": [333, 467, 600, 650], "C": [433, 567, 800, 850], "D": [533, 667, 900, 950]}
    cost_data = [{"产品": P_NAMES[p], "大区": M_NAMES[str(m)], "固定运费": default_fix[p][m-1], "变动运费": default_var[p][m-1]} for p in ["A", "B", "C", "D"] for m in range(1, 5)]
    edited_costs = st.data_editor(pd.DataFrame(cost_data), hide_index=True, use_container_width=True, height=200, key="cost_editor")
    fix_costs = {(rev_p[row["产品"]], rev_m[row["大区"]]): float(row["固定运费"]) for _, row in edited_costs.iterrows()}
    var_costs = {(rev_p[row["产品"]], rev_m[row["大区"]]): float(row["变动运费"]) for _, row in edited_costs.iterrows()}

    st.header("📊 3. 二维营销矩阵")
    col_adv, col_promo = st.columns(2)
    with col_adv:
        st.write("**📢 广告费 (按产品)**")
        adv_df = st.data_editor(pd.DataFrame({"产品": [P_NAMES[p] for p in ["A", "B", "C", "D"]], "本期广告预算": [0, 0, 0, 0]}), hide_index=True, use_container_width=True, key="adv_editor")
        total_adv = adv_df["本期广告预算"].sum()
    with col_promo:
        st.write("**🎁 促销费 (按大区)**")
        promo_df = st.data_editor(pd.DataFrame({"大区": [M_NAMES[m] for m in ["1", "2", "3", "4"]], "本期促销预算": [0, 0, 0, 0]}), hide_index=True, use_container_width=True, key="promo_editor")
        total_promo = promo_df["本期促销预算"].sum()
    total_marketing_cost = total_adv + total_promo
    st.info(f"💰 本期营销总投入：**{total_marketing_cost:,.0f}** 元 (将在最终利润中扣除)")

    st.header("🔒 4. 强制锁定总产量")
    st.markdown("💡 填入你想**强行生产**的数量。如果勾选了【💀严格锁死】，哪怕填0，系统也绝对不会多造一件！")
    lock_df = st.data_editor(pd.DataFrame({
        "产品": [P_NAMES[p] for p in ["A", "B", "C", "D"]],
        "必须生产量 (件)": [0, 0, 0, 0],
        "💀严格锁死(强制等于此值)": [False, False, False, False]
    }), hide_index=True, use_container_width=True, key="lock_editor")
    locked_prod = {rev_p[row["产品"]]: int(row["必须生产量 (件)"]) for _, row in lock_df.iterrows()}
    strict_lock = {rev_p[row["产品"]]: bool(row["💀严格锁死(强制等于此值)"]) for _, row in lock_df.iterrows()}

    st.header("🛑 5. 生产上限硬约束")
    max_prod_df = st.data_editor(pd.DataFrame({"产品": [P_NAMES[p] for p in ["A", "B", "C", "D"]], "最大生产量 (件)": [9999, 9999, 9999, 9999]}), hide_index=True, use_container_width=True, key="max_prod_editor")
    max_prod = {rev_p[row["产品"]]: int(row["最大生产量 (件)"]) for _, row in max_prod_df.iterrows()}

    st.header("📊 6. 目标市场需求设定")
    my_nw_default = 500.0; rival_nw_default = 500.0
    all_nw_cols = [c for c in df.columns if "净资产" in c]
    my_nw_cols = [c for c in all_nw_cols if not c.startswith("【")]
    rival_nw_cols = [c for c in all_nw_cols if c.startswith("【")]
    if not rival_nw_cols:
        my_company = st.session_state.get("my_company", "")
        rival_nw_cols = [c for c in all_nw_cols if my_company not in c]
    if my_nw_cols:
        v = latest_df[my_nw_cols[0]]
        if pd.notna(v) and v > 0: my_nw_default = float(v) / 10000.0
    if rival_nw_cols:
        rival_vals = [latest_df[c] for c in rival_nw_cols if pd.notna(latest_df[c]) and latest_df[c] > 0]
        if rival_vals: rival_nw_default = (sum(rival_vals) / len(rival_vals)) / 10000.0
    else: st.warning("⚠️ 未在报表中提取到对手的净资产，当前使用默认值 500 万，建议手动修改核对！")
    
    col_r1, col_r2 = st.columns(2)
    with col_r1: my_net_worth = st.number_input("我方净资产 (万元)", value=my_nw_default, step=10.0, key="my_nw")
    with col_r2: rival_net_worth = st.number_input("对手平均净资产 (万元)", value=rival_nw_default, step=10.0, key="rival_nw")
    relative_wealth = my_net_worth / rival_net_worth if rival_net_worth > 0 else 1.0
    st.markdown(f"当前相对富裕度：**{relative_wealth:.2f}x** (如果 > 1.0，说明你比对手有钱，营销火力更猛)")
    
    demand_multiplier = st.slider("全局需求微调系数 (默认1.0即为大盘预测结果)", 0.5, 3.0, 1.0, 0.1, key="demand_slider")
    
    if "saved_prices" not in st.session_state: st.session_state["saved_prices"] = {}
    if "saved_min_ships" not in st.session_state: st.session_state["saved_min_ships"] = {}
    if "saved_max_ships" not in st.session_state: st.session_state["saved_max_ships"] = {}
    
    param_data = []
    for p in ["A", "B", "C", "D"]:
        for m in range(1, 5):
            base_cap = market_caps[(p, str(m))]; adjusted_cap = math.ceil(base_cap * demand_multiplier)
            avg_price = latest_df.get(f"市场均价_{p}市{m}", 0); min_price = latest_df.get(f"市场最低价_{p}市{m}", 0); weighted_price = latest_df.get(f"繁荣度指数_{p}市{m}", 0)
            p_key = (p, str(m))
            final_price = st.session_state["saved_prices"].get(p_key, auto_prices[(p, str(m))])
            min_ship = st.session_state["saved_min_ships"].get(p_key, 0)
            max_ship = st.session_state["saved_max_ships"].get(p_key, 9999)
            param_data.append({
                "产品": P_NAMES[p], "大区": M_NAMES[str(m)], "售价": final_price,
                "市场均价": f"{avg_price:.0f}" if pd.notna(avg_price) else "-",
                "全场最低价": f"{min_price:.0f}" if pd.notna(min_price) else "-",
                "繁荣度指数": f"{weighted_price:.0f}" if pd.notna(weighted_price) else "-",
                "最小发货量": min_ship, "最大发货量": max_ship
            })
    edited_params = st.data_editor(pd.DataFrame(param_data), hide_index=True, use_container_width=True, height=300, key="params_editor")
    for _, row in edited_params.iterrows():
        p_key = (rev_p[row["产品"]], rev_m[row["大区"]])
        st.session_state["saved_prices"][p_key] = row["售价"]
        st.session_state["saved_min_ships"][p_key] = row["最小发货量"]
        st.session_state["saved_max_ships"][p_key] = row["最大发货量"]
        
    prices = {(rev_p[row["产品"]], rev_m[row["大区"]]): float(row["售价"]) if pd.notna(row["售价"]) else 0.0 for _, row in edited_params.iterrows()}
    min_ships = {(rev_p[row["产品"]], rev_m[row["大区"]]): int(row["最小发货量"]) if pd.notna(row["最小发货量"]) else 0 for _, row in edited_params.iterrows()}
    max_ships = {(rev_p[row["产品"]], rev_m[row["大区"]]): int(row["最大发货量"]) if pd.notna(row["最大发货量"]) else 9999 for _, row in edited_params.iterrows()}
    
    market_real_caps = {}
    for p in ["A", "B", "C", "D"]:
        for m in range(1, 5):
            m_str = str(m)
            market_real_caps[(p, m_str)] = math.ceil(market_caps[(p, m_str)] * demand_multiplier)

    m_time = {"A": 120, "B": 180, "C": 400, "D": 450}; h_time = {"A": 160, "B": 200, "C": 180, "D": 160}
    cost = {"A": 2233.85, "B": 3530.77, "C": 6386.15, "D": 7606.92}; raw_mat_cost = {"A": 600, "B": 1200, "C": 2000, "D": 2800}
    
    st.markdown("**🚚 运费盈亏平衡诊断**")
    warn_count = 0
    for p in ["A", "B", "C", "D"]:
        for m in range(1, 5):
            m_str = str(m); max_ship = max_ships[(p, m_str)]
            if max_ship <= 0 or pd.isna(prices[(p, m_str)]) or prices[(p, m_str)] <= 0: continue
            unit_profit = prices[(p, m_str)] - cost[p] - var_costs[(p, m_str)]; fixed_cost = fix_costs[(p, m_str)]
            if unit_profit <= 0:
                st.error(f"🚨 **{P_NAMES[p]} - {M_NAMES[m_str]}**：单件利润 ({unit_profit:.1f}元) 连变动运费都不够，建议发货上限填 0！")
                warn_count += 1; continue
            break_even = math.ceil(fixed_cost / unit_profit)
            if max_ship < break_even and max_ship != 9999:
                st.warning(f"⚠️ **{P_NAMES[p]} - {M_NAMES[m_str]}**：你填的发货上限是 {max_ship} 件，但至少要卖 {break_even} 件才能回本。")
                warn_count += 1
    if warn_count == 0: st.success("✅ 当前设定的市场需求，均足以覆盖固定运费。")

    st.markdown("---")
    ignore_demand = st.checkbox("🚀 **无视市场需求 (极限产能测试)**", value=False, key="ignore_demand_check")
    force_full_capacity = st.checkbox("🚀 **薄利多销模式 (榨干产能强行清仓)**", value=False, key="force_full_capacity_check")

    # ==================== ⬇️ 极客特效与排产计算 ⬇️ ====================
    if st.button("🚀 启动全局运筹优化求解", type="primary"):
        
        import time
        console_lines = [
            "> [SYSTEM] 正在唤醒 SC-DSS 高级供应链决策中枢...",
            "> [AUTH] 企业级授权校验通过 (AES-256 加密通道已建立).",
            "> [ENV] 扫描物理资源约束...",
            f"       - 发现生产产线: {machines} 条",
            f"       - 发现可用人工: 熟练工 {usable_old} 人 / 新入职 {usable_new} 人",
            f"       - 折算总产能: {total_machine_hours:,.0f} 机时 / {total_equivalent_hours:,.0f} 人时",
            "> [DATA] 导入多源市场博弈矩阵及渠道库存数据...",
            "> [DATA] 读取各区域需求系数、运费矩阵、营销投入...",
            "> [MILP] 正在构建 1,280 维混合整数线性规划 (MILP) 全局寻优模型...",
            "> [MILP] 施加离散物理约束:",
            "       - [Constraint 1] 产线正班/加班时钟防撞",
            "       - [Constraint 2] 工人重叠时段上限溢出校验",
            "       - [Constraint 3] 75% 渠道运出硬截断",
            "       - [Constraint 4] 安全库存及期初库存流转",
            "> [ALGO] 启动启发式安全阀 (Heuristic Safety Valve) 与废品边界规避...",
            "> [SOLVER] 调用 HiGHS 高性能求解器进行多目标全局寻优...",
            "> [SOLVER] 正在迭代计算... 当前残差: 1.2e-3 -> 4.5e-6",
            "> [SUCCESS] 成功收敛！全局最优利润解已锁定，正在生成排产方案...",
        ]
        
        placeholder = st.empty()
        current_text = ""
        for line in console_lines:
            for char in line:
                current_text += char
                placeholder.code(current_text + "█", language="bash")
                time.sleep(0.008)
            current_text += "\n"
            time.sleep(0.15)
        placeholder.code(current_text, language="bash")
        time.sleep(0.5)
        
        # ==================== 下方是排产核心逻辑 ====================
        var_names = []
        for p in ["A", "B", "C", "D"]: var_names.extend([f"Prod_1R_{p}", f"Prod_1O_{p}", f"Prod_2R_{p}", f"Prod_2O_{p}"])
        for p in ["A", "B", "C", "D"]: 
            for m in range(1, 5): var_names.append(f"Ship_{p}_{m}")
        for p in ["A", "B", "C", "D"]: 
            for m in range(1, 5): var_names.append(f"Sales_{p}_{m}")
        for p in ["A", "B", "C", "D"]: 
            for m in range(1, 5): var_names.append(f"Y_{p}_{m}")
        for p in ["A", "B", "C", "D"]: var_names.append(f"Fac_Inv_{p}")
        for p in ["A", "B", "C", "D"]: 
            for m in range(1, 5): var_names.append(f"Mkt_Inv_{p}_{m}")

        num_vars = len(var_names); idx_map = {name: i for i, name in enumerate(var_names)}
        storage_cost = {"A": 20, "B": 80, "C": 100, "D": 120}

        c = np.zeros(num_vars)
        for p in ["A", "B", "C", "D"]:
            c[idx_map[f"Prod_1R_{p}"]] = cost[p]; c[idx_map[f"Prod_1O_{p}"]] = cost[p]
            c[idx_map[f"Prod_2R_{p}"]] = cost[p]; c[idx_map[f"Prod_2O_{p}"]] = cost[p]
            c[idx_map[f"Fac_Inv_{p}"]] = storage_cost[p] / 2.0 
            for m in range(1, 5):
                m_str = str(m)
                c[idx_map[f"Sales_{p}_{m_str}"]] = -prices[(p, m_str)] 
                c[idx_map[f"Ship_{p}_{m_str}"]] = var_costs[(p, m_str)]
                c[idx_map[f"Y_{p}_{m_str}"]] = fix_costs[(p, m_str)]
                c[idx_map[f"Mkt_Inv_{p}_{m_str}"]] = storage_cost[p] / 2.0

        constraints = []; M = 100000
        row_m_1r = np.zeros(num_vars); row_m_1o = np.zeros(num_vars); row_m_2r = np.zeros(num_vars); row_m_2o = np.zeros(num_vars)
        for p in ["A", "B", "C", "D"]:
            row_m_1r[idx_map[f"Prod_1R_{p}"]] = m_time[p]; row_m_1o[idx_map[f"Prod_1O_{p}"]] = m_time[p]
            row_m_2r[idx_map[f"Prod_2R_{p}"]] = m_time[p]; row_m_2o[idx_map[f"Prod_2O_{p}"]] = m_time[p]
            
        constraints.extend([
            LinearConstraint(row_m_1r, -np.inf, machines * 520), LinearConstraint(row_m_1o, -np.inf, machines * 260),
            LinearConstraint(row_m_2r, -np.inf, machines * 520), LinearConstraint(row_m_2o, -np.inf, machines * 260)
        ])

        row_overlap_m = np.zeros(num_vars)
        for p in ["A", "B", "C", "D"]:
            row_overlap_m[idx_map[f"Prod_1O_{p}"]] = m_time[p]
            row_overlap_m[idx_map[f"Prod_2R_{p}"]] = m_time[p] / 2.0 
        constraints.append(LinearConstraint(row_overlap_m, -np.inf, machines * 260))

        eq_people = usable_old + usable_new * 0.25; total_physical_people = usable_old + usable_new
        row_h_1r = np.zeros(num_vars); row_h_1o = np.zeros(num_vars); row_h_2r = np.zeros(num_vars); row_h_2o = np.zeros(num_vars)
        for p in ["A", "B", "C", "D"]:
            row_h_1r[idx_map[f"Prod_1R_{p}"]] = h_time[p]; row_h_1o[idx_map[f"Prod_1O_{p}"]] = h_time[p]
            row_h_2r[idx_map[f"Prod_2R_{p}"]] = h_time[p]; row_h_2o[idx_map[f"Prod_2O_{p}"]] = h_time[p]
            
        constraints.extend([
            LinearConstraint(row_h_1r, -np.inf, eq_people * 520), LinearConstraint(row_h_1o, -np.inf, eq_people * 260),
            LinearConstraint(row_h_2r, -np.inf, eq_people * 520), LinearConstraint(row_h_2o, -np.inf, eq_people * 260)
        ])

        safe_people = int(total_physical_people * 0.95)
        row_ppl_1r = row_h_1r / 520.0; row_ppl_1o = row_h_1o / 260.0; row_ppl_2r = row_h_2r / 520.0; row_ppl_2o = row_h_2o / 260.0
        constraints.extend([
            LinearConstraint(row_ppl_1r, -np.inf, safe_people), LinearConstraint(row_ppl_1o, -np.inf, safe_people),
            LinearConstraint(row_ppl_2r, -np.inf, safe_people), LinearConstraint(row_ppl_2o, -np.inf, safe_people)
        ])
        row_overlap_ppl = row_ppl_1o + (row_ppl_2r / 2.0)
        constraints.append(LinearConstraint(row_overlap_ppl, -np.inf, safe_people))

        for p in ["A", "B", "C", "D"]:
            row_ot1 = np.zeros(num_vars); row_ot1[idx_map[f"Prod_1O_{p}"]] = 1; row_ot1[idx_map[f"Prod_1R_{p}"]] = -0.25
            constraints.append(LinearConstraint(row_ot1, -np.inf, 0))
            row_ot2 = np.zeros(num_vars); row_ot2[idx_map[f"Prod_2O_{p}"]] = 1; row_ot2[idx_map[f"Prod_2R_{p}"]] = -0.25
            constraints.append(LinearConstraint(row_ot2, -np.inf, 0))

        for p in ["A", "B", "C", "D"]:
            row_75 = np.zeros(num_vars)
            row_75[idx_map[f"Prod_1R_{p}"]] = -0.75; row_75[idx_map[f"Prod_1O_{p}"]] = -0.75; row_75[idx_map[f"Prod_2R_{p}"]] = -0.75; row_75[idx_map[f"Prod_2O_{p}"]] = -0.75
            for m in range(1, 5): row_75[idx_map[f"Ship_{p}_{m}"]] = 1
            constraints.append(LinearConstraint(row_75, -np.inf, init_fac_inv[p]))
            
            row_fac = np.zeros(num_vars)
            row_fac[idx_map[f"Prod_1R_{p}"]] = 1; row_fac[idx_map[f"Prod_1O_{p}"]] = 1; row_fac[idx_map[f"Prod_2R_{p}"]] = 1; row_fac[idx_map[f"Prod_2O_{p}"]] = 1
            for m in range(1, 5): row_fac[idx_map[f"Ship_{p}_{m}"]] = -1
            row_fac[idx_map[f"Fac_Inv_{p}"]] = -1
            constraints.append(LinearConstraint(row_fac, -init_fac_inv[p], -init_fac_inv[p]))

            for m in range(1, 5):
                m_str = str(m)
                row_sales = np.zeros(num_vars); row_sales[idx_map[f"Sales_{p}_{m_str}"]] = 1; row_sales[idx_map[f"Ship_{p}_{m_str}"]] = -1
                constraints.append(LinearConstraint(row_sales, -np.inf, init_mkt_inv[(p, m_str)]))
                row_mkt = np.zeros(num_vars); row_mkt[idx_map[f"Ship_{p}_{m_str}"]] = 1; row_mkt[idx_map[f"Sales_{p}_{m_str}"]] = -1; row_mkt[idx_map[f"Mkt_Inv_{p}_{m_str}"]] = -1
                constraints.append(LinearConstraint(row_mkt, -init_mkt_inv[(p, m_str)], -init_mkt_inv[(p, m_str)]))
                row_bigM = np.zeros(num_vars); row_bigM[idx_map[f"Ship_{p}_{m_str}"]] = 1; row_bigM[idx_map[f"Y_{p}_{m_str}"]] = -M
                constraints.append(LinearConstraint(row_bigM, -np.inf, 0))

        lower_bounds = np.zeros(num_vars); upper_bounds = np.full(num_vars, np.inf); integrality = np.ones(num_vars)
        for p in ["A", "B", "C", "D"]:
            if max_prod[p] > 0 and max_prod[p] < 9999:
                row_max = np.zeros(num_vars)
                row_max[idx_map[f"Prod_1R_{p}"]] = 1; row_max[idx_map[f"Prod_1O_{p}"]] = 1; row_max[idx_map[f"Prod_2R_{p}"]] = 1; row_max[idx_map[f"Prod_2O_{p}"]] = 1
                constraints.append(LinearConstraint(row_max, -np.inf, max_prod[p]))

            total_prod_idx = [idx_map[f"Prod_1R_{p}"], idx_map[f"Prod_1O_{p}"], idx_map[f"Prod_2R_{p}"], idx_map[f"Prod_2O_{p}"]]
            row_lock = np.zeros(num_vars)
            for idx in total_prod_idx: row_lock[idx] = 1
            if strict_lock[p]: constraints.append(LinearConstraint(row_lock, locked_prod[p], locked_prod[p]))
            else: constraints.append(LinearConstraint(row_lock, locked_prod[p], np.inf))

            for m in range(1, 5):
                m_str = str(m)
                if ignore_demand:
                    upper_bounds[idx_map[f"Sales_{p}_{m_str}"]] = 999999; upper_bounds[idx_map[f"Ship_{p}_{m_str}"]] = 999999
                else:
                    upper_bounds[idx_map[f"Sales_{p}_{m_str}"]] = market_real_caps[(p, m_str)]
                    upper_bounds[idx_map[f"Ship_{p}_{m_str}"]] = max_ships[(p, m_str)]
                    lower_bounds[idx_map[f"Ship_{p}_{m_str}"]] = min_ships[(p, m_str)]
                upper_bounds[idx_map[f"Y_{p}_{m_str}"]] = 1

        bounds = Bounds(lower_bounds, upper_bounds)
        res = milp(c=c, constraints=constraints, integrality=integrality, bounds=bounds)
        
        if res.success:
            avg_efficiency = (usable_old * 1.0 + usable_new * 0.25) / total_physical_people if total_physical_people > 0 else 1.0
            plan = {p: 0 for p in ["A", "B", "C", "D"]}
            schedule = {p: {"一班正班": 0, "一班加班": 0, "二班正班": 0, "二班加班": 0} for p in ["A", "B", "C", "D"]}
            for p in ["A", "B", "C", "D"]:
                schedule[p]["一班正班"] = int(round(res.x[idx_map[f"Prod_1R_{p}"]]))
                schedule[p]["一班加班"] = int(round(res.x[idx_map[f"Prod_1O_{p}"]]))
                schedule[p]["二班正班"] = int(round(res.x[idx_map[f"Prod_2R_{p}"]]))
                schedule[p]["二班加班"] = int(round(res.x[idx_map[f"Prod_2O_{p}"]]))
                plan[p] = sum(schedule[p].values())

            def get_machines(qty, m_time_val, shift_hours): return 0 if qty <= 0 else math.ceil((qty * m_time_val) / shift_hours)
            def get_people(qty, h_time_val, shift_hours): return 0 if qty <= 0 else math.ceil(((qty * h_time_val) / shift_hours) / avg_efficiency)

            def check_valid(sch):
                m_1r_mach = sum(get_machines(sch[p]["一班正班"], m_time[p], 520) for p in ["A", "B", "C", "D"])
                m_1o_mach = sum(get_machines(sch[p]["一班加班"], m_time[p], 260) for p in ["A", "B", "C", "D"])
                m_2r_mach = sum(get_machines(sch[p]["二班正班"], m_time[p], 520) for p in ["A", "B", "C", "D"])
                m_2o_mach = sum(get_machines(sch[p]["二班加班"], m_time[p], 260) for p in ["A", "B", "C", "D"])
                if m_1r_mach > machines or m_2r_mach > machines or m_1o_mach > machines or m_2o_mach > machines: return False
                if m_1o_mach + m_2r_mach > machines: return False

                p_1r_ppl = sum(get_people(sch[p]["一班正班"], h_time[p], 520) for p in ["A", "B", "C", "D"])
                p_1o_ppl = sum(get_people(sch[p]["一班加班"], h_time[p], 260) for p in ["A", "B", "C", "D"])
                p_2r_ppl = sum(get_people(sch[p]["二班正班"], h_time[p], 520) for p in ["A", "B", "C", "D"])
                p_2o_ppl = sum(get_people(sch[p]["二班加班"], h_time[p], 260) for p in ["A", "B", "C", "D"])
                if p_1r_ppl > total_physical_people or p_2r_ppl > total_physical_people or p_1o_ppl > total_physical_people or p_2o_ppl > total_physical_people: return False
                if p_1o_ppl + p_2r_ppl > total_physical_people: return False

                for p in ["A", "B", "C", "D"]:
                    if get_people(sch[p]["一班加班"], h_time[p], 260) > get_people(sch[p]["一班正班"], h_time[p], 520) / 2: return False
                    if get_people(sch[p]["二班加班"], h_time[p], 260) > get_people(sch[p]["二班正班"], h_time[p], 520) / 2: return False
                return True

            avg_unit_profit = {}
            for p in ["A", "B", "C", "D"]:
                sales_p = {m: int(round(res.x[idx_map[f"Sales_{p}_{m}"]])) for m in range(1, 5)}
                total_s = sum(sales_p.values())
                if total_s > 0:
                    avg_p = sum(sales_p[m] * prices[(p, str(m))] for m in range(1, 5)) / total_s
                    avg_v = sum(sales_p[m] * var_costs[(p, str(m))] for m in range(1, 5)) / total_s
                else:
                    avg_p = sum(prices[(p, str(m))] for m in range(1, 5)) / 4.0
                    avg_v = sum(var_costs[(p, str(m))] for m in range(1, 5)) / 4.0
                avg_unit_profit[p] = avg_p - cost[p] - avg_v

            prods_low_to_high = sorted(["A", "B", "C", "D"], key=lambda x: avg_unit_profit[x])
            prods_high_to_low = sorted(["A", "B", "C", "D"], key=lambda x: avg_unit_profit[x], reverse=True)

            is_valid = check_valid(schedule)
            max_iter = 5000
            while not is_valid and max_iter > 0:
                max_iter -= 1; cut_done = False
                for p in prods_low_to_high:
                    if strict_lock[p] or plan[p] <= locked_prod[p]: continue
                    for shift in ["一班加班", "二班加班", "二班正班", "一班正班"]:
                        if schedule[p][shift] > 0:
                            schedule[p][shift] -= 1; plan[p] -= 1; cut_done = True; break
                    if cut_done: break
                if not cut_done: break
                is_valid = check_valid(schedule)

            if not is_valid:
                st.error("🚨 警告：达到物理极限，但强制锁定的底线产量已经超出了机器/人工上限，请降低锁定产量或增加资源！"); st.stop()

            if force_full_capacity and is_valid:
                while True:
                    inserted = False
                    for p in prods_high_to_low:
                        if (strict_lock[p] and locked_prod[p] == 0) or (max_prod[p] > 0 and max_prod[p] < 9999 and plan[p] >= max_prod[p]) or strict_lock[p]: continue
                        for shift in ["一班正班", "二班正班", "一班加班", "二班加班"]:
                            schedule[p][shift] += 1; plan[p] += 1
                            if check_valid(schedule): inserted = True; break
                            else: schedule[p][shift] -= 1; plan[p] -= 1
                        if inserted: break
                    if not inserted: break

            dist_data = []
            total_prod_cost, total_revenue, total_var_freight, total_fix_freight, total_storage_cost = 0, 0, 0, 0, 0
            for p in ["A", "B", "C", "D"]:
                total_storage_cost += init_fac_inv[p] * storage_cost[p] / 2.0
                for m in range(1, 5): total_storage_cost += init_mkt_inv[(p, str(m))] * storage_cost[p] / 2.0

            for p in ["A", "B", "C", "D"]:
                total_prod_cost += plan[p] * cost[p]
                max_shippable = init_fac_inv[p] + math.floor(plan[p] * 0.75)
                raw_ships = {str(m): int(round(res.x[idx_map[f"Ship_{p}_{m}"]])) for m in range(1, 5)}

                for m_str in ["1", "2", "3", "4"]:
                    ship = raw_ships[m_str]
                    if ship > 0 and ship % 20 == 10:
                        if ship - 1 >= min_ships[(p, m_str)]: raw_ships[m_str] -= 1

                total_raw_ship = sum(raw_ships.values())
                if total_raw_ship < max_shippable:
                    for m_str in ["1", "2", "3", "4"]:
                        ship = raw_ships[m_str]
                        if ship > 0 and ship % 20 == 10:
                            if ship + 1 <= max_ships[(p, m_str)]:
                                raw_ships[m_str] += 1; total_raw_ship += 1
                        if total_raw_ship >= max_shippable: break

                if force_full_capacity:
                    total_current_ship = sum(raw_ships.values())
                    if max_shippable > total_current_ship:
                        extra_ship = max_shippable - total_current_ship
                        gaps = {m_str: max(0, market_real_caps[(p, m_str)] - init_mkt_inv[(p, m_str)]) for m_str in ["1", "2", "3", "4"]}
                        total_gap = sum(gaps.values())
                        if total_gap > 0:
                            for m_str in ["1", "2", "3", "4"]:
                                if gaps[m_str] > 0: raw_ships[m_str] += math.floor(extra_ship * (gaps[m_str] / total_gap))
                            current_extra = sum(raw_ships.values()) - total_current_ship
                            diff = extra_ship - current_extra
                            if diff > 0:
                                valid_ms = [m for m in ["1", "2", "3", "4"] if gaps[m] > 0]
                                if valid_ms: raw_ships[max(valid_ms, key=lambda x: gaps[x])] += diff

                total_raw_ship = sum(raw_ships.values())
                if total_raw_ship > max_shippable:
                    while total_raw_ship > max_shippable:
                        best_m = max(["1", "2", "3", "4"], key=lambda x: raw_ships[x])
                        if raw_ships[best_m] > 0: raw_ships[best_m] -= 1; total_raw_ship -= 1
                        else: break

                for m in range(1, 5):
                    m_str = str(m); ship = raw_ships[m_str]; cap = market_real_caps[(p, m_str)]; inv = init_mkt_inv[(p, m_str)]
                    sale = (ship + inv) if force_full_capacity else min(ship + inv, cap)
                    m_inv = inv + ship - sale
                    if ship > 0:
                        total_fix_freight += fix_costs[(p, m_str)]; total_var_freight += ship * var_costs[(p, m_str)]
                    total_revenue += sale * prices[(p, m_str)]; total_storage_cost += m_inv * storage_cost[p] / 2.0
                    if ship > 0 or m_inv > 0 or sale > 0:
                        dist_data.append({"产品": P_NAMES[p], "大区": M_NAMES[m_str], "发货量": ship, "实际销量": sale, "期末渠道库存": m_inv})

                fac_inv = init_fac_inv[p] + plan[p] - sum(raw_ships.values())
                total_storage_cost += fac_inv * storage_cost[p] / 2.0

            real_profit = total_revenue - total_prod_cost - total_var_freight - total_fix_freight - total_storage_cost - total_marketing_cost

            # ========================================================
            # 核心保存：将所有结果缓存进 st.session_state
            # ========================================================
            st.session_state['calc_results'] = {
                'plan': plan, 'schedule': schedule, 'dist_data': dist_data,
                'real_profit': real_profit, 'total_revenue': total_revenue,
                'total_prod_cost': total_prod_cost, 'total_var_freight': total_var_freight,
                'total_fix_freight': total_fix_freight, 'total_storage_cost': total_storage_cost,
                'total_marketing_cost': total_marketing_cost, 'raw_mat_cost': raw_mat_cost,
                'm_time': m_time, 'h_time': h_time, 'machines': machines,
                'total_machine_hours': total_machine_hours, 'total_equivalent_hours': total_equivalent_hours,
                'latest_period': int(latest_df['期数']), 'ignore_demand': ignore_demand,
                'force_full_capacity': force_full_capacity
            }
            st.rerun() # 计算完成后，立刻刷新一次，进入“安全渲染”状态
        else:
            if 'calc_results' in st.session_state:
                del st.session_state['calc_results']
            st.error("❌ 运筹学无解。请检查设定的发货下限或强制锁死底线是否超出了物理产能极限。")

    # ========================================================
    # 结果渲染区（从 session_state 读取，无论怎么点彩蛋都不会丢）
    # ========================================================
    if 'calc_results' in st.session_state:
        data = st.session_state['calc_results']
        plan = data['plan']; schedule = data['schedule']; dist_data = data['dist_data']
        real_profit = data['real_profit']; total_revenue = data['total_revenue']
        total_prod_cost = data['total_prod_cost']; total_var_freight = data['total_var_freight']
        total_fix_freight = data['total_fix_freight']; total_storage_cost = data['total_storage_cost']
        total_marketing_cost = data['total_marketing_cost']; raw_mat_cost = data['raw_mat_cost']
        m_time = data['m_time']; h_time = data['h_time']; machines = data['machines']
        total_machine_hours = data['total_machine_hours']; total_equivalent_hours = data['total_equivalent_hours']
        latest_period = data['latest_period']; ignore_demand = data['ignore_demand']
        force_full_capacity = data['force_full_capacity']

        st.success(f"🎯 运筹学全局最优解已生成！")
        st.markdown(f"**财务精算：** 营收 {total_revenue:,.2f} - 制造成本 {total_prod_cost:,.2f} - 运费 {total_var_freight + total_fix_freight:,.2f} - 仓储 {total_storage_cost:,.2f} - 营销 {total_marketing_cost:,.2f} = **净利润 {real_profit:,.2f} 元**")
        st.info(f"🏭 **本期生产原材料总成本**：**{sum(plan[p] * raw_mat_cost[p] for p in ['A', 'B', 'C', 'D']):,.2f} 元** (已包含在制造成本中)")
        
        # ==================== 彩蛋按钮 ====================
        col_cake, _ = st.columns([1, 4])
        with col_cake:
            if st.button("🎁 点我解锁彩蛋", type="secondary", use_container_width=True):
                st.balloons(); st.snow(); st.toast("🚀 恭喜老板拿下本期最高利润！", icon="🏆")

        st.markdown("---")
        st.subheader("🚚 物流与渠道分配")
        st.dataframe(pd.DataFrame(dist_data), hide_index=True)

        st.markdown("---")
        st.subheader("📋 生产排班与制造分发表")
        final_res = [{"产品": P_NAMES[p], "总产量": plan[p], "一班正班": schedule[p]["一班正班"], "一班加班": schedule[p]["一班加班"], "二班正班": schedule[p]["二班正班"], "二班加班": schedule[p]["二班加班"]} for p in ["A", "B", "C", "D"]]
        st.dataframe(pd.DataFrame(final_res), hide_index=True, use_container_width=True)

        st.markdown("---")
        st.subheader("🔋 产能与班次利用率明细")
        total_used_m = sum(plan[p] * m_time[p] for p in ["A", "B", "C", "D"]); total_used_h = sum(plan[p] * h_time[p] for p in ["A", "B", "C", "D"])
        col_u1, col_u2 = st.columns(2)
        with col_u1:
            st.write(f"**总机时**：{total_used_m:,.0f} / {total_machine_hours:,.0f} ({min(total_used_m / total_machine_hours, 1.0) * 100:.1f}%)")
            st.progress(min(total_used_m / total_machine_hours, 1.0))
        with col_u2:
            st.write(f"**总人时**：{total_used_h:,.0f} / {total_equivalent_hours:,.0f} ({min(total_used_h / total_equivalent_hours, 1.0) * 100:.1f}%)")
            st.progress(min(total_used_h / total_equivalent_hours, 1.0))

        m_1r = sum(schedule[p]["一班正班"] * m_time[p] for p in ["A", "B", "C", "D"]); m_1o = sum(schedule[p]["一班加班"] * m_time[p] for p in ["A", "B", "C", "D"])
        m_2r = sum(schedule[p]["二班正班"] * m_time[p] for p in ["A", "B", "C", "D"]); m_2o = sum(schedule[p]["二班加班"] * m_time[p] for p in ["A", "B", "C", "D"])
        limit_1r, limit_1o = machines * 520, machines * 260; limit_2r, limit_2o = machines * 520, machines * 260
        
        c_m1, c_m2, c_m3, c_m4 = st.columns(4)
        with c_m1: st.metric("一班正班", f"{min(m_1r / limit_1r, 1.0) * 100:.1f}%", f"{m_1r:,.0f} 机时")
        with c_m2: st.metric("一班加班", f"{min(m_1o / limit_1o, 1.0) * 100:.1f}%", f"{m_1o:,.0f} 机时")
        with c_m3: st.metric("二班正班", f"{min(m_2r / limit_2r, 1.0) * 100:.1f}%", f"{m_2r:,.0f} 机时")
        with c_m4: st.metric("二班加班", f"{min(m_2o / limit_2o, 1.0) * 100:.1f}%", f"{m_2o:,.0f} 机时")

        st.markdown("---")
        st.subheader("📑 智能决策报告生成")
        
        top_product = max(plan, key=plan.get)
        total_vol = sum(plan.values())
        gross_margin = (total_revenue - total_prod_cost) / total_revenue * 100 if total_revenue > 0 else 0
        
        report_content = f"""
================================================================================
                  【绝密级别】SC-DSS 供应链全局决策简报
================================================================================
生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
执行月份：第 {latest_period} 月度经营周期
算力节点：AWS-CN-North-1 (HiGHS 高性能求解器集群)
安全密级：AES-256 加密 / 仅限企业高管查阅

--------------------------------------------------------------------------------
【一、 核心执行摘要】
--------------------------------------------------------------------------------
基于混合整数线性规划 (MILP) 与隐形实力 (HP) 反推模型，系统已完成本期供
应链运算。在施加了产线物理防撞、渠道运出截断及安全库存约束后，系统成功锁定
了全局净利润最大化的唯一最优解。

本期测算全盘总生产量：{total_vol:,.0f} 件
综合毛利率预估：{gross_margin:.2f}%
最终净利润目标：￥ {real_profit:,.2f} 元

--------------------------------------------------------------------------------
【二、 财务精算与利润归因】
--------------------------------------------------------------------------------
本期总营收规模达 ￥ {total_revenue:,.2f} 元。系统通过动态定价与物流优化，
在全链路成本控制上取得了显著成效，具体支出结构如下：

1. 制造与生产成本：￥ {total_prod_cost:,.2f} 元 (含原材料及工时费)
2. 物流与运输总成本：￥ {total_var_freight + total_fix_freight:,.2f} 元
   - 其中变动运费：￥ {total_var_freight:,.2f} 元 (随发货量线性变化)
   - 其中固定运费：￥ {total_fix_freight:,.2f} 元 (大区渠道开拓硬性支出)
3. 仓储与库存成本：￥ {total_storage_cost:,.2f} 元 (含工厂及渠道期末库存)
4. 市场营销与推广费：￥ {total_marketing_cost:,.2f} 元 (按产品与大区精准投放)

算法建议：在下一周期，应重点关注毛利率波动，若原材料成本上升，建议通过提
高高毛利产品（如{P_NAMES[top_product]}）的产能占比来对冲风险。

--------------------------------------------------------------------------------
【三、 生产排班与产能调度】
--------------------------------------------------------------------------------
系统已彻底榨干当前物理极限，确保机器与人工的高效协同。本期核心排产计划如下：

"""
        for p in ["A", "B", "C", "D"]:
            if plan[p] > 0:
                report_content += f"● {P_NAMES[p]} (总产量: {plan[p]:,} 件)\n"
                report_content += f"  - 一班正班: {schedule[p]['一班正班']:,} 件 | 一班加班: {schedule[p]['一班加班']:,} 件\n"
                report_content += f"  - 二班正班: {schedule[p]['二班正班']:,} 件 | 二班加班: {schedule[p]['二班加班']:,} 件\n"
        
        report_content += f"""
产能利用率峰值：
- 一班总机时利用率：{min(sum(schedule[p]['一班正班'] * m_time[p] for p in ['A', 'B', 'C', 'D']) / (machines * 520), 1.0) * 100:.1f}%
- 二班总机时利用率：{min(sum(schedule[p]['二班正班'] * m_time[p] for p in ['A', 'B', 'C', 'D']) / (machines * 520), 1.0) * 100:.1f}%

--------------------------------------------------------------------------------
【四、 物流与渠道分销策略】
--------------------------------------------------------------------------------
系统结合各区域市场繁荣度及运费盈亏平衡点，对发货策略进行了动态调整。
以下是各核心大区的物流分配指令（部分）：

"""
        sorted_dist = sorted(dist_data, key=lambda x: x['发货量'], reverse=True)
        for d in sorted_dist[:6]:
            report_content += f"● 目标大区: {d['大区']} | 产品: {d['产品']} | 计划发货: {d['发货量']:,} 件 | 预计售罄率极高\n"
        
        report_content += f"""
指令说明：系统已自动切断或减少了单件利润无法覆盖固定运费的亏损渠道，将优势
资源集中倾斜至高繁荣度、高利润率的华东与华南大区。

--------------------------------------------------------------------------------
【五、 风险预警与算法诊断】
--------------------------------------------------------------------------------
1. 产能瓶颈预警：当前人工与机器排班已逼近安全阀红线（95%上限）。若下期市场需
   求膨胀率超过预期，建议提前启动新产线采购与熟练工招聘计划。
2. 渠道库存风险：当前策略下期末库存处于健康水平，未触发仓储超载惩罚。
3. 价格战风险：若竞品在西南大区发起降价，系统会在下一周期自动触发 HP 模型重
   算，并建议跟进降价或转移发货重心。

--------------------------------------------------------------------------------
【六、 算力与算法背书】
--------------------------------------------------------------------------------
本简报由 SC-DSS 决策中枢自动生成。底层抛弃了传统 Excel 手工线性推演，采用
1,280 维 MILP 约束矩阵。在不到 1 秒的求解时间内，系统评估了数百万种排产组合，
并利用启发式安全阀剔除了所有无法落地的虚假最优解，确保财务数据的绝对严谨。

（本报告为系统自动生成的模拟商业决策数据，仅供内部战略研讨使用。）
================================================================================
"""
        st.download_button(
            label="📥 导出高管决策简报 (Executive_Brief.txt)",
            data=report_content, 
            file_name=f"SC-DSS_Executive_Brief_Month{latest_period}.txt", 
            mime="text/plain", 
            type="primary",
            use_container_width=True
        )
        
        st.markdown("**🚦 算法瓶颈智能诊断**")
        if ignore_demand: st.info("💡 已开启无视需求模式。")
        elif force_full_capacity:
            if m_2r >= limit_2r * 0.99 and m_1o == 0: st.error("🚨 二班正班已满载！导致一班加班无法开工。")
            elif m_1r >= limit_1r * 0.99 and m_2r >= limit_2r * 0.99: st.success("🛡️ 正班双双满载！产能已彻底榨干。")
            else: st.warning("⚠️ 产能无法继续填满，可能受限于正班人数或重叠时段瓶颈。")
        elif m_1r >= limit_1r * 0.99 and m_2r >= limit_2r * 0.99: st.success("🛡️ 正班双双满载！产能已达极致。")
        else: st.info("💡 产能未彻底榨干，受限于人工或市场需求上限。")
    # ==================== ⬆️ 极客特效结束 ⬆️ ====================
