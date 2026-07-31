# frontend/src/views/master_view.py
from nicegui import ui

def render_master_editor(manager, refresh_all_cb):
    """Renders the master resume editor drawer and forms."""
    
    # Outer row container for sidebar navigation + content area
    with ui.row().classes('w-full no-wrap items-start gap-0'):
        
        # LEFT NAVIGATION SIDEBAR (Replaced ui.left_drawer with a clean sidebar card)
        with ui.card().classes('w-64 min-h-[calc(100vh-80px)] p-4 bg-secondary rounded-none shadow-none'):
            ui.label('Master Sections').classes('text-xs font-bold text-slate-800 uppercase mb-2')
            with ui.tabs().props('vertical color=primary').classes('w-full') as section_tabs:
                tab_profile = ui.tab('Profile & Summaries', icon='person')
                tab_exp = ui.tab('Experience', icon='work')
                tab_edu = ui.tab('Education', icon='school')
                tab_proj = ui.tab('Projects', icon='code')
                tab_skills = ui.tab('Skills', icon='build')
                tab_certs = ui.tab('Certifications', icon='card_membership')

        # MAIN CONTENT TAB PANELS
        with ui.tab_panels(section_tabs, value=tab_profile).classes('bg-quaternary flex-grow p-6 min-h-[calc(100vh-80px)]'):

            # ---------------------------------------------------------------------
            # 1. PROFILE & SUMMARIES TAB
            # ---------------------------------------------------------------------
            with ui.tab_panel(tab_profile):
                ui.label('Personal Profile').classes('text-2xl font-bold mb-4')
                
                p_data = manager.data.get('profile', {})
                with ui.grid(columns=2).classes('w-full gap-4'):
                    name_input = ui.input('Full Name', value=p_data.get('name', ''))
                    email_input = ui.input('Email', value=p_data.get('email', ''))
                    title_input = ui.input('Target Title', value=p_data.get('title', ''))
                    phone_input = ui.input('Phone', value=p_data.get('phone', ''))
                    loc_input = ui.input('Location', value=p_data.get('location', ''))

                def save_profile():
                    manager.update_profile(
                        name=name_input.value,
                        email=email_input.value,
                        title=title_input.value,
                        phone=phone_input.value,
                        location=loc_input.value
                    )
                    refresh_all_cb()

                ui.button('Save Profile', on_click=save_profile, icon='save').classes('mt-4 bg-primary text-white')

                ui.separator().classes('my-8')
                ui.label('Targeted Summaries').classes('text-xl font-bold mb-2')

                @ui.refreshable
                def render_summaries():
                    for key, summary_text in manager.data.get('summaries', {}).items():
                        with ui.card().classes('w-full mb-3 p-4 bg-slate-50'):
                            with ui.row().classes('justify-between items-center w-full'):
                                ui.label(key).classes('font-bold text-lg text-primary')
                                def make_delete(k=key):
                                    return lambda: (manager.delete_summary(k), render_summaries.refresh())
                                ui.button(icon='delete', on_click=make_delete()).props('flat color=negative dense')
                            
                            ui.label(summary_text).classes('text-slate-600')

                render_summaries()

                with ui.row().classes('w-full items-center gap-2 mt-4'):
                    new_key = ui.input('Target Role (e.g. data_engineer)')
                    new_text = ui.textarea('Summary Text').classes('flex-grow')
                    
                    def add_sum():
                        if new_key.value and new_text.value:
                            manager.add_summary(new_key.value, new_text.value)
                            new_key.value = ''
                            new_text.value = ''
                            render_summaries.refresh()
                    
                    ui.button('Add Summary', on_click=add_sum, icon='add')

            # ---------------------------------------------------------------------
            # 2. WORK EXPERIENCE TAB
            # ---------------------------------------------------------------------
            with ui.tab_panel(tab_exp):
                ui.label('Work Experience').classes('text-2xl font-bold mb-4')

                @ui.refreshable
                def render_experiences():
                    for exp in manager.data.get('experiences', []):
                        with ui.card().classes('w-full mb-4 p-4'):
                            with ui.row().classes('justify-between w-full'):
                                ui.label(f"{exp.get('role', '')} @ {exp.get('company', '')}").classes('font-bold text-lg')
                                def make_delete_exp(exp_id=exp['id']):
                                    return lambda: (manager.delete_work_experience(exp_id), render_experiences.refresh())
                                ui.button(icon='delete', on_click=make_delete_exp()).props('flat color=negative dense')

                            ui.label(f"{exp.get('dates', '')} | {exp.get('location', '')}").classes('text-sm text-slate-500 mb-2')
                            
                            with ui.row().classes('gap-1 mb-2'):
                                for tag in exp.get('tags', []):
                                    ui.chip(tag).props('dense outline')

                            ui.label('Bullets:').classes('font-medium text-sm mt-2')
                            for b in exp.get('bullets', []):
                                ui.label(f"• {b}").classes('text-slate-700 text-sm pl-2')

                render_experiences()

                ui.separator().classes('my-6')
                ui.label('Add New Experience').classes('text-xl font-bold mb-2')
                
                with ui.column().classes('w-full gap-2'):
                    c_company = ui.input('Company')
                    c_role = ui.input('Role / Title')
                    with ui.row().classes('w-full gap-4'):
                        c_dates = ui.input('Dates (e.g., Jan 2022 - Present)').classes('flex-grow')
                        c_loc = ui.input('Location (e.g., Remote / NY)').classes('flex-grow')
                    c_tags = ui.input('Tags (comma separated)').classes('w-full')
                    c_bullets = ui.textarea('Bullets (one per line)').classes('w-full')

                    def submit_exp():
                        tags_list = [t.strip() for t in c_tags.value.split(',') if t.strip()]
                        bullets_list = [b.strip() for b in c_bullets.value.split('\n') if b.strip()]
                        manager.add_work_experience(
                            company=c_company.value,
                            role=c_role.value,
                            dates=c_dates.value,
                            location=c_loc.value,
                            tags=tags_list,
                            bullets=bullets_list
                        )
                        c_company.value = c_role.value = c_dates.value = c_loc.value = c_tags.value = c_bullets.value = ''
                        render_experiences.refresh()

                    ui.button('Add Work Experience', on_click=submit_exp, icon='add').classes('mt-2')

            # ---------------------------------------------------------------------
            # 3. EDUCATION TAB
            # ---------------------------------------------------------------------
            with ui.tab_panel(tab_edu):
                ui.label('Education').classes('text-2xl font-bold mb-4')

                @ui.refreshable
                def render_education():
                    for ed in manager.data.get('education', []):
                        with ui.card().classes('w-full mb-4 p-4'):
                            with ui.row().classes('justify-between w-full'):
                                ui.label(f"{ed.get('degree', '')} in {ed.get('major', '')}").classes('font-bold text-lg')
                                def make_del_ed(ed_id=ed['id']):
                                    return lambda: (manager.delete_education(ed_id), render_education.refresh())
                                ui.button(icon='delete', on_click=make_del_ed()).props('flat color=negative dense')

                            ui.label(f"{ed.get('university', '')} ({ed.get('start_year', '')} - {ed.get('end_year', '')})").classes('text-slate-600')

                render_education()

                ui.separator().classes('my-6')
                ui.label('Add Education').classes('text-xl font-bold mb-2')
                
                with ui.column().classes('w-full gap-2'):
                    e_uni = ui.input('University / Institution')
                    e_degree = ui.input('Degree (e.g., B.S.)')
                    e_major = ui.input('Major')
                    e_minor = ui.input('Minor (Optional)')
                    with ui.row().classes('w-full gap-4'):
                        e_start = ui.input('Start Year')
                        e_end = ui.input('End Year')

                    def submit_edu():
                        manager.add_education(
                            university=e_uni.value,
                            degree=e_degree.value,
                            major=e_major.value,
                            minor=e_minor.value or None,
                            start_year=e_start.value,
                            end_year=e_end.value,
                            bullets=[]
                        )
                        e_uni.value = e_degree.value = e_major.value = e_minor.value = e_start.value = e_end.value = ''
                        render_education.refresh()

                    ui.button('Add Education', on_click=submit_edu, icon='add').classes('mt-2')

            # ---------------------------------------------------------------------
            # 4. PROJECTS TAB
            # ---------------------------------------------------------------------
            with ui.tab_panel(tab_proj):
                ui.label('Projects').classes('text-2xl font-bold mb-4')

                @ui.refreshable
                def render_projects():
                    for proj in manager.data.get('projects', []):
                        with ui.card().classes('w-full mb-4 p-4'):
                            with ui.row().classes('justify-between w-full'):
                                ui.label(proj.get('title', '')).classes('font-bold text-lg')
                                def make_del_proj(pid=proj['id']):
                                    return lambda: (manager.delete_project(pid), render_projects.refresh())
                                ui.button(icon='delete', on_click=make_del_proj()).props('flat color=negative dense')

                            ui.label(proj.get('description', '')).classes('text-slate-700 mb-2')
                            if proj.get('link'):
                                ui.link(proj['link'], proj['link'], new_tab=True).classes('text-sm mb-2')

                render_projects()

                ui.separator().classes('my-6')
                ui.label('Add Project').classes('text-xl font-bold mb-2')

                with ui.column().classes('w-full gap-2'):
                    p_title = ui.input('Project Title')
                    p_desc = ui.textarea('Description')
                    p_link = ui.input('Link (Optional)')
                    p_tags = ui.input('Tags (comma separated)')

                    def submit_proj():
                        tags_list = [t.strip() for t in p_tags.value.split(',') if t.strip()]
                        manager.add_project(
                            title=p_title.value,
                            description=p_desc.value,
                            link=p_link.value,
                            tags=tags_list
                        )
                        p_title.value = p_desc.value = p_link.value = p_tags.value = ''
                        render_projects.refresh()

                    ui.button('Add Project', on_click=submit_proj, icon='add').classes('mt-2')

            # ---------------------------------------------------------------------
            # 5. SKILLS TAB
            # ---------------------------------------------------------------------
            with ui.tab_panel(tab_skills):
                ui.label('Skills').classes('text-2xl font-bold mb-4')

                @ui.refreshable
                def render_skills():
                    for category, skill_list in manager.data.get('skills', {}).items():
                        with ui.card().classes('w-full mb-4 p-4'):
                            ui.label(category.capitalize()).classes('font-bold text-md mb-2 text-primary')
                            with ui.row().classes('gap-2 items-center'):
                                for skill in skill_list:
                                    def make_rem_skill(c=category, s=skill):
                                        return lambda: (manager.remove_skill(c, s), render_skills.refresh())
                                    ui.chip(skill, removable=True, on_click=make_rem_skill())

                render_skills()

                ui.separator().classes('my-6')
                ui.label('Add Skill').classes('text-xl font-bold mb-2')

                with ui.row().classes('w-full items-center gap-2'):
                    sk_cat = ui.input('Category (e.g. languages, frameworks)')
                    sk_name = ui.input('Skill Name (e.g. Python)')

                    def submit_skill():
                        if sk_cat.value and sk_name.value:
                            manager.add_skill(sk_cat.value.lower().strip(), sk_name.value.strip())
                            sk_name.value = ''
                            render_skills.refresh()

                    ui.button('Add Skill', on_click=submit_skill, icon='add')

            # ---------------------------------------------------------------------
            # 6. CERTIFICATIONS TAB
            # ---------------------------------------------------------------------
            with ui.tab_panel(tab_certs):
                ui.label('Certifications').classes('text-2xl font-bold mb-4')

                @ui.refreshable
                def render_certs():
                    for cert in manager.data.get('certifications', []):
                        with ui.card().classes('w-full mb-4 p-4'):
                            with ui.row().classes('justify-between w-full'):
                                ui.label(cert.get('name', '')).classes('font-bold text-lg')
                                def make_del_cert(cid=cert['id']):
                                    return lambda: (manager.delete_certification(cid), render_certs.refresh())
                                ui.button(icon='delete', on_click=make_del_cert()).props('flat color=negative dense')

                            ui.label(f"Issuer: {cert.get('issuer', '')} | Issued: {cert.get('date', '')}").classes('text-slate-600')

                render_certs()

                ui.separator().classes('my-6')
                ui.label('Add Certification').classes('text-xl font-bold mb-2')

                with ui.column().classes('w-full gap-2'):
                    ct_name = ui.input('Certification Name')
                    ct_issuer = ui.input('Issuer (e.g., AWS, Coursera)')
                    ct_date = ui.input('Date Obtained')

                    def submit_cert():
                        manager.add_certification(
                            name=ct_name.value,
                            issuer=ct_issuer.value,
                            date_obtained=ct_date.value
                        )
                        ct_name.value = ct_issuer.value = ct_date.value = ''
                        render_certs.refresh()

                    ui.button('Add Certification', on_click=submit_cert, icon='add').classes('mt-2')