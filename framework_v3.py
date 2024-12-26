import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLineEdit, QPushButton, QLabel, 
                           QMessageBox, QTabWidget, QStackedWidget)
from PyQt6.QtCore import Qt
from PyQt6.QtWebEngineWidgets import QWebEngineView
import verticapy as vp
from verticapy.performance.vertica import QueryProfiler

class ConnectionWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        form_widget = QWidget()
        form_layout = QVBoxLayout()
        
        input_style = """
            QLineEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: white;
                min-width: 250px;
            }
            QLineEdit:focus {
                border: 1px solid #4a90e2;
            }
        """
        
        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("Host")
        self.host_input.setStyleSheet(input_style)
        
        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("Port")
        self.port_input.setStyleSheet(input_style)
        
        self.database_input = QLineEdit()
        self.database_input.setPlaceholderText("Database")
        self.database_input.setStyleSheet(input_style)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setStyleSheet(input_style)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet(input_style)
        
        for widget in [self.host_input, self.port_input, self.database_input, 
                      self.username_input, self.password_input]:
            form_layout.addWidget(widget)
            form_layout.addSpacing(10)
            
        self.connect_button = QPushButton("Connect to Database")
        self.connect_button.setStyleSheet("""
            QPushButton {
                background-color: #4a90e2;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 4px;
                min-width: 250px;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
            QPushButton:pressed {
                background-color: #2a5f9e;
            }
        """)
        
        form_layout.addWidget(self.connect_button)
        form_widget.setLayout(form_layout)
        
        main_layout = QHBoxLayout()
        main_layout.addStretch()
        main_layout.addWidget(form_widget)
        main_layout.addStretch()
        
        layout.addStretch()
        layout.addLayout(main_layout)
        layout.addStretch()
        
        self.setLayout(layout)
        self.connect_button.clicked.connect(self.try_connection)
        
    def try_connection(self):
        try:
            conn_info = {
                'host': self.host_input.text(),
                'port': self.port_input.text(),
                'database': self.database_input.text(),
                'user': self.username_input.text(),
                'password': self.password_input.text()
            }
            
            vp.new_connection(
                conn_info,
                auto=True,
                overwrite=True,
            )
            QMessageBox.information(self, "Success", "Connected to database successfully!")
            self.main_window.show_table_viewer()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to connect: {str(e)}")

class TableViewerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Table name input section
        input_layout = QHBoxLayout()
        self.table_input = QLineEdit()
        self.table_input.setPlaceholderText("Enter table name (e.g., public.table_name)")
        self.table_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: white;
                min-width: 300px;
            }
        """)
        
        self.view_button = QPushButton("View Table")
        self.view_button.setStyleSheet("""
            QPushButton {
                background-color: #4a90e2;
                color: white;
                padding: 8px 15px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
        """)
        
        input_layout.addWidget(self.table_input)
        input_layout.addWidget(self.view_button)
        
        # Web view for table display
        self.web_view = QWebEngineView()
        self.web_view.setMinimumHeight(400)
        
        layout.addLayout(input_layout)
        layout.addWidget(self.web_view)
        
        self.setLayout(layout)
        
        # Connect signals
        self.view_button.clicked.connect(self.display_table)
        
    def display_table(self):
        try:
            table_name = self.table_input.text()
            if not table_name:
                raise ValueError("Please enter a table name")
                
            vdf = vp.vDataFrame(table_name)
            html_content = vdf._repr_html_()
            
            # Add some CSS to make the table look better
            styled_html = f"""
                <html>
                <head>
                    <style>
                        body {{ font-family: Arial, sans-serif; }}
                        table {{ 
                            border-collapse: collapse; 
                            width: 100%; 
                            margin: 20px 0;
                        }}
                        th, td {{ 
                            padding: 12px; 
                            text-align: left; 
                            border: 1px solid #ddd; 
                        }}
                        th {{ 
                            background-color: #4a90e2; 
                            color: white; 
                        }}
                        tr:nth-child(even) {{ 
                            background-color: #f9f9f9; 
                        }}
                        tr:hover {{ 
                            background-color: #f5f5f5; 
                        }}
                    </style>
                </head>
                <body>
                    {html_content}
                </body>
                </html>
            """
            
            self.web_view.setHtml(styled_html)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to display table: {str(e)}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Vertica Database Viewer")
        self.setMinimumSize(1000, 700)
        
        self.stacked_widget = QStackedWidget()
        self.connection_widget = ConnectionWidget(self)
        
        self.tab_widget = QTabWidget()
        self.table_viewer_widget = TableViewerWidget(self)
        self.query_plan_widget = QueryPlanWidget(self)
        
        self.tab_widget.addTab(self.table_viewer_widget, "Table View")
        self.tab_widget.addTab(self.query_plan_widget, "Query Plan")
        
        self.stacked_widget.addWidget(self.connection_widget)
        self.stacked_widget.addWidget(self.tab_widget)
        
        self.setCentralWidget(self.stacked_widget)
        
    def show_table_viewer(self):
        self.stacked_widget.setCurrentWidget(self.tab_widget)

class QueryPlanWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        input_layout = QHBoxLayout()
        self.schema_input = QLineEdit()
        self.schema_input.setPlaceholderText("Enter schema name")
        self.schema_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: white;
                min-width: 300px;
            }
        """)
        
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("Enter key")
        self.key_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: white;
                min-width: 300px;
            }
        """)
        
        self.view_button = QPushButton("View Query Plan")
        self.view_button.setStyleSheet("""
            QPushButton {
                background-color: #4a90e2;
                color: white;
                padding: 8px 15px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
        """)
        
        input_layout.addWidget(self.schema_input)
        input_layout.addWidget(self.key_input)
        input_layout.addWidget(self.view_button)
        
        self.web_view = QWebEngineView()
        self.web_view.setMinimumHeight(400)
        
        layout.addLayout(input_layout)
        layout.addWidget(self.web_view)
        
        self.setLayout(layout)
        self.view_button.clicked.connect(self.display_plan)
        
    def display_plan(self):
        try:
            schema = self.schema_input.text()
            key = self.key_input.text()
            
            if not schema or not key:
                raise ValueError("Please enter both schema and key")
                
            qprof = QueryProfiler(target_schema=schema, key_id=key, check_tables=False)
            res = qprof.get_qplan_tree()
            html_content = res._repr_html_()
            
            styled_html = f"""
                <html>
                <head>
                    <style>
                        body {{ font-family: Arial, sans-serif; padding: 20px; }}
                    </style>
                </head>
                <body>
                    {html_content}
                </body>
                </html>
            """
            
            self.web_view.setHtml(styled_html)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to display query plan: {str(e)}")

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()