#!/usr/bin/env python3
import os
import sys
import atexit
import subprocess
import threading
import gi

gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk, GLib

import engine
from translations import t, set_lang, get_lang
from ui_guide import create_manual_content_widget

CSS_STYLES = b"""
.app-window {
    background-color: @theme_bg_color;
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.12);
}

.modal-backdrop {
    background-color: rgba(0, 0, 0, 0.65);
}

.modal-card {
    background-color: @theme_bg_color;
    border-radius: 14px;
    border: 1px solid rgba(255, 255, 255, 0.15);
    padding: 20px;
    box-shadow: 0 12px 36px rgba(0, 0, 0, 0.6);
}

@keyframes pulse-glow {
    0% {
        background-color: rgba(53, 132, 228, 0.2);
        box-shadow: 0 0 4px rgba(53, 132, 228, 0.5);
    }
    50% {
        background-color: rgba(53, 132, 228, 0.75);
        box-shadow: 0 0 16px rgba(53, 132, 228, 1.0);
        color: #ffffff;
    }
    100% {
        background-color: rgba(53, 132, 228, 0.2);
        box-shadow: 0 0 4px rgba(53, 132, 228, 0.5);
    }
}

.pulsing-glow {
    animation: pulse-glow 1.5s infinite ease-in-out;
    font-weight: bold;
    border-radius: 6px;
}
"""

class AppWindow(Gtk.Window):
    def __init__(self):
        super().__init__()
        self.set_decorated(False)
        self.set_default_size(650, 540)
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.cobalt_processes = []
        self.cobalt_has_launched = False

        atexit.register(self.cleanup_cobalt)
        self.connect("destroy", self.on_destroy)

        self.apply_custom_css()

        # Root Overlay Container
        self.overlay = Gtk.Overlay()
        self.add(self.overlay)

        # Base Application Container
        base_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        base_container.get_style_context().add_class("app-window")
        base_container.connect("button-press-event", self.on_window_drag)
        self.overlay.add(base_container)

        # Main Body Padding
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        main_box.set_property("margin", 14)
        base_container.pack_start(main_box, True, True, 0)

        # Top Control Row
        top_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

        self.lbl_title = Gtk.Label()
        top_bar.pack_start(self.lbl_title, False, False, 0)

        # Language Switcher Button
        self.btn_lang = Gtk.Button()
        self.btn_lang.connect("clicked", self.on_toggle_language)
        top_bar.pack_start(self.btn_lang, False, False, 0)

        # Advanced Toggle Button
        self.btn_adv = Gtk.ToggleButton()
        self.btn_adv.connect("toggled", self.on_advanced_toggled)
        top_bar.pack_end(self.btn_adv, False, False, 0)

        self.btn_manual = Gtk.Button()
        self.btn_manual.connect("clicked", lambda w: self.open_manual())
        top_bar.pack_end(self.btn_manual, False, False, 0)

        self.btn_recheck = Gtk.Button()
        self.btn_recheck.connect("clicked", lambda w: self.run_deps_check(force=True))
        top_bar.pack_end(self.btn_recheck, False, False, 0)

        main_box.pack_start(top_bar, False, False, 0)

        # 1. Operation Mode
        self.mode_frame = Gtk.Frame()
        mode_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        mode_box.set_property("margin", 10)
        mode_box.set_halign(Gtk.Align.CENTER)
        mode_box.get_style_context().add_class("linked")

        self.radio_convert = Gtk.RadioButton.new_with_label(None, "")
        self.radio_convert.set_mode(False)

        self.radio_update = Gtk.RadioButton.new_with_label_from_widget(self.radio_convert, "")
        self.radio_update.set_mode(False)

        self.radio_convert.connect("toggled", self.on_mode_changed)

        mode_box.pack_start(self.radio_convert, False, False, 0)
        mode_box.pack_start(self.radio_update, False, False, 0)
        self.mode_frame.add(mode_box)
        main_box.pack_start(self.mode_frame, False, False, 0)

        # 2. Cobalt Launcher Panel
        self.cobalt_frame = Gtk.Frame()
        cobalt_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        cobalt_box.set_property("margin", 10)

        self.lbl_cobalt = Gtk.Label(xalign=0)
        self.btn_launch_cobalt = Gtk.Button()
        self.btn_launch_cobalt.connect("clicked", self.on_cobalt_click)

        cobalt_box.pack_start(self.lbl_cobalt, False, False, 0)
        cobalt_box.pack_start(self.btn_launch_cobalt, False, False, 0)
        self.cobalt_frame.add(cobalt_box)
        main_box.pack_start(self.cobalt_frame, False, False, 0)

        # 3. Theme Configuration Grid
        self.theme_frame = Gtk.Frame()
        self.grid = Gtk.Grid()
        self.grid.set_property("margin", 10)
        self.grid.set_column_spacing(10)
        self.grid.set_row_spacing(8)

        # Row 0: Theme Name & Browse
        self.lbl_name_label = Gtk.Label(xalign=0)
        self.grid.attach(self.lbl_name_label, 0, 0, 1, 1)
        name_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.entry_name = Gtk.Entry()
        self.entry_name.set_placeholder_text("e.g. MyConvertedTheme")
        self.entry_name.set_hexpand(True)

        self.btn_pick_theme = Gtk.Button()
        self.btn_pick_theme.connect("clicked", self.on_browse_theme_picker)

        name_box.pack_start(self.entry_name, True, True, 0)
        name_box.pack_start(self.btn_pick_theme, False, False, 0)
        self.grid.attach(name_box, 1, 0, 1, 1)

        # Row 1: Target Cursor Sizes Configuration
        self.lbl_sizes_label = Gtk.Label(xalign=0)
        self.grid.attach(self.lbl_sizes_label, 0, 1, 1, 1)
        self.entry_sizes = Gtk.Entry()
        self.entry_sizes.set_text("16, 24, 32, 48, 64, 72, 96, 128, 256")
        self.grid.attach(self.entry_sizes, 1, 1, 1, 1)

        # Row 2: Theme Directory (Advanced Only)
        self.lbl_dir_label = Gtk.Label(xalign=0)
        self.btn_chooser = Gtk.FileChooserButton(title="", action=Gtk.FileChooserAction.SELECT_FOLDER)
        self.grid.attach(self.lbl_dir_label, 0, 2, 1, 1)
        self.grid.attach(self.btn_chooser, 1, 2, 1, 1)

        # Row 3 & 4: Hyprland Options
        self.chk_hypr = Gtk.CheckButton()
        self.chk_hypr.set_active(True)
        self.chk_hypr.connect("toggled", lambda w: self.box_algo.set_sensitive(w.get_active()))
        self.grid.attach(self.chk_hypr, 0, 3, 2, 1)

        self.box_algo = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.lbl_algo_label = Gtk.Label()
        self.box_algo.pack_start(self.lbl_algo_label, False, False, 0)
        self.combo_algo = Gtk.ComboBoxText()
        for algo in ["nearest", "bilinear", "none"]:
            self.combo_algo.append(algo, algo)
        self.combo_algo.set_active(0)
        self.box_algo.pack_start(self.combo_algo, False, False, 0)
        self.grid.attach(self.box_algo, 0, 4, 2, 1)

        self.theme_frame.add(self.grid)
        main_box.pack_start(self.theme_frame, False, False, 0)

        # Action Button
        self.btn_process = Gtk.Button()
        self.btn_process.get_style_context().add_class("suggested-action")
        self.btn_process.connect("clicked", self.on_start_process)
        main_box.pack_start(self.btn_process, False, False, 0)

        # Execution Output Log (Advanced Only)
        self.log_expander = Gtk.Expander()
        log_scrolled = Gtk.ScrolledWindow()
        log_scrolled.set_min_content_height(120)
        self.txt_log = Gtk.TextView()
        self.txt_log.set_editable(False)
        self.log_buffer = self.txt_log.get_buffer()
        log_scrolled.add(self.txt_log)
        self.log_expander.add(log_scrolled)
        main_box.pack_start(self.log_expander, True, True, 0)

        self.current_overlay_widget = None

        # Apply translations & initial layout state
        self.refresh_ui_text()

        self.show_all()
        self.set_advanced_visible(False)
        self.update_theme_config_sensitivity()

        GLib.idle_add(self.check_first_run)

    def apply_custom_css(self):
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(CSS_STYLES)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def refresh_ui_text(self):
        self.lbl_title.set_markup(f"<b>{t('app_title')}</b>")
        self.btn_lang.set_label(t('lang_code'))
        self.btn_adv.set_label(t('advanced'))
        self.btn_manual.set_label(t('manual'))
        self.btn_recheck.set_label(t('download_deps'))

        self.mode_frame.set_label(f" {t('select_mode')} ")
        self.radio_convert.set_label(t('convert_mode'))
        self.radio_update.set_label(t('update_mode'))

        self.cobalt_frame.set_label(f" {t('cobalt_section')} ")
        self.lbl_cobalt.set_text(t('cobalt_desc'))
        self.btn_launch_cobalt.set_label(t('launch_cobalt'))

        self.theme_frame.set_label(f" {t('theme_config')} ")
        self.lbl_name_label.set_text(t('theme_name'))
        self.btn_pick_theme.set_label(t('browse'))
        self.lbl_sizes_label.set_text(t('cursor_sizes'))
        self.lbl_dir_label.set_text(t('theme_dir'))
        self.chk_hypr.set_label(t('build_hyprcursor'))
        self.lbl_algo_label.set_text(t('resize_algo'))
        self.btn_process.set_label(t('start_process'))
        self.log_expander.set_label(t('execution_log'))

        self.update_theme_config_sensitivity()

    def on_toggle_language(self, widget):
        new_lang = "ru" if get_lang() == "en" else "en"
        set_lang(new_lang)
        self.refresh_ui_text()

    def cleanup_cobalt(self):
        for proc in self.cobalt_processes:
            if proc and proc.poll() is None:
                try:
                    proc.terminate()
                    proc.wait(timeout=1)
                except Exception:
                    try:
                        proc.kill()
                    except Exception:
                        pass
        self.cobalt_processes.clear()

    def on_destroy(self, widget):
        self.cleanup_cobalt()
        Gtk.main_quit()

    def on_window_drag(self, widget, event):
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 1:
            clicked_widget = Gtk.get_event_widget(event)
            if clicked_widget and isinstance(clicked_widget, (Gtk.Button, Gtk.ToggleButton, Gtk.Entry, Gtk.Switch, Gtk.RadioButton, Gtk.ComboBox, Gtk.FileChooserButton, Gtk.Expander)):
                return False
            self.begin_move_drag(event.button, int(event.x_root), int(event.y_root), event.time)
            return True
        return False

    def show_in_app_modal(self, title, description_or_widget, buttons):
        if self.current_overlay_widget:
            self.overlay.remove(self.current_overlay_widget)

        backdrop = Gtk.EventBox()
        backdrop.get_style_context().add_class("modal-backdrop")

        center_align = Gtk.Alignment.new(0.5, 0.5, 0.0, 0.0)
        backdrop.add(center_align)

        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        card.get_style_context().add_class("modal-card")
        card.set_size_request(460, -1)

        lbl_title = Gtk.Label()
        lbl_title.set_markup(f"<b><big>{title}</big></b>")
        lbl_title.set_xalign(0)
        card.pack_start(lbl_title, False, False, 0)

        if isinstance(description_or_widget, str):
            lbl_desc = Gtk.Label(label=description_or_widget)
            lbl_desc.set_xalign(0)
            lbl_desc.set_line_wrap(True)
            card.pack_start(lbl_desc, False, False, 0)
        else:
            card.pack_start(description_or_widget, True, True, 0)

        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        btn_box.set_halign(Gtk.Align.END)

        def close_modal():
            if self.current_overlay_widget:
                self.overlay.remove(self.current_overlay_widget)
                self.current_overlay_widget = None

        for btn_label, callback, is_suggested in buttons:
            btn = Gtk.Button(label=btn_label)
            if is_suggested:
                btn.get_style_context().add_class("suggested-action")

            def make_handler(cb):
                def handler(w):
                    close_modal()
                    if cb:
                        cb()
                return handler

            btn.connect("clicked", make_handler(callback))
            btn_box.pack_start(btn, False, False, 0)

        card.pack_start(btn_box, False, False, 0)
        center_align.add(card)

        self.current_overlay_widget = backdrop
        self.overlay.add_overlay(backdrop)
        backdrop.show_all()

    def set_advanced_visible(self, visible):
        self.lbl_dir_label.set_visible(visible)
        self.btn_chooser.set_visible(visible)
        self.log_expander.set_visible(visible)

    def on_advanced_toggled(self, toggle_button):
        self.set_advanced_visible(toggle_button.get_active())

    def update_theme_config_sensitivity(self):
        is_convert_mode = self.radio_convert.get_active()
        if is_convert_mode and not self.cobalt_has_launched:
            self.theme_frame.set_sensitive(False)
            self.btn_process.set_sensitive(False)
            self.theme_frame.set_tooltip_text(t('tooltip_launch_cobalt'))
        else:
            self.theme_frame.set_sensitive(True)
            self.btn_process.set_sensitive(True)
            self.theme_frame.set_tooltip_text(None)

    def append_log(self, text):
        def _append():
            end_iter = self.log_buffer.get_end_iter()
            self.log_buffer.insert(end_iter, text)
            self.txt_log.scroll_to_iter(self.log_buffer.get_end_iter(), 0.0, False, 0.0, 0.0)
        GLib.idle_add(_append)

    def open_manual(self):
        manual_widget = create_manual_content_widget()
        self.show_in_app_modal(
            t('manual_title'),
            manual_widget,
            [(t('close'), None, True)]
        )

    def on_mode_changed(self, widget):
        self.cobalt_frame.set_visible(self.radio_convert.get_active())
        self.update_theme_config_sensitivity()

    def on_browse_theme_picker(self, widget):
        dialog = Gtk.FileChooserDialog(
            title=t('select_theme_picker'),
            parent=self,
            action=Gtk.FileChooserAction.OPEN,
            use_header_bar=True
        )
        dialog.add_buttons(f"_{t('cancel')}", Gtk.ResponseType.CANCEL, "_Open", Gtk.ResponseType.OK)

        icons_dir = os.path.expanduser("~/.local/share/icons")
        if not os.path.isdir(icons_dir):
            os.makedirs(icons_dir, exist_ok=True)
        dialog.set_current_folder(icons_dir)

        res = dialog.run()
        if res == Gtk.ResponseType.OK:
            selected_path = dialog.get_filename()
            dialog.destroy()
            if selected_path:
                t_name, t_dir = engine.parse_theme_info(selected_path)
                self.entry_name.set_text(t_name)
                self.btn_chooser.set_filename(t_dir)
                self.append_log(f"[Picker] Selected Theme '{t_name}' at '{t_dir}'\n")
        else:
            dialog.destroy()

    def check_first_run(self):
        if engine.is_first_run(self.script_dir):
            self.show_in_app_modal(
                t('first_run_title'),
                t('first_run_desc'),
                [
                    (t('later'), None, False),
                    (t('download_deps'), lambda: self.run_deps_check(force=False), True)
                ]
            )

    def run_deps_check(self, force=False):
        def task():
            self.append_log("[Setup] Running dependency check...\n")
            script_path = os.path.join(self.script_dir, "scripts", "install_deps.sh")
            res = engine.run_cmd_log(["bash", script_path, "true"], self.append_log)
            if res == 0:
                engine.setup_repositories(self.script_dir, self.append_log)
                engine.mark_deps_complete(self.script_dir)
                self.append_log("[Setup] Dependencies and repositories ready!\n")

            def notify_complete():
                if engine.check_system_deps_met():
                    self.show_in_app_modal(
                        t('deps_status_title'),
                        t('deps_ok'),
                        [("OK", None, True)]
                    )
                else:
                    self.show_in_app_modal(
                        t('deps_status_title'),
                        t('deps_warn'),
                        [("OK", None, True)]
                    )

            GLib.idle_add(notify_complete)

        threading.Thread(target=task, daemon=True).start()

    def on_cobalt_click(self, widget):
        def start_cobalt():
            def task():
                _, c_dir = engine.setup_repositories(self.script_dir, self.append_log)
                self.append_log("[Info] Launching Cobalt GUI...\n")
                proc = subprocess.Popen([sys.executable, "main.py"], cwd=c_dir)
                self.cobalt_processes.append(proc)
                self.cobalt_has_launched = True

                GLib.idle_add(self.update_theme_config_sensitivity)

                GLib.idle_add(lambda: self.btn_manual.get_style_context().add_class("pulsing-glow"))
                proc.wait()
                GLib.idle_add(lambda: self.btn_manual.get_style_context().remove_class("pulsing-glow"))

            threading.Thread(target=task, daemon=True).start()

        def open_manual_and_launch():
            self.open_manual()
            start_cobalt()

        self.show_in_app_modal(
            t('launch_cobalt_title'),
            t('launch_cobalt_desc'),
            [
                (t('cancel'), None, False),
                (t('launch_directly'), start_cobalt, False),
                (t('open_manual_launch'), open_manual_and_launch, True)
            ]
        )

    def on_start_process(self, widget):
        theme_name = self.entry_name.get_text().strip()
        chosen_path = self.btn_chooser.get_filename()
        cursor_sizes_str = self.entry_sizes.get_text().strip()

        if not theme_name:
            self.append_log(f"{t('error_no_name')}\n")
            return

        target_dir = chosen_path if chosen_path else engine.resolve_theme_dir(theme_name)

        def task():
            self.append_log(f"[Build] Processing theme at: {target_dir}\n")
            m_dir, _ = engine.setup_repositories(self.script_dir, self.append_log)

            if self.chk_hypr.get_active():
                algo = self.combo_algo.get_active_text()
                engine.build_hyprcursor(target_dir, theme_name, algo, self.append_log)

            engine.process_massive_resize(m_dir, target_dir, theme_name, cursor_sizes_str, self.append_log)
            self.append_log(f"\n[Success] Finished processing {theme_name}!\n")

        threading.Thread(target=task, daemon=True).start()
