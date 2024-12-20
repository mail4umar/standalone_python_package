import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                            QStackedWidget, QMessageBox, QFileDialog, QFormLayout)
from PyQt6.QtCore import Qt
import verticapy as vp
from verticapy.performance.vertica import QueryProfilerInterface, QueryProfiler
import logging
import os

class DatabaseConnector(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Use QFormLayout for more compact and aligned form fields
        self.layout = QFormLayout()
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(10)
        
        # Create form fields more compactly
        self.host_input = QLineEdit()
        self.port_input = QLineEdit()
        self.database_input = QLineEdit()
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        # Add fields to form layout
        self.layout.addRow("Host:", self.host_input)
        self.layout.addRow("Port:", self.port_input)
        self.layout.addRow("Database:", self.database_input)
        self.layout.addRow("Username:", self.username_input)
        self.layout.addRow("Password:", self.password_input)
        
        # Create a container for the button to control its width
        button_container = QWidget()
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 10, 0, 0)
        
        # Connect button
        self.connect_btn = QPushButton("Connect to Database")
        self.connect_btn.setFixedWidth(200)
        self.connect_btn.clicked.connect(self.try_connection)
        
        button_layout.addWidget(self.connect_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        button_container.setLayout(button_layout)
        self.layout.addRow(button_container)
        
        # Set maximum width for the form
        self.setMaximumWidth(400)
        self.setLayout(self.layout)
        
        # Set up logging
        if not os.path.exists('logs'):
            os.makedirs('logs')
        logging.basicConfig(filename='logs/app_log.log', 
                          level=logging.INFO,
                          format='%(asctime)s - %(levelname)s - %(message)s')
    
    def try_connection(self):
        try:
            conn_info = {
                'host': self.host_input.text(),
                'port': self.port_input.text(),
                'database': self.database_input.text(),
                'user': self.username_input.text(),
                'password': self.password_input.text()
            }
            logging.info(f'Attempting to connect to database {conn_info["database"]}')
            
            vp.new_connection(
                conn_info,
                auto=True,
                overwrite=True,
            )
            
            QMessageBox.information(self, "Success", "Connected to database successfully!")
            # Get the main window reference and call the switch method
            main_window = self.parent()
            if isinstance(main_window, MainWindow):
                main_window.stacked_widget.setCurrentIndex(1)
            
        except Exception as e:
            logging.error(f'Connection error: {str(e)}')
            QMessageBox.critical(self, "Error", f"Failed to connect: {str(e)}")

class QueryInputPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Use QFormLayout for consistency with DatabaseConnector
        self.layout = QFormLayout()
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(10)
        
        # Create input fields
        self.schema_input = QLineEdit()
        self.key_input = QLineEdit()
        
        # Add fields to form layout
        self.layout.addRow("Schema Name:", self.schema_input)
        self.layout.addRow("Key ID:", self.key_input)
        
        # Create a container for the button
        button_container = QWidget()
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 10, 0, 0)
        
        # Create button
        self.visualize_btn = QPushButton("Visualize Query Plan")
        self.visualize_btn.setFixedWidth(200)
        self.visualize_btn.clicked.connect(self.load_query_plan)
        
        button_layout.addWidget(self.visualize_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        button_container.setLayout(button_layout)
        self.layout.addRow(button_container)
        
        # Set maximum width for the form
        self.setMaximumWidth(400)
        self.setLayout(self.layout)
    
    def load_query_plan(self):
        try:
            schema = self.schema_input.text()
            key = self.key_input.text()
            
            logging.info(f'Loading query plan with schema={schema}, key={key}')
            
            qprof = QueryProfilerInterface(
                target_schema=schema,
                key_id=key,
                check_tables=False
            )
            
            # Get the main window reference and create/switch to visualization
            main_window = self.parent()
            if isinstance(main_window, MainWindow):
                main_window.switch_to_visualization(qprof)
            
        except Exception as e:
            logging.error(f'Error loading query plan: {str(e)}')
            QMessageBox.critical(self, "Error", f"Failed to load query plan: {str(e)}")

# QueryVisualizer class remains the same
def check_graphviz():
    """Check if GraphViz is installed and accessible"""
    import shutil
    return shutil.which('dot') is not None

class QueryVisualizer(QWidget):
    def __init__(self, qprof, parent=None):
        super().__init__(parent)
        self.qprof = qprof
        self.layout = QVBoxLayout()
        
        # Check for GraphViz before proceeding
        if not check_graphviz():
            error_label = QLabel(
                "GraphViz is not found on your system. Please install GraphViz and add it to your PATH.\n\n"
                "Installation instructions:\n"
                "Windows: Download from https://graphviz.org/download/\n"
                "macOS: Run 'brew install graphviz'\n"
                "Linux: Run 'sudo apt-get install graphviz'"
            )
            error_label.setWordWrap(True)
            error_label.setStyleSheet("color: red;")
            self.layout.addWidget(error_label)
        else:
            # Create visualization area
            self.viz_area = QLabel("Loading visualization...")
            self.viz_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.viz_area.setStyleSheet("border: 1px solid black; min-height: 400px;")
            self.layout.addWidget(self.viz_area)
            
            # Generate visualization
            self.display_query_plan()
        
        self.setLayout(self.layout)
    
    def display_query_plan(self):
        try:
            logging.info('Generating query plan visualization')
            # Get the query plan tree
            tree = self.qprof.get_qplan_tree()
            
            # Convert the visualization to an image that PyQt can display
            # This part depends on how verticapy generates the visualization
            # You might need to save it to a temporary file and load it
            
            # Example (pseudo-code):
            # image_path = tree.save_as_image()
            # pixmap = QPixmap(image_path)
            # self.viz_area.setPixmap(pixmap)
            
        except Exception as e:
            logging.error(f'Error displaying query plan: {str(e)}')
            QMessageBox.critical(self, "Error", f"Failed to display query plan: {str(e)}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Query Plan Visualizer")
        self.setMinimumSize(800, 600)  # Reduced window size
        
        # Create stacked widget to handle multiple pages
        self.stacked_widget = QStackedWidget()
        
        # Create pages
        self.db_connector = DatabaseConnector(self)
        self.query_input = QueryInputPage(self)
        
        # Add pages to stacked widget
        self.stacked_widget.addWidget(self.db_connector)
        self.stacked_widget.addWidget(self.query_input)
        
        self.setCentralWidget(self.stacked_widget)
        
        # Create menu bar for navigation
        self.create_menu_bar()
    
    def create_menu_bar(self):
        menubar = self.menuBar()
        navigation = menubar.addMenu("Navigation")
        
        connect_action = navigation.addAction("Database Connection")
        connect_action.triggered.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        
        query_action = navigation.addAction("Query Input")
        query_action.triggered.connect(lambda: self.stacked_widget.setCurrentIndex(1))
    
    def switch_to_visualization(self, qprof):
        query_visualizer = QueryVisualizer(qprof, self)
        self.stacked_widget.addWidget(query_visualizer)
        self.stacked_widget.setCurrentWidget(query_visualizer)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())