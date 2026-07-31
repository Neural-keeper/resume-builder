# gui.py
import sys
from pathlib import Path
from nicegui import ui

# Add project root to sys.path so 'backend' and 'frontend' imports work
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.src.master_gen import MasterManager
from views.master_view import render_master_editor
from views.modular_view import render_modular_builder

# Initialize master state manager
manager = MasterManager()

def refresh_all():
    ui.notify("Master changes saved to disk!", type="positive", position="bottom-right")

@ui.page('/')
def main_page():
    # Set app palette
    ui.colors(primary='#D16D3B', secondary='#EEB1A2', tertiary='#FFE497', quaternary='#FFFAF1', penta='#FFF8D9')
    ui.query('body').style('background-color: #FFE497')

    # Global Header Header
    with ui.header().classes('items-center justify-between bg-primary text-quaternary p-4'):
        ui.label('Resume Builder Studio').classes('text-xl font-bold')
        
        # Navigation Tabs
        with ui.tabs() as main_nav:
            nav_master = ui.tab('Master Editor', icon='edit')
            nav_modular = ui.tab('Modular Builder', icon='view_module')

        ui.button('Save Master', icon='save', on_click=lambda: (manager.save(), refresh_all())).props('flat color=white')

    # Main Tab Router
    with ui.tab_panels(main_nav, value=nav_master).classes('w-full bg-transparent'):
        
        # TAB 1: MASTER RESUME EDITOR
        with ui.tab_panel(nav_master).classes('p-0'):
            render_master_editor(manager, refresh_all)

        # TAB 2: MODULAR BUILDER & PREVIEW
        with ui.tab_panel(nav_modular).classes('p-6 bg-quaternary'):
            render_modular_builder(manager)

# Launch local Uvicorn webserver
ui.run(title='Resume Builder Studio', port=8080, reload=True)