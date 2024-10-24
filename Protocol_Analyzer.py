import sys
import serial
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (QApplication, QWidget, QTabWidget, QLabel, QVBoxLayout, 
                             QLineEdit, QPushButton, QComboBox, QTextEdit, QHBoxLayout, QSpacerItem, QSizePolicy)

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
        ax.step(x, y + i * 2, where='mid')  # Removed label argument
    
    # Y-axis labels as D0, D1, D2, ..., D6
    ax.set_yticks(np.arange(0, channels * 2, 2))
    ax.set_yticklabels([f'D{i}' for i in range(channels)])  # Keep the Y-axis labels

    # X-axis as Time
    ax.set_xlabel('Time')
    # ax.legend(loc='upper right')  # Removed legend since there are no labels

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
        
        # Add a QTextEdit for displaying received data
        self.data_display = QTextEdit()
        self.data_display.setReadOnly(True)  # Make it read-only
        main_layout.addWidget(self.data_display)
        
        # Dummy data for plotting
        self.data = np.random.randint(0, 128, 100)  # Random 7-bit data
        
        # Update Plot Button
        self.btn_update_plot = QPushButton("Update Plot")
        self.btn_update_plot.clicked.connect(self.update_plot)
        main_layout.addWidget(self.btn_update_plot)
        
        # Button to simulate reading serial data and displaying it
        self.btn_read_data = QPushButton("Read Serial Data")
        self.btn_read_data.clicked.connect(self.read_and_display_data)
        main_layout.addWidget(self.btn_read_data)

        self.setLayout(main_layout)

    def create_spi_tab(self):
        layout = QVBoxLayout()

        lbl_spi = QLabel("SPI Configuration")
        layout.addWidget(lbl_spi)
        
        form_layout = QVBoxLayout()

        # Clock Frequency
        lbl_clock = QLabel("Clock Frequency (Hz):")
        self.spi_clock_entry = QLineEdit()
        self.spi_clock_entry.setFixedWidth(100)
        
        form_layout.addWidget(lbl_clock)
        form_layout.addWidget(self.spi_clock_entry)
        
        # Clock Polarity
        lbl_polarity = QLabel("Clock Polarity (CPOL):")
        self.spi_polarity_combo = QComboBox()
        self.spi_polarity_combo.addItems(["0 (Idle Low)", "1 (Idle High)"])
        self.spi_polarity_combo.setFixedWidth(100)

        form_layout.addWidget(lbl_polarity)
        form_layout.addWidget(self.spi_polarity_combo)
        
        # Clock Phase
        lbl_phase = QLabel("Clock Phase (CPHA):")
        self.spi_phase_combo = QComboBox()
        self.spi_phase_combo.addItems(["0 (Leading Edge)", "1 (Trailing Edge)"])
        self.spi_phase_combo.setFixedWidth(100)

        form_layout.addWidget(lbl_phase)
        form_layout.addWidget(self.spi_phase_combo)
        
        # Chip Select
        lbl_chip_select = QLabel("Chip Select Pin:")
        self.spi_chip_select_entry = QLineEdit()
        self.spi_chip_select_entry.setFixedWidth(100)

        form_layout.addWidget(lbl_chip_select)
        form_layout.addWidget(self.spi_chip_select_entry)
        
        # Centering Layout
        centered_layout = QHBoxLayout()
        centered_layout.addStretch(1)  # Add spacer to the left
        centered_layout.addLayout(form_layout)  # Add form layout in the center
        centered_layout.addStretch(1)  # Add spacer to the right

        layout.addLayout(centered_layout)
        self.tab_spi.setLayout(layout)

    def create_uart_tab(self):
        layout = QVBoxLayout()
        
        lbl_uart = QLabel("UART Configuration")
        layout.addWidget(lbl_uart)
        
        form_layout = QVBoxLayout()

        # Baud Rate
        lbl_baud_rate = QLabel("Baud Rate:")
        self.uart_baud_rate_entry = QLineEdit()
        self.uart_baud_rate_entry.setFixedWidth(100)

        form_layout.addWidget(lbl_baud_rate)
        form_layout.addWidget(self.uart_baud_rate_entry)
        
        # Data Bits
        lbl_data_bits = QLabel("Data Bits:")
        self.uart_data_bits_combo = QComboBox()
        self.uart_data_bits_combo.addItems(["5", "6", "7", "8"])
        self.uart_data_bits_combo.setFixedWidth(100)

        form_layout.addWidget(lbl_data_bits)
        form_layout.addWidget(self.uart_data_bits_combo)
        
        # Stop Bits
        lbl_stop_bits = QLabel("Stop Bits:")
        self.uart_stop_bits_combo = QComboBox()
        self.uart_stop_bits_combo.addItems(["1", "1.5", "2"])
        self.uart_stop_bits_combo.setFixedWidth(100)

        form_layout.addWidget(lbl_stop_bits)
        form_layout.addWidget(self.uart_stop_bits_combo)
        
        # Parity
        lbl_parity = QLabel("Parity:")
        self.uart_parity_combo = QComboBox()
        self.uart_parity_combo.addItems(["None", "Even", "Odd"])
        self.uart_parity_combo.setFixedWidth(100)

        form_layout.addWidget(lbl_parity)
        form_layout.addWidget(self.uart_parity_combo)
        
        # Centering Layout
        centered_layout = QHBoxLayout()
        centered_layout.addStretch(1)  # Add spacer to the left
        centered_layout.addLayout(form_layout)  # Add form layout in the center
        centered_layout.addStretch(1)  # Add spacer to the right

        layout.addLayout(centered_layout)
        self.tab_uart.setLayout(layout)

    def create_i2c_tab(self):
        layout = QVBoxLayout()
        
        lbl_i2c = QLabel("I2C Configuration")
        layout.addWidget(lbl_i2c)

        form_layout = QVBoxLayout()

        # Address Bit
        lbl_address = QLabel("Address (7 or 10-bit):")
        self.i2c_address_entry = QLineEdit()
        self.i2c_address_entry.setFixedWidth(100)

        form_layout.addWidget(lbl_address)
        form_layout.addWidget(self.i2c_address_entry)
        
        # Read/Write Mode
        lbl_rw_mode = QLabel("Read/Write Mode:")
        self.i2c_rw_mode_combo = QComboBox()
        self.i2c_rw_mode_combo.addItems(["Read", "Write"])
        self.i2c_rw_mode_combo.setFixedWidth(100)

        form_layout.addWidget(lbl_rw_mode)
        form_layout.addWidget(self.i2c_rw_mode_combo)
        
        # Clock Speed
        lbl_clock_speed = QLabel("Clock Speed (kHz):")
        self.i2c_clock_speed_entry = QLineEdit()
        self.i2c_clock_speed_entry.setFixedWidth(100)

        form_layout.addWidget(lbl_clock_speed)
        form_layout.addWidget(self.i2c_clock_speed_entry)

        # Centering Layout
        centered_layout = QHBoxLayout()
        centered_layout.addStretch(1)  # Add spacer to the left
        centered_layout.addLayout(form_layout)  # Add form layout in the center
        centered_layout.addStretch(1)  # Add spacer to the right

        layout.addLayout(centered_layout)
        self.tab_i2c.setLayout(layout)

    def update_plot(self):
        plot_waveform(self.ax, self.data)
        self.canvas.draw()

    def read_and_display_data(self):
        # Simulate reading data from serial port
        port = "COM3"  # Example port
        baud_rate = 9600  # Example baud rate
        data = read_serial_data(port, baud_rate)
        
        if data:
            # Convert byte data to a readable format
            data_str = data.decode('utf-8', errors='replace')  # Decode data
            self.data_display.append(f"Received Data: {data_str}")  # Append received data to display

# Main Function
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProtocolAnalyzerGUI()
    window.show()
    sys.exit(app.exec_())
