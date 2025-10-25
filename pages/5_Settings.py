"""
Settings page for LLM configuration and other app settings.
"""
import streamlit as st
from datetime import datetime
from src.db import get_db
from src.ui import t, use_language_selector

# Initialize
use_language_selector()

st.title("⚙️ " + t("settings.title"))
st.write(t("settings.subtitle"))

db = get_db()

# LLM Configuration Section
st.header(t("settings.llm.header"))
st.write(t("settings.llm.description"))

# Get current active config
active_config = db.fetchone(
    "SELECT * FROM llm_configs WHERE is_active = 1"
)

# LLM Configuration Form
with st.expander(t("settings.llm.add_config"), expanded=not active_config):
    st.subheader(t("settings.llm.form_title"))
    
    col1, col2 = st.columns(2)
    
    with col1:
        provider = st.selectbox(
            t("settings.llm.provider_label"),
            options=["openai", "anthropic"],
            format_func=lambda x: {
                "openai": "OpenAI (GPT)",
                "anthropic": "Anthropic (Claude)"
            }[x],
            help=t("settings.llm.provider_help"),
            key="provider_select"
        )
    
    with col2:
        # Model options based on provider
        if provider == "openai":
            model_options = [
                "gpt-4-turbo-preview",
                "gpt-4",
                "gpt-4-1106-preview",
                "gpt-3.5-turbo",
                "gpt-3.5-turbo-16k"
            ]
            default_idx = 0
        else:
            model_options = [
                "claude-3-5-sonnet-20241022",
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307"
            ]
            default_idx = 0
        
        model = st.selectbox(
            t("settings.llm.model_label"),
            options=model_options,
            index=default_idx,
            help=t("settings.llm.model_help"),
            key="model_select"
        )
    
    api_key = st.text_input(
        t("settings.llm.api_key_label"),
        type="password",
        help=t("settings.llm.api_key_help"),
        key="api_key_input"
    )
    
    col_btn1, col_btn2 = st.columns([1, 3])
    with col_btn1:
        submitted = st.button(
            t("settings.llm.save_button"),
            type="primary",
            use_container_width=True
        )
    
    if submitted:
        if not api_key:
            st.error(t("settings.llm.api_key_required"))
        else:
            db.execute("UPDATE llm_configs SET is_active = 0")
            now = datetime.now().isoformat()
            db.execute(
                """INSERT INTO llm_configs 
                   (provider, model, api_key, is_active, created_at, updated_at)
                   VALUES (?, ?, ?, 1, ?, ?)""",
                (provider, model, api_key, now, now)
            )
            st.success(t("settings.llm.save_success"))
            st.rerun()

# Display current active configuration
if active_config:
    st.divider()
    st.subheader(t("settings.llm.current_config"))
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        provider_display = {
            "openai": "OpenAI (GPT)",
            "anthropic": "Anthropic (Claude)"
        }.get(active_config['provider'], active_config['provider'])
        st.metric(t("settings.llm.provider_label"), provider_display)
    
    with col2:
        st.metric(t("settings.llm.model_label"), active_config['model'])
    
    with col3:
        masked_key = active_config['api_key'][:8] + "..." + active_config['api_key'][-4:]
        st.metric(t("settings.llm.api_key_label"), masked_key)
    
    st.caption(t("settings.llm.config_updated", date=active_config['updated_at']))
    
    if st.button(t("settings.llm.delete_button"), type="secondary"):
        db.execute("DELETE FROM llm_configs WHERE id = ?", (active_config['id'],))
        st.success(t("settings.llm.delete_success"))
        st.rerun()

# All saved configurations
st.divider()
st.subheader(t("settings.llm.all_configs"))

all_configs = db.fetchall(
    "SELECT * FROM llm_configs ORDER BY created_at DESC"
)

if all_configs:
    for config in all_configs:
        with st.expander(
            f"{'✅ ' if config['is_active'] else ''}🤖 {config['provider'].upper()} - {config['model']}",
            expanded=False
        ):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**{t('settings.llm.provider_label')}:** {config['provider']}")
                st.write(f"**{t('settings.llm.model_label')}:** {config['model']}")
                masked_key = config['api_key'][:8] + "..." + config['api_key'][-4:]
                st.write(f"**{t('settings.llm.api_key_label')}:** {masked_key}")
                st.write(f"**{t('settings.llm.created')}:** {config['created_at']}")
                status_text = '✅ ' + t('settings.llm.active') if config['is_active'] else t('settings.llm.inactive')
                st.write(f"**{t('settings.llm.status')}:** {status_text}")
            
            with col2:
                if not config['is_active']:
                    if st.button(
                        t("settings.llm.activate_button"),
                        key=f"activate_{config['id']}"
                    ):
                        db.execute("UPDATE llm_configs SET is_active = 0")
                        db.execute(
                            "UPDATE llm_configs SET is_active = 1, updated_at = ? WHERE id = ?",
                            (datetime.now().isoformat(), config['id'])
                        )
                        st.success(t("settings.llm.activate_success"))
                        st.rerun()
                
                if st.button(
                    t("settings.llm.delete_button"),
                    key=f"delete_{config['id']}",
                    type="secondary"
                ):
                    db.execute("DELETE FROM llm_configs WHERE id = ?", (config['id'],))
                    st.success(t("settings.llm.delete_success"))
                    st.rerun()
else:
    st.info(t("settings.llm.no_configs"))

# Test LLM Connection
st.divider()
st.subheader(t("settings.llm.test_header"))

if active_config:
    test_text = st.text_area(
        t("settings.llm.test_input_label"),
        value="Buy AAPL when 50-day SMA crosses above 200-day SMA",
        height=100
    )
    
    if st.button(t("settings.llm.test_button")):
        with st.spinner(t("settings.llm.test_spinner")):
            try:
                from src.strategy import NLParser
                
                llm_config = {
                    'provider': active_config['provider'],
                    'model': active_config['model'],
                    'api_key': active_config['api_key']
                }
                
                parser = NLParser(use_llm=True, llm_config=llm_config)
                human, strategy_dict, code = parser.parse_with_llm(test_text)
                
                st.success(t("settings.llm.test_success"))
                
                with st.expander(t("settings.llm.test_show_results")):
                    st.write("**Human Readable:**")
                    st.text(human)
                    st.write("**JSON:**")
                    st.json(strategy_dict)
                    st.write("**Code (first 500 chars):**")
                    st.code(code[:500] + "...", language="python")
                    
            except Exception as e:
                st.error(t("settings.llm.test_error", error=str(e)))
else:
    st.info(t("settings.llm.test_no_config"))
