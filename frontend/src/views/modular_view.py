# frontend/src/views/modular_view.py
import os
from nicegui import ui
from backend.src.pdf_gen import generate_typst_resume
from backend.src.profile_man import ProfileManager
from frontend.src.state.modular_manager import ModularManagerState


def render_modular_builder(master_manager):
    """Renders the non-destructive sub-profile builder & live preview using ModularManagerState."""
    # Initialize state manager backed by master_manager
    state = ModularManagerState(master_manager)

    with ui.column().classes('w-full gap-4'):
        
        # =====================================================================
        # TOP TOOLBAR: SUB-PROFILE MANAGEMENT & EXPORT
        # =====================================================================
        with ui.card().classes('w-full p-4 bg-slate-100 border border-slate-300'):
            with ui.row().classes('w-full items-center justify-between gap-4'):
                
                # Profile Dropdown Selector
                with ui.row().classes('items-center gap-2 flex-grow'):
                    ui.label('Active Sub-Profile:').classes('font-bold text-slate-700')
                    
                    profile_options = ProfileManager.list_profiles()
                    profile_select = ui.select(
                        options=profile_options,
                        value=profile_options[0] if profile_options else None,
                        label='Select Preset'
                    ).classes('w-64 bg-white')

                # Action Buttons
                with ui.row().classes('items-center gap-2'):
                    
                    # LOAD PROFILE
                    def handle_load():
                        if not profile_select.value:
                            ui.notify("Select a profile to load.", type="warning")
                            return
                        
                        if state.load_preset(profile_select.value):
                            title_input.value = state.target_title
                            render_controls.refresh()
                            render_preview.refresh()
                            ui.notify(f"Loaded '{profile_select.value}'!", type="positive")

                    ui.button('Load', icon='folder_open', on_click=handle_load).props('outline color=primary')

                    # SAVE / SAVE AS
                    def open_save_dialog():
                        with ui.dialog() as dialog, ui.card().classes('p-6 w-96'):
                            ui.label('Save Sub-Profile').classes('text-lg font-bold mb-2')
                            name_input = ui.input('Profile Name', value=state.active_profile_name).classes('w-full')
                            
                            def do_save():
                                if name_input.value:
                                    if state.save_preset(name_input.value):
                                        profile_select.options = ProfileManager.list_profiles()
                                        profile_select.value = name_input.value
                                        ui.notify(f"Saved '{name_input.value}'!", type="positive")
                                        dialog.close()

                            with ui.row().classes('justify-end w-full gap-2 mt-4'):
                                ui.button('Cancel', on_click=dialog.close).props('flat')
                                ui.button('Save', on_click=do_save, icon='save').classes('bg-primary text-white')
                        
                        dialog.open()

                    ui.button('Save Preset', icon='save', on_click=open_save_dialog).classes('bg-primary text-white')

                    # DELETE
                    def handle_delete():
                        if profile_select.value:
                            ProfileManager.delete_profile(profile_select.value)
                            ui.notify(f"Deleted profile '{profile_select.value}'", type="info")
                            profile_select.options = ProfileManager.list_profiles()
                            profile_select.value = profile_select.options[0] if profile_select.options else None

                    ui.button(icon='delete', on_click=handle_delete).props('flat color=negative')

                    # EXPORT TO PDF VIA TYPST
                    def export_pdf():
                        # Gets experience objects with local bullet overrides applied
                        filtered_experiences = state.get_effective_experiences()
                        output_path = "output_resume.pdf"
                        
                        success = generate_typst_resume(
                            profile=master_manager.data.get('profile', {}),
                            experiences=filtered_experiences,
                            target_title=state.target_title,
                            output_pdf_path=output_path
                        )

                        if success and os.path.exists(output_path):
                            ui.notify("PDF Generated Successfully!", type="positive")
                            filename = f"{state.target_title.replace(' ', '_')}_Resume.pdf"
                            ui.download(output_path, filename=filename)
                        else:
                            ui.notify("Typst PDF generation failed. Ensure Typst CLI or package is installed.", type="negative")

                    ui.button('Export PDF', icon='picture_as_pdf', on_click=export_pdf).classes('bg-emerald-600 text-white ml-2')

        # =====================================================================
        # MAIN WORKSPACE: SELECTION CONTROLS & LIVE PREVIEW
        # =====================================================================
        with ui.row().classes('w-full gap-6 items-start mt-2'):
            
            # LEFT COLUMN: Controls
            with ui.column().classes('w-1/2 gap-4'):
                ui.label('Modular Target Controls').classes('text-xl font-bold text-primary')
                
                title_input = ui.input(
                    'Target Role / Version Title', 
                    value=state.target_title,
                    on_change=lambda e: setattr(state, 'target_title', e.value) or render_preview.refresh()
                ).classes('w-full')

                @ui.refreshable
                def render_controls():
                    ui.label('Toggle Experiences & Fine-Tune Bullets').classes('font-bold text-lg mt-2')

                    for exp in master_manager.data.get('experiences', []):
                        exp_id = exp['id']
                        
                        with ui.card().classes('w-full p-4 border border-slate-200 bg-white mb-2'):
                            # Toggle for inclusion using ModularManagerState
                            def make_toggle(e, eid=exp_id):
                                state.toggle_experience(eid, e.value)
                                render_preview.refresh()

                            is_checked = exp_id in state.selected_exp_ids
                            ui.checkbox(f"{exp['role']} @ {exp['company']}", value=is_checked, on_change=make_toggle)

                            # Fine-tuning local override text area
                            ui.label('Fine-tune Bullets (Local Override)').classes('text-xs font-semibold text-slate-500 mt-2')
                            
                            default_bullets = "\n".join(exp.get('bullets', []))
                            current_text = state.overrides.get(exp_id, default_bullets)

                            def make_override(eid=exp_id):
                                return lambda e: (state.set_override(eid, e.value), render_preview.refresh())

                            ui.textarea(
                                value=current_text, 
                                on_change=make_override(exp_id)
                            ).classes('w-full text-xs')

                render_controls()

            # RIGHT COLUMN: Live Resume Preview Panel
            with ui.column().classes('w-1/2 p-6 bg-quaternary border border-slate-300 rounded shadow-md min-h-[500px]'):
                ui.label('Live Resume Preview').classes('font-bold text-slate-400 border-b pb-1 w-full text-xs uppercase tracking-wider')

                @ui.refreshable
                def render_preview():
                    profile = master_manager.data.get('profile', {})
                    
                    ui.label(profile.get('name', 'Your Name')).classes('text-2xl font-bold text-primary')
                    ui.label(f"{profile.get('email', '')} | {profile.get('phone', '')} | {profile.get('location', '')}").classes('text-xs text-slate-600 mb-2')
                    
                    if state.target_title:
                        ui.label(f"Targeting: {state.target_title}").classes('text-xs italic text-secondary font-semibold mb-4')

                    ui.separator().classes('my-2')
                    ui.label('WORK EXPERIENCE').classes('font-bold text-sm text-slate-800 tracking-wide')
                    
                    # Read compiled effective experiences directly from ModularManagerState
                    for exp in state.get_effective_experiences():
                        with ui.column().classes('gap-0 mb-3 w-full'):
                            with ui.row().classes('justify-between w-full'):
                                ui.label(f"{exp['role']} - {exp['company']}").classes('font-semibold text-xs')
                                ui.label(exp.get('dates', '')).classes('text-xs text-slate-500')
                            
                            for bullet in exp.get('bullets', []):
                                if bullet.strip():
                                    ui.label(f"• {bullet.strip()}").classes('text-xs text-slate-700 pl-3')

                render_preview()