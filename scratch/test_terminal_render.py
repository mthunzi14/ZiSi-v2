import zisi_terminal

try:
    panel = zisi_terminal.build_active_positions_panel()
    print("ACTIVE_PANEL_RENDER_SUCCESS")
except Exception as e:
    import traceback
    print("RENDER_ERROR:", e)
    traceback.print_exc()
