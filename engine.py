#!/usr/bin/env python3
import os
import shutil
import subprocess
import tempfile
import re

CONFIG_TEMPLATE = """#!/bin/bash
PATH_TO_ANI_CUR_CURSORS="Windows-Cursors"
PATH_TO_XCURSOR="{target_theme_dir}/cursors"
PATH_TO_ADAPT_XCURSOR="XCursor-Adapt"
PATH_TO_TEMPLATE="Template"
PATH_TO_INSTALL="{home_dir}/.local/share/icons/"

CONVERT_WINDOWS_CURSOR=0
CURSOR_SIZES=({cursor_sizes})

CONVERTING=0
INSTALL_CURSOR_PACK=1
REINSTALL_PACK=1
PACK_NAME="{theme_name}"
PACK_DESCRIPTION="Description"

declare -A CURSOR_ACTIONS
CURSOR_ACTIONS=(
  ["Normal"]="default arrow left_ptr top_left_arrow"
  ["Link"]="pointer hand1 hand2 pointing_hand 9d800788f1b08800ae810202380a0822 e29285e634086352946a0e7090d73106 "
  ["Text"]="text vertical-text ibeam xterm"
  ["Busy"]="wait watch"
  ["Help"]="help question_arrow whats_this 5c6cd98b3f3ebcb1f9c7f1c204630408 d9ce0ab605698f320427677b458ad60b"
  ["Move"]="grabbing all-scroll fleur size_all"
  ["Unavailable"]="dnd-no-drop no-drop not-allowed circle crossed_circle forbidden"
  ["Working"]="progress half-busy left_ptr_watch 00000000000000020006000e7e9ffc3f 08e8e1c95fe2fc01f976f1e063a24ccd 3ecb610c1bf2410f44200f48c40d3599"
  ["Precision"]="crosshair cross tcross"
  ["Pin"]="copy openhand dnd-copy grab 1081e37283d90000800003c07f3ef6bf 6407b0e94181790501fd1e167b474872 b66166c04f8c3109214a4fbd64a50fc8"
  ["Diagonal1"]="size_fdiag nw-resize nwse-resize se-resize size-fdiag"
  ["Diagonal2"]="size_bdiag ne-resize nesw-resize size-bdiag sw-resize"
  ["Horizontal"]="col-resize size_hor e-resize ew-resize h_double_arrow left_ptr_help sb_h_double_arrow size-hor split_h w-resize"
  ["Vertical"]="row-resize size_ver n-resize ns-resize sb_v_double_arrow size-ver split_v s-resize v_double_arrow 00008160000006810000408080010102"
  ["Alternate"]="dnd-move dnd-none alias link closedhand move fcf21c00b30f7e3f83fe0dfd12e71cff 4498f0e0c1937ffe01fd06f973665830 9081237383d90e509aa00f00170e968f 3085a0e285430894940527032f8b26df 640fb0e74195791501fd1ed57b41487f a2a266d0498c3104214a47bd64ab0fc8"
  ["Handwriting"]="color-picker draft pencil"
  ["Person"]="context-menu"
)
"""

def is_first_run(base_dir):
    deps_file = os.path.join(base_dir, ".deps_status")
    return not os.path.isfile(deps_file)

def mark_deps_complete(base_dir):
    deps_file = os.path.join(base_dir, ".deps_status")
    with open(deps_file, "w") as f:
        f.write("dependencies_met=true\n")

