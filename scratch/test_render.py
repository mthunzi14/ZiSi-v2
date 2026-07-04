import zisi_terminal
from rich.console import Console

def test():
    print("Loading file states...")
    zisi_terminal.sync_file_states()
    
    print("Creating layout...")
    layout = zisi_terminal.make_layout()
    
    print("Updating panels...")
    layout["header"].update(zisi_terminal.build_header_panel())
    layout["metrics"].update(zisi_terminal.build_metrics_panel())
    layout["prices"].update(zisi_terminal.build_spot_prices_panel())
    layout["regime"].update(zisi_terminal.build_regime_panel())
    layout["active_panel"].update(zisi_terminal.build_active_positions_panel())
    layout["closed_panel"].update(zisi_terminal.build_closed_positions_panel())
    layout["logs_panel"].update(zisi_terminal.build_logs_panel())
    
    print("Attempting to render layout to Console (180x45)...")
    console = Console(width=180, height=45)
    try:
        # Measure or render
        with console.capture() as capture:
            console.print(layout)
        print("Render succeeded! Capture length:", len(capture.get()))
    except Exception as e:
        print("Render failed with exception:", type(e), e)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test()
