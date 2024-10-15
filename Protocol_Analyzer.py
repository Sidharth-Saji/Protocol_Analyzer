import sys
import serial
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (QApplication, QWidget, QTabWidget, QLabel, QVBoxLayout, 
                             QHBoxLayout, QLineEdit, QPushButton, QComboBox)

# Function to read serial data
def read_serial_data(port, baud_rate):
    try:
        ser = serial.Serial(port, baud_rate)
        data = ser.read(100)  
        ser.close()
        return data
    except Exception as e:
        print(f"Error reading from {port}: {e}")
        return None

# Plotting digital waveform for 7 channels
def plot_waveform(ax, data):
    ax.clear()
    channels = 7  # (D0 to D6)
    x = np.linspace(0, len(data), len(data))  # Time axis

    for i in range(channels):
        y = (data >> i) & 1  # Simulate 7 channels from the data
        ax.step(x, y + i * 2, where='mid', label=f'D{i}')  # Label each channel as D0, D1, etc.
    
    # Y-axis labels as D0, D1, D2, ..., D6
    ax.set_yticks(np.arange(0, channels * 2, 2))
    ax.set_yticklabels([f'D{i}' for i in range(channels)])

    # X-axis as Time
    ax.set_xlabel('Time')
    ax.legend(loc='upper right')

# Main Protocol Analyzer GUI Class
class ProtocolAnalyzerGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ScopeX Protocol Analyzer")
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Create SPI, UART, I2C tabs
        self.tab_spi = QWidget()
        self.tab_uart = QWidget()
        self.tab_i2c = QWidget()
        
        # Add tabs to tab widget
        self.tab_widget.addTab(self.tab_spi, "SPI")
        self.tab_widget.addTab(self.tab_uart, "UART")
        self.tab_widget.addTab(self.tab_i2c, "I2C")
        
        # Layout for each tab
        self.create_spi_tab()
        self.create_uart_tab()
        self.create_i2c_tab()
        
        # Create layout for the main window
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.tab_widget)
        
        # Matplotlib Figure and Canvas for waveform plot
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        main_layout.addWidget(self.canvas)
        
        # Dummy data for plotting
        self.data = np.random.randint(0, 128, 100)  # Random 7-bit data
        
        # Update Plot Button
        self.btn_update_plot = QPushButton("Update Plot")
        self.btn_update_plot.clicked.connect(self.update_plot)
        main_layout.addWidget(self.btn_update_plot)
        
        self.setLayout(main_layout)

    def create_spi_tab(self):
        layout = QVBoxLayout()
        
        lbl_spi = QLabel("SPI Configuration")
        layout.addWidget(lbl_spi)
        
        lbl_clock = QLabel("Clock Frequency:")
        layout.addWidget(lbl_clock)
        
        self.spi_clock_entry = QLineEdit()
        layout.addWidget(self.spi_clock_entry)
        
        self.tab_spi.setLayout(layout)

    def create_uart_tab(self):
        layout = QVBoxLayout()
        
        lbl_uart = QLabel("UART Configuration")
        layout.addWidget(lbl_uart)
        
        lbl_baud_rate = QLabel("Baud Rate:")
        layout.addWidget(lbl_baud_rate)
        
        self.uart_baud_rate_entry = QLineEdit()
        layout.addWidget(self.uart_baud_rate_entry)
        
        self.tab_uart.setLayout(layout)

    def create_i2c_tab(self):
        layout = QVBoxLayout()
        
        lbl_i2c = QLabel("I2C Configuration")
        layout.addWidget(lbl_i2c)
        
        lbl_address = QLabel("Address Bit:")
        layout.addWidget(lbl_address)
        
        self.i2c_address_entry = QLineEdit()
        layout.addWidget(self.i2c_address_entry)
        
        self.tab_i2c.setLayout(layout)

    def update_plot(self):
        plot_waveform(self.ax, self.data)
        self.canvas.draw()

# Main Function
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProtocolAnalyzerGUI()
    window.show()
    sys.exit(app.exec_())
