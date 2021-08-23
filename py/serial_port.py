from posix import listdir
import sys
import glob
import serial

serialPort = None

def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    print("ports", ports)

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException) as err:
            print(f"error {port} {err}")
            pass
    return result

def move(label):
    if label == "flat":
        command = "g\n" # go
    elif label == "up":
        command = "l\n" # left
    elif label == "down":
        command = "r\n" # right
    elif label == "silence":
        command = "s\n" # stop
    elif label == "click":
        command = "b\n" # back
    else:
        command = None

    if command:
        # print(f"command={command}")
        serialPort.write(command.encode())
    else:
        print(f"unknown label {label}")
def connect(device):
    global serialPort
    print(f"connecting to {device}")
    serialPort = serial.Serial(port = device, baudrate=115200, bytesize = 8, timeout = 2, stopbits=serial.STOPBITS_ONE)
    print(f"connected to {serialPort}")
    count = 0
    
def read():
    bytes = serialPort.in_waiting
    if bytes > 0:
        line = serialPort.read(bytes)
        return line.decode()
    else:
        return None

if __name__ == '__main__':
    ports = serial_ports()
    if len(ports) ==0:
        print("No serial ports, exiting")
        exit(0)
    print(ports)
    device = "/dev/ttyUSB0"
    if device in ports:
        print(f"found {device}")
        connect(device)
    else:
        print(f"not found {device}")