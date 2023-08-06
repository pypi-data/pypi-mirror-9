import os
import fcntl
import array


SG_SCSI_RESET = 0x2284
SG_SCSI_RESET_NOTHING = 0
SG_SCSI_RESET_DEVICE = 1
SG_SCSI_RESET_BUS = 2
SG_SCSI_RESET_HOST = 3
SG_SCSI_RESET_TARGET = 4


def reset(device_path, reset_type):
    _buffer = array.array('H', [reset_type])
    fd = os.open(device_path, os.O_RDWR | os.O_NONBLOCK)
    try:
        fcntl.ioctl(fd, SG_SCSI_RESET, _buffer, False)
    finally:
        os.close(fd)


def lun_reset(device_path):
    reset(device_path, SG_SCSI_RESET_DEVICE)


def host_reset(device_path):
    reset(device_path, SG_SCSI_RESET_HOST)


def bus_reset(device_path):
    reset(device_path, SG_SCSI_RESET_BUS)

def target_reset(device_path):
    reset(device_path, SG_SCSI_RESET_TARGET)