def check_system_deps_met():
    deps = [
        "win2xcur",
        "pyside6",
        "bc",
        "imagemagick",
        "xorg-xcursorgen",
        "python-pillow",
        "gtk3",
        "git",
        "python-gobject"
    ]
    for pkg in deps:
        res = subprocess.run(["pacman", "-Q", pkg], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if res.returncode != 0:
            return False

    return shutil.which("yay") is not None and shutil.which("git") is not None

def check_hyprcursor_installed():
    return shutil.which("hyprcursor-util") is not None or subprocess.run(["pacman", "-Q", "hyprcursor"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0

def install_hyprcursor(log_cb):
    log_cb("[Hyprcursor] Installing hyprcursor package using pkexec...\n")
    return run_cmd_log(["pkexec", "pacman", "-S", "--needed", "--noconfirm", "hyprcursor"], log_cb)

def run_cmd_log(cmd, log_cb, cwd=None):
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=cwd)
    for line in iter(process.stdout.readline, ''):
        log_cb(line)
    process.stdout.close()
    return process.wait()

def parse_theme_info(selected_path):
    if os.path.isfile(selected_path):
        theme_dir = os.path.dirname(selected_path)
        index_file = selected_path
    else:
        theme_dir = selected_path
        index_file = os.path.join(theme_dir, "index.theme")

    theme_name = os.path.basename(theme_dir)

    if os.path.isfile(index_file):
        try:
            with open(index_file, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    if line.startswith("Name="):
                        parsed = line.split("=", 1)[1].strip()
                        if parsed:
                            theme_name = parsed
                        break
        except Exception:
            pass

    return theme_name, theme_dir

def resolve_theme_dir(theme_name):
    home = os.path.expanduser("~")
    p1 = os.path.join(home, ".local", "share", "icons", theme_name)
    p2 = os.path.join(home, ".icons", theme_name)
    if os.path.isdir(p1): return p1
    if os.path.isdir(p2): return p2
    return p1

def setup_repositories(base_dir, log_cb):
    m_dir = os.path.join(base_dir, "xcursor-massive-resize")
    c_dir = os.path.join(base_dir, "Cobalt")

    if not os.path.isdir(m_dir):
        log_cb("[Setup] Cloning xcursor-massive-resize...\n")
        run_cmd_log(["git", "clone", "https://github.com/Katze-942/xcursor-massive-resize", m_dir, "--depth=1"], log_cb)

    if not os.path.isdir(c_dir):
        log_cb("[Setup] Cloning Cobalt...\n")
        run_cmd_log(["git", "clone", "https://github.com/PxRyzl/Cobalt/", c_dir, "--depth=1"], log_cb)
        
        main_py = os.path.join(c_dir, "main.py")
        if os.path.isfile(main_py):
            with open(main_py, "r") as f:
                content = f.read()
            if "QT_QPA_PLATFORMTHEME" not in content:
                log_cb("[Setup] Modifying Cobalt main.py to enable GTK3 file picker...\n")
                code = 'import os\nos.environ["QT_QPA_PLATFORMTHEME"] = "gtk3"\n'
                with open(main_py, "w") as f:
                    f.write(code + content)

    return m_dir, c_dir

def build_hyprcursor(target_theme_dir, theme_name, resize_algo, log_cb):
    if not check_hyprcursor_installed():
        raise FileNotFoundError("hyprcursor-util is not installed.")

    log_cb(f"[Hyprcursor] Compiling theme with algorithm '{resize_algo}'...\n")
    with tempfile.TemporaryDirectory(prefix="hypr_ext_") as tmp_ext, \
         tempfile.TemporaryDirectory(prefix="hypr_bld_") as tmp_bld:

        run_cmd_log(["hyprcursor-util", "--extract", target_theme_dir, "--output", tmp_ext], log_cb)

        subdirs = [os.path.join(tmp_ext, d) for d in os.listdir(tmp_ext) if os.path.isdir(os.path.join(tmp_ext, d))]
        work_dir = subdirs[0] if subdirs else tmp_ext

        index_theme = os.path.join(target_theme_dir, "index.theme")
        parsed_name = theme_name
        if os.path.isfile(index_theme):
            with open(index_theme, "r") as f:
                for line in f:
                    if line.startswith("Name="):
                        parsed_name = line.split("=", 1)[1].strip()
                        break

        manifest = os.path.join(work_dir, "manifest.hl")
        if os.path.isfile(manifest):
            with open(manifest, "r") as f:
                mc = f.read()
            mc = re.sub(r"^name = .*", f"name = {parsed_name}", mc, flags=re.MULTILINE)
            with open(manifest, "w") as f:
                f.write(mc)

        hypr_dir = os.path.join(work_dir, "hyprcursors")
        for root, _, files in os.walk(hypr_dir):
            for file in files:
                if file == "meta.hl":
                    meta_path = os.path.join(root, file)
                    with open(meta_path, "r") as f:
                        m_content = f.read()
                    if "resize_algorithm" in m_content:
                        m_content = re.sub(r"^resize_algorithm = .*", f"resize_algorithm = {resize_algo}", m_content, flags=re.MULTILINE)
                    else:
                        m_content += f"\nresize_algorithm = {resize_algo}\n"
                    with open(meta_path, "w") as f:
                        f.write(m_content)

        run_cmd_log(["hyprcursor-util", "--create", work_dir, "--output", tmp_bld], log_cb)

        b_subdirs = [os.path.join(tmp_bld, d) for d in os.listdir(tmp_bld) if os.path.isdir(os.path.join(tmp_bld, d))]
        compiled_dir = b_subdirs[0] if b_subdirs else tmp_bld

        shutil.copytree(os.path.join(compiled_dir, "hyprcursors"), os.path.join(target_theme_dir, "hyprcursors"), dirs_exist_ok=True)
        shutil.copy2(os.path.join(compiled_dir, "manifest.hl"), os.path.join(target_theme_dir, "manifest.hl"))
        log_cb("[Hyprcursor] Build finished!\n")

def process_massive_resize(m_dir, target_theme_dir, theme_name, cursor_sizes_str, log_cb):
    log_cb("[Resize] Configuring xcursor-massive-resize...\n")
    config_file = os.path.join(m_dir, "config.sh")
    home_dir = os.path.expanduser("~")

    sizes = [s.strip() for s in cursor_sizes_str.replace(',', ' ').split() if s.strip().isdigit()]
    formatted_sizes = " ".join(sizes) if sizes else "16 24 32 48 64 72 96 128 256"

    content = CONFIG_TEMPLATE.format(
        target_theme_dir=target_theme_dir,
        home_dir=home_dir,
        theme_name=theme_name,
        cursor_sizes=formatted_sizes
    )

    with open(config_file, "w") as f:
        f.write(content)

    log_cb(f"[Resize] Target cursor sizes: {formatted_sizes}\n")
    log_cb("[Resize] Running cursor_converting.sh...\n")
    run_cmd_log(["bash", os.path.join(m_dir, "cursor_converting.sh")], log_cb, cwd=m_dir)

    adapt_dir = os.path.join(m_dir, "XCursor-Adapt")
    if os.path.isdir(adapt_dir) and os.listdir(adapt_dir):
        target_cursors = os.path.join(target_theme_dir, "cursors")
        os.makedirs(target_cursors, exist_ok=True)
        for item in os.listdir(adapt_dir):
            src = os.path.join(adapt_dir, item)
            dst = os.path.join(target_cursors, item)
            if os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dst)
        log_cb(f"[Resize] Updated multi-resolution cursors installed in {target_cursors}\n")
