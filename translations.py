#!/usr/bin/env python3
import os
import locale

STRINGS = {
    'en': {
        "app_title": "Cursor Theme Manager",
        "advanced": "Advanced",
        "manual": "Manual",
        "download_deps": "Download Dependencies",
        "select_mode": "Select Operation Mode",
        "convert_mode": "Convert Windows Cursor",
        "update_mode": "Update Existing XCursor Theme",
        "cobalt_section": "Windows Cursor Conversion",
        "cobalt_desc": "Cobalt converts Windows .cur/.ani files into an XCursor theme.",
        "launch_cobalt": "Launch Cobalt Converter",
        "theme_config": "Target Theme Configuration",
        "theme_name": "Theme Name:",
        "browse": "Browse...",
        "cursor_sizes": "Cursor Sizes:",
        "theme_dir": "Theme Directory:",
        "build_hyprcursor": "Build Hyprcursor Theme (for Hyprland)",
        "resize_algo": "Resize Algorithm:",
        "start_process": "Start Processing Theme",
        "execution_log": "Execution Output Log",
        "first_run_title": "First-Time Setup",
        "first_run_desc": "Would you like to check system dependencies and download required tools now?",
        "later": "Later",
        "launch_cobalt_title": "Launch Cobalt Converter",
        "launch_cobalt_desc": "Would you like to open the Cursor Reference Manual before launching Cobalt?",
        "cancel": "Cancel",
        "launch_directly": "Launch Directly",
        "open_manual_launch": "Open Manual & Launch",
        "deps_status_title": "Dependency Status",
        "deps_ok": "✔ System dependencies are installed & ready!",
        "deps_warn": "⚠ Dependencies incomplete. Please check execution output logs.",
        "manual_title": "Windows Cursor Reference Manual",
        "close": "Close",
        "error_no_name": "[Error] Please enter a Cursor Theme Name.",
        "tooltip_launch_cobalt": "Please launch Cobalt Converter first.",
        "select_theme_picker": "Select Theme Folder or index.theme File",
        "lang_code": "RU",
        "hypr_missing_title": "Hyprcursor Dependency Missing",
        "hypr_missing_desc": "Building Hyprcursor themes for Hyprland requires 'hyprcursor' (hyprcursor-util). Would you like to install it now using Polkit, or disable Hyprcursor generation?",
        "install_hypr": "Install hyprcursor",
        "skip_hypr": "Disable & Continue"
    },
    'ru': {
        "app_title": "Менеджер тем курсоров",
        "advanced": "Расширенные",
        "manual": "Справка",
        "download_deps": "Загрузить зависимости",
        "select_mode": "Выберите режим работы",
        "convert_mode": "Конвертировать курсор Windows",
        "update_mode": "Обновить тему XCursor",
        "cobalt_section": "Конвертация курсоров Windows",
        "cobalt_desc": "Cobalt конвертирует файлы Windows .cur/.ani в тему XCursor.",
        "launch_cobalt": "Запустить конвертер Cobalt",
        "theme_config": "Настройка целевой темы",
        "theme_name": "Имя темы:",
        "browse": "Обзор...",
        "cursor_sizes": "Размеры курсора:",
        "theme_dir": "Каталог темы:",
        "build_hyprcursor": "Собрать тему Hyprcursor (для Hyprland)",
        "resize_algo": "Алгоритм масштабирования:",
        "start_process": "Начать обработку темы",
        "execution_log": "Журнал выполнения",
        "first_run_title": "Первоначальная настройка",
        "first_run_desc": "Хотите проверить системные зависимости и загрузить необходимые инструменты сейчас?",
        "later": "Позже",
        "launch_cobalt_title": "Запуск конвертера Cobalt",
        "launch_cobalt_desc": "Хотите открыть справочник по курсорам перед запуском Cobalt?",
        "cancel": "Отмена",
        "launch_directly": "Запустить напрямую",
        "open_manual_launch": "Открыть справочник и запустить",
        "deps_status_title": "Статус зависимостей",
        "deps_ok": "✔ Системные зависимости установлены и готовы!",
        "deps_warn": "⚠ Зависимости неполные. Пожалуйста, проверьте журнал выполнения.",
        "manual_title": "Справочник по курсорам Windows",
        "close": "Закрыть",
        "error_no_name": "[Ошибка] Пожалуйста, введите имя темы курсоров.",
        "tooltip_launch_cobalt": "Пожалуйста, сначала запустите конвертер Cobalt.",
        "select_theme_picker": "Выберите папку темы или файл index.theme",
        "lang_code": "EN",
        "hypr_missing_title": "Отсутствует зависимость Hyprcursor",
        "hypr_missing_desc": "Сборка тем Hyprcursor для Hyprland требует пакет 'hyprcursor' (hyprcursor-util). Хотите установить его сейчас через Polkit или пропустить сборку Hyprcursor?",
        "install_hypr": "Установить hyprcursor",
        "skip_hypr": "Отключить Hyprcursor и продолжить"
    }
}

CURRENT_LANG = "en"

def detect_system_lang():
    try:
        lang = os.environ.get("LANG", "") or locale.getdefaultlocale()[0] or ""
        return "ru" if lang.startswith("ru") else "en"
    except Exception:
        return "en"

CURRENT_LANG = detect_system_lang()

def set_lang(lang_code):
    global CURRENT_LANG
    if lang_code in STRINGS:
        CURRENT_LANG = lang_code

def get_lang():
    return CURRENT_LANG

def t(key, default=None):
    dict_lang = STRINGS.get(CURRENT_LANG, STRINGS["en"])
    return dict_lang.get(key, STRINGS["en"].get(key, default or key))
