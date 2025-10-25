"""
Code safety validator using AST inspection.
Ensures generated code has no filesystem/network access.
"""
import ast
from typing import List, Tuple


class CodeValidator:
    """Validate generated code for security and safety."""
    
    # Disallowed modules and functions
    FORBIDDEN_MODULES = {
        'os', 'sys', 'subprocess', 'socket', 'urllib', 'requests',
        'http', 'ftplib', 'smtplib', 'telnetlib', 'paramiko',
        'shutil', 'pathlib', 'glob', 'pickle', 'shelve',
        'sqlite3', 'psycopg2', 'pymongo', 'redis'
    }
    
    FORBIDDEN_BUILTINS = {
        'open', 'exec', 'eval', 'compile', '__import__',
        'input', 'raw_input', 'file'
    }
    
    def __init__(self):
        self.violations = []
    
    def validate(self, code: str) -> Tuple[bool, List[str]]:
        """Validate code for security issues.
        
        Args:
            code: Python code string to validate
            
        Returns:
            Tuple of (is_valid, list of violations)
        """
        self.violations = []
        
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            self.violations.append(f"Syntax error: {str(e)}")
            return False, self.violations
        
        # Check for forbidden imports
        self._check_imports(tree)
        
        # Check for forbidden function calls
        self._check_function_calls(tree)
        
        # Check for dangerous attribute access
        self._check_attribute_access(tree)
        
        is_valid = len(self.violations) == 0
        return is_valid, self.violations
    
    def _check_imports(self, tree: ast.AST):
        """Check for forbidden import statements.
        
        Args:
            tree: AST tree to check
        """
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in self.FORBIDDEN_MODULES:
                        self.violations.append(
                            f"Forbidden module import: {alias.name}"
                        )
            
            elif isinstance(node, ast.ImportFrom):
                if node.module in self.FORBIDDEN_MODULES:
                    self.violations.append(
                        f"Forbidden module import: {node.module}"
                    )
    
    def _check_function_calls(self, tree: ast.AST):
        """Check for forbidden function calls.
        
        Args:
            tree: AST tree to check
        """
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Check for direct builtin calls
                if isinstance(node.func, ast.Name):
                    if node.func.id in self.FORBIDDEN_BUILTINS:
                        self.violations.append(
                            f"Forbidden function call: {node.func.id}"
                        )
    
    def _check_attribute_access(self, tree: ast.AST):
        """Check for dangerous attribute access patterns.
        
        Args:
            tree: AST tree to check
        """
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute):
                # Check for __dict__, __class__, etc.
                if node.attr.startswith('__') and node.attr.endswith('__'):
                    self.violations.append(
                        f"Forbidden attribute access: {node.attr}"
                    )
    
    def validate_backtrader_strategy(self, code: str) -> Tuple[bool, List[str]]:
        """Validate that code defines a proper Backtrader strategy.
        
        Args:
            code: Python code string
            
        Returns:
            Tuple of (is_valid, list of violations)
        """
        # First run standard validation
        is_valid, violations = self.validate(code)
        
        if not is_valid:
            return False, violations
        
        # Check for Backtrader-specific requirements
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return False, [f"Syntax error: {str(e)}"]
        
        # Check that there's a class definition
        has_class = False
        has_next_method = False
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                has_class = True
                
                # Check for next() method
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == 'next':
                        has_next_method = True
        
        if not has_class:
            violations.append("Code must define a strategy class")
        
        if not has_next_method:
            violations.append("Strategy class must have a next() method")
        
        is_valid = len(violations) == 0
        return is_valid, violations
