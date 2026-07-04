import zisi_terminal

def test():
    print("Loading file states...")
    zisi_terminal.sync_file_states()
    
    print("Creating layout...")
    layout = zisi_terminal.make_layout()
    
    print("Updating header...")
    header_panel = zisi_terminal.build_header_panel()
    layout["header"].update(header_panel)
    print("Header renderable type:", type(layout["header"].renderable))
    
    print("Updating metrics...")
    metrics_panel = zisi_terminal.build_metrics_panel()
    layout["metrics"].update(metrics_panel)
    print("Metrics renderable type:", type(layout["metrics"].renderable))
    
    print("Updating closed panel...")
    closed_panel = zisi_terminal.build_closed_positions_panel()
    layout["closed_panel"].update(closed_panel)
    print("Closed panel renderable type:", type(layout["closed_panel"].renderable))

if __name__ == "__main__":
    test()
