"""
Strategy Builder page for creating and editing strategies.
"""
import streamlit as st
import json
from datetime import datetime
from src.strategy import NLParser, StrategyCompiler, CodeValidator
from src.models import Strategy
from src.db import get_db
from src.ui import t, use_language_selector
import uuid


def show():
    """Display the strategy builder page."""
    use_language_selector()

    st.title("📈 " + t("builder.title"))
    st.write(t("builder.subtitle"))
    
    # Initialize database connection first
    db = get_db()
    
    # Load active LLM config from database
    llm_config_row = db.fetchone("SELECT * FROM llm_configs WHERE is_active = 1")
    llm_config = None
    if llm_config_row:
        llm_config = {
            'provider': llm_config_row['provider'],
            'model': llm_config_row['model'],
            'api_key': llm_config_row['api_key']
        }
    
    # Initialize components
    parser = NLParser(use_llm=bool(llm_config), llm_config=llm_config)
    compiler = StrategyCompiler()
    validator = CodeValidator()
    
    # Initialize session state for three formats
    if 'human_readable' not in st.session_state:
        st.session_state.human_readable = ""
    if 'json_definition' not in st.session_state:
        st.session_state.json_definition = None
    if 'backtrader_code' not in st.session_state:
        st.session_state.backtrader_code = ""
    
    # Tabs: Define Strategy and Saved Strategies
    tab1, tab2 = st.tabs([
        t("builder.tabs.define"),
        t("builder.tabs.saved"),
    ])
    
    # === DEFINE STRATEGY TAB (merged NL + JSON) ===
    with tab1:
        st.header(t("builder.define.header"))
        
        st.write(t("builder.define.description"))
        
        # Show LLM status
        if llm_config:
            provider_name = {"openai": "OpenAI", "anthropic": "Anthropic"}.get(
                llm_config['provider'], llm_config['provider']
            )
            st.info(
                f"🤖 {t('builder.define.llm_active')}: {provider_name} ({llm_config['model']})"
            )
        else:
            st.warning(t("builder.define.llm_inactive"))
        
        # Natural language input
        nl_text = st.text_area(
            t("builder.define.nl_input_label"),
            value=t("builder.define.sample"),
            height=150,
            key="nl_input"
        )
        
        # Symbol override
        col1, col2 = st.columns(2)
        with col1:
            override_symbols = st.text_input(
                t("builder.define.override_label"),
                placeholder=t("builder.define.override_placeholder")
            )
        
        with col2:
            if st.button(t("builder.define.parse_button"), type="primary"):
                with st.spinner(t("builder.define.spinner")):
                    # Parse symbols if provided
                    symbols = None
                    if override_symbols:
                        symbols = [s.strip().upper() for s in override_symbols.split(",")]
                    
                    # Parse strategy using LLM (returns three formats)
                    human_readable, strategy_dict, backtrader_code = parser.parse_with_llm(nl_text)
                    
                    # Update session state
                    st.session_state.human_readable = human_readable
                    st.session_state.json_definition = strategy_dict
                    st.session_state.backtrader_code = backtrader_code
                    
                    st.success(t("builder.define.success"))
                    st.rerun()
        
        st.divider()
        
        # Three editable format sections
        st.subheader(t("builder.define.formats_header"))
        
        # Create three columns for the format tabs
        format_tab1, format_tab2, format_tab3 = st.tabs([
            t("builder.define.format_human"),
            t("builder.define.format_json"),
            t("builder.define.format_code")
        ])
        
        # Human Readable Format
        with format_tab1:
            st.write(t("builder.define.human_description"))
            human_readable_edited = st.text_area(
                t("builder.define.human_label"),
                value=st.session_state.human_readable,
                height=300,
                key="human_readable_editor"
            )
            if st.button(t("builder.define.update_human"), key="update_human"):
                st.session_state.human_readable = human_readable_edited
                st.success(t("builder.define.update_success"))
        
        # JSON Format
        with format_tab2:
            st.write(t("builder.define.json_description"))
            
            if st.session_state.json_definition:
                json_str = json.dumps(st.session_state.json_definition, indent=2)
            else:
                # Show example
                json_str = json.dumps({
                    "name": "SMA Cross Strategy",
                    "universe": ["AAPL"],
                    "timeframe": {
                        "start": "2019-01-01",
                        "end": "2024-12-31",
                        "interval": "1d"
                    },
                    "entry": [
                        {
                            "type": "indicator",
                            "ind": "SMA",
                            "period": 50,
                            "op": ">",
                            "rhs": {"ind": "SMA", "period": 200}
                        }
                    ],
                    "exit": [
                        {"type": "trailing_stop", "percent": 0.08},
                        {"type": "take_profit", "percent": 0.15}
                    ],
                    "position": {
                        "sizing": "percent_cash",
                        "value": 0.25,
                        "max_positions": 4
                    },
                    "costs": {
                        "commission_per_share": 0.005,
                        "slippage_bps": 5
                    }
                }, indent=2)
            
            json_edited = st.text_area(
                t("builder.define.json_label"),
                value=json_str,
                height=400,
                key="json_editor"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button(t("builder.define.validate_json"), key="validate_json"):
                    try:
                        strategy_dict = json.loads(json_edited)
                        # Validate with Pydantic model
                        strategy_model = Strategy(**strategy_dict)
                        st.session_state.json_definition = strategy_dict
                        st.success(t("builder.define.validate_success"))
                    except Exception as e:
                        st.error(t("builder.define.validate_error", error=str(e)))
            
            with col2:
                if st.button(t("builder.define.compile_json"), key="compile_json"):
                    try:
                        strategy_dict = json.loads(json_edited)
                        code = compiler.compile(strategy_dict)
                        st.session_state.json_definition = strategy_dict
                        st.session_state.backtrader_code = code
                        
                        # Validate code
                        is_valid, violations = validator.validate_backtrader_strategy(code)
                        if is_valid:
                            st.success(t("builder.define.compile_success"))
                        else:
                            st.warning(t("builder.define.compile_warning"))
                            for v in violations:
                                st.write(f"- {v}")
                        st.rerun()
                    except Exception as e:
                        st.error(t("builder.define.compile_error", error=str(e)))
        
        # Backtrader Code Format
        with format_tab3:
            st.write(t("builder.define.code_description"))
            code_edited = st.text_area(
                t("builder.define.code_label"),
                value=st.session_state.backtrader_code,
                height=400,
                key="code_editor"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button(t("builder.define.validate_code"), key="validate_code"):
                    is_valid, violations = validator.validate_backtrader_strategy(code_edited)
                    if is_valid:
                        st.session_state.backtrader_code = code_edited
                        st.success(t("builder.define.code_valid"))
                    else:
                        st.warning(t("builder.define.code_warnings"))
                        for v in violations:
                            st.write(f"- {v}")
            
            with col2:
                if st.button(t("builder.define.update_code"), key="update_code"):
                    st.session_state.backtrader_code = code_edited
                    st.success(t("builder.define.update_success"))
        
        # Save all three formats
        st.divider()
        st.subheader(t("builder.define.save_header"))
        
        col1, col2 = st.columns([3, 1])
        with col1:
            strategy_name = st.text_input(
                t("builder.define.strategy_name"),
                value=st.session_state.json_definition.get('name', 'My Strategy') if st.session_state.json_definition else 'My Strategy',
                key="strategy_name_input"
            )
        
        with col2:
            if st.button(t("builder.define.save_button"), type="primary", key="save_strategy"):
                if not st.session_state.json_definition:
                    st.error(t("builder.define.save_error_no_data"))
                else:
                    # Save to database
                    strategy_id = f"strat_{uuid.uuid4().hex[:8]}"
                    
                    # Save strategy with all three formats
                    db.execute(
                        """INSERT INTO strategies (
                            id, name, version, json, 
                            human_readable, json_definition, backtrader_code,
                            created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                        (
                            strategy_id, 
                            strategy_name, 
                            1,
                            json.dumps(st.session_state.json_definition),  # Legacy compatibility
                            st.session_state.human_readable,
                            json.dumps(st.session_state.json_definition),
                            st.session_state.backtrader_code,
                            datetime.now().isoformat()
                        )
                    )
                    
                    st.success(t("builder.define.save_success", strategy_id=strategy_id))
                    st.session_state['saved_strategy_id'] = strategy_id
    
    # === SAVED STRATEGIES TAB ===
    with tab2:
        st.header(t("builder.saved.header"))
        
        # Load saved strategies
        strategies = db.fetchall(
            "SELECT id, name, version, created_at FROM strategies ORDER BY created_at DESC"
        )
        
        if strategies:
            for strat in strategies:
                with st.expander(f"📋 {strat['name']} (v{strat['version']})"):
                    st.write(t("builder.saved.id", value=strat['id']))
                    st.write(t("builder.saved.created", value=strat['created_at']))
                    
                    # Load full strategy data
                    full_strat = db.fetchone(
                        """SELECT human_readable, json_definition, backtrader_code, json 
                           FROM strategies WHERE id = ?""",
                        (strat['id'],)
                    )
                    
                    # Show three formats in tabs
                    saved_tab1, saved_tab2, saved_tab3 = st.tabs([
                        t("builder.saved.format_human"),
                        t("builder.saved.format_json"),
                        t("builder.saved.format_code")
                    ])
                    
                    with saved_tab1:
                        human_text = full_strat.get('human_readable', '')
                        if not human_text and full_strat.get('json'):
                            # Generate from JSON if missing
                            try:
                                strategy_dict = json.loads(full_strat['json'])
                                human_text = parser._generate_human_readable(strategy_dict)
                            except:
                                human_text = "Not available"
                        
                        edited_human = st.text_area(
                            t("builder.saved.human_label"),
                            value=human_text,
                            height=200,
                            key=f"saved_human_{strat['id']}"
                        )
                        
                        if st.button(t("builder.saved.update_button"), key=f"update_human_{strat['id']}"):
                            db.execute(
                                "UPDATE strategies SET human_readable = ? WHERE id = ?",
                                (edited_human, strat['id'])
                            )
                            st.success(t("builder.saved.update_success"))
                            st.rerun()
                    
                    with saved_tab2:
                        json_text = full_strat.get('json_definition') or full_strat.get('json', '{}')
                        try:
                            json_dict = json.loads(json_text) if isinstance(json_text, str) else json_text
                            json_formatted = json.dumps(json_dict, indent=2)
                        except:
                            json_formatted = json_text
                        
                        edited_json = st.text_area(
                            t("builder.saved.json_label"),
                            value=json_formatted,
                            height=300,
                            key=f"saved_json_{strat['id']}"
                        )
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(t("builder.saved.validate_button"), key=f"validate_json_{strat['id']}"):
                                try:
                                    strategy_dict = json.loads(edited_json)
                                    Strategy(**strategy_dict)
                                    st.success(t("builder.saved.validate_success"))
                                except Exception as e:
                                    st.error(t("builder.saved.validate_error", error=str(e)))
                        
                        with col2:
                            if st.button(t("builder.saved.update_button"), key=f"update_json_{strat['id']}"):
                                try:
                                    strategy_dict = json.loads(edited_json)
                                    db.execute(
                                        "UPDATE strategies SET json_definition = ?, json = ? WHERE id = ?",
                                        (edited_json, edited_json, strat['id'])
                                    )
                                    st.success(t("builder.saved.update_success"))
                                    st.rerun()
                                except Exception as e:
                                    st.error(t("builder.saved.update_error", error=str(e)))
                    
                    with saved_tab3:
                        code_text = full_strat.get('backtrader_code', '')
                        if not code_text and full_strat.get('json'):
                            # Generate from JSON if missing
                            try:
                                strategy_dict = json.loads(full_strat['json'])
                                code_text = compiler.compile(strategy_dict)
                            except:
                                code_text = "# Code generation failed"
                        
                        edited_code = st.text_area(
                            t("builder.saved.code_label"),
                            value=code_text,
                            height=300,
                            key=f"saved_code_{strat['id']}"
                        )
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(t("builder.saved.validate_button"), key=f"validate_code_{strat['id']}"):
                                is_valid, violations = validator.validate_backtrader_strategy(edited_code)
                                if is_valid:
                                    st.success(t("builder.saved.code_valid"))
                                else:
                                    st.warning(t("builder.saved.code_warnings"))
                                    for v in violations:
                                        st.write(f"- {v}")
                        
                        with col2:
                            if st.button(t("builder.saved.update_button"), key=f"update_code_{strat['id']}"):
                                db.execute(
                                    "UPDATE strategies SET backtrader_code = ? WHERE id = ?",
                                    (edited_code, strat['id'])
                                )
                                st.success(t("builder.saved.update_success"))
                                st.rerun()
                    
                    # Load and Delete buttons
                    st.divider()
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button(t("builder.saved.load_button"), key=f"load_{strat['id']}", type="primary"):
                            # Load into Define Strategy tab
                            try:
                                json_data = full_strat.get('json_definition') or full_strat.get('json')
                                st.session_state.json_definition = json.loads(json_data) if isinstance(json_data, str) else json_data
                                st.session_state.human_readable = full_strat.get('human_readable', '')
                                st.session_state.backtrader_code = full_strat.get('backtrader_code', '')
                                st.success(t("builder.saved.load_success"))
                                st.rerun()
                            except Exception as e:
                                st.error(t("builder.saved.load_error", error=str(e)))
                    
                    with col2:
                        if st.button(t("builder.saved.delete_button"), key=f"del_{strat['id']}", type="secondary"):
                            db.execute("DELETE FROM strategies WHERE id = ?", (strat['id'],))
                            db.execute("DELETE FROM codes WHERE strategy_id = ?", (strat['id'],))
                            st.success(t("builder.saved.delete_success"))
                            st.rerun()
        else:
            st.info(t("builder.saved.empty"))


if __name__ == "__main__":
    show()
