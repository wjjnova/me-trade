"""
Strategy Builder page for creating and editing strategies.
"""
import streamlit as st
import json
from datetime import datetime
from src.strategy import NLParser, StrategyCompiler, CodeValidator
from src.models import Strategy
from src.db import get_db
import uuid


def show():
    """Display the strategy builder page."""
    st.title("Strategy Builder")
    st.write("Create trading strategies using natural language or structured definitions")
    
    # Initialize components
    parser = NLParser()
    compiler = StrategyCompiler()
    validator = CodeValidator()
    db = get_db()
    
    # Initialize session state
    if 'current_strategy' not in st.session_state:
        st.session_state.current_strategy = None
    if 'generated_code' not in st.session_state:
        st.session_state.generated_code = None
    
    # Tabs for different workflows
    tab1, tab2, tab3 = st.tabs(["📝 Natural Language", "⚙️ Structured JSON", "💾 Saved Strategies"])
    
    # === NATURAL LANGUAGE TAB ===
    with tab1:
        st.header("Natural Language Strategy")
        
        st.write("Describe your trading strategy in plain English or Chinese")
        
        nl_text = st.text_area(
            "Strategy Description",
            value="""Buy AAPL when the 50-day SMA crosses above the 200-day SMA and RSI is below 70. 
Sell with an 8% trailing stop or 15% profit target. 
Test from 2019-01-01 to 2024-12-31.""",
            height=150
        )
        
        # Symbol override
        col1, col2 = st.columns(2)
        with col1:
            override_symbols = st.text_input(
                "Override Symbols (optional)",
                placeholder="AAPL, MSFT, GOOGL"
            )
        
        if st.button("Parse Strategy", type="primary"):
            with st.spinner("Parsing natural language..."):
                # Parse symbols if provided
                symbols = None
                if override_symbols:
                    symbols = [s.strip().upper() for s in override_symbols.split(",")]
                
                # Parse strategy
                strategy_dict = parser.parse(nl_text, symbols)
                st.session_state.current_strategy = strategy_dict
                
                st.success("✓ Strategy parsed successfully!")
                st.json(strategy_dict)
    
    # === STRUCTURED JSON TAB ===
    with tab2:
        st.header("Structured Strategy Definition")
        
        # If we have a parsed strategy, show it
        if st.session_state.current_strategy:
            strategy_json = json.dumps(st.session_state.current_strategy, indent=2)
        else:
            # Show example
            strategy_json = json.dumps({
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
        
        # Editable JSON
        edited_json = st.text_area(
            "Strategy JSON",
            value=strategy_json,
            height=400
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Validate Strategy"):
                try:
                    strategy_dict = json.loads(edited_json)
                    # Try to create Pydantic model
                    strategy_model = Strategy(**strategy_dict)
                    st.success("✓ Strategy is valid!")
                    st.session_state.current_strategy = strategy_dict
                except Exception as e:
                    st.error(f"Validation error: {str(e)}")
        
        with col2:
            if st.button("Compile to Code", disabled=st.session_state.current_strategy is None):
                if st.session_state.current_strategy:
                    with st.spinner("Compiling strategy..."):
                        code = compiler.compile(st.session_state.current_strategy)
                        st.session_state.generated_code = code
                        
                        # Validate code
                        is_valid, violations = validator.validate_backtrader_strategy(code)
                        
                        if is_valid:
                            st.success("✓ Code compiled and validated!")
                        else:
                            st.warning("Code compiled but has validation warnings:")
                            for v in violations:
                                st.write(f"- {v}")
        
        # Show generated code
        if st.session_state.generated_code:
            st.divider()
            st.subheader("Generated Backtrader Code")
            
            st.code(st.session_state.generated_code, language="python")
            
            col1, col2 = st.columns(2)
            
            with col1:
                strategy_name = st.text_input(
                    "Strategy Name",
                    value=st.session_state.current_strategy.get('name', 'My Strategy')
                )
            
            with col2:
                if st.button("Save Strategy", type="primary"):
                    # Save to database
                    strategy_id = f"strat_{uuid.uuid4().hex[:8]}"
                    code_id = f"code_{uuid.uuid4().hex[:8]}"
                    
                    # Save strategy
                    db.execute(
                        """INSERT INTO strategies (id, name, version, json, created_at)
                           VALUES (?, ?, ?, ?, ?)""",
                        (strategy_id, strategy_name, 1, 
                         json.dumps(st.session_state.current_strategy),
                         datetime.now().isoformat())
                    )
                    
                    # Save code
                    db.execute(
                        """INSERT INTO codes (id, strategy_id, language, code, created_at)
                           VALUES (?, ?, ?, ?, ?)""",
                        (code_id, strategy_id, 'python', 
                         st.session_state.generated_code,
                         datetime.now().isoformat())
                    )
                    
                    st.success(f"✓ Strategy saved! ID: {strategy_id}")
                    st.session_state['saved_strategy_id'] = strategy_id
                    st.session_state['saved_code_id'] = code_id
    
    # === SAVED STRATEGIES TAB ===
    with tab3:
        st.header("Saved Strategies")
        
        # Load saved strategies
        strategies = db.fetchall("SELECT id, name, version, created_at FROM strategies ORDER BY created_at DESC")
        
        if strategies:
            for strat in strategies:
                with st.expander(f"{strat['name']} (v{strat['version']})"):
                    st.write(f"**ID:** {strat['id']}")
                    st.write(f"**Created:** {strat['created_at']}")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("Load", key=f"load_{strat['id']}"):
                            # Load strategy JSON
                            full_strat = db.fetchone(
                                "SELECT json FROM strategies WHERE id = ?",
                                (strat['id'],)
                            )
                            st.session_state.current_strategy = json.loads(full_strat['json'])
                            st.success("Strategy loaded!")
                            st.rerun()
                    
                    with col2:
                        if st.button("View Code", key=f"code_{strat['id']}"):
                            code_rec = db.fetchone(
                                "SELECT code FROM codes WHERE strategy_id = ?",
                                (strat['id'],)
                            )
                            if code_rec:
                                st.code(code_rec['code'], language="python")
                    
                    with col3:
                        if st.button("Delete", key=f"del_{strat['id']}", type="secondary"):
                            db.execute("DELETE FROM strategies WHERE id = ?", (strat['id'],))
                            db.execute("DELETE FROM codes WHERE strategy_id = ?", (strat['id'],))
                            st.success("Strategy deleted!")
                            st.rerun()
        else:
            st.info("No saved strategies yet. Create one using the tabs above!")


if __name__ == "__main__":
    show()
