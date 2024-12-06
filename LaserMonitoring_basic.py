import tango
import numpy as np

from tango import DeviceProxy
from matplotlib import pyplot as plt

import time

#import serial

###############################################
#               PARAMETERS                    #
###############################################

tango_host = tango.ApiUtil.get_env_var("TANGO_HOST")
print(tango_host)
print(tango.__version__)

polling_period = 1  # In seconds
polling_time =   # In seconds
nb_loops = int(polling_time / polling_period)

size_of_file = nb_loops * 0.05
print('your file is going to take roughly ' + str(size_of_file) + 'Mb')
print("Do you want to continue ? yes/no : ")
txt = input()

if (txt == 'yes' or txt == 'y' or txt == 'oui'):
    print("ok")
    ###############################################
    #               OPEN PROXIES                  #
    ###############################################

    print("Creating proxy to Tango devices...")
    tango_spectrometer1 = DeviceProxy("SY-SPECTRO_1/Spectrometer/FE1")
    tango_spectrometer2 = DeviceProxy("SY-SPECTRO_1/Spectrometer/FE2")

    tango_imager = DeviceProxy("FE_camera_1/BaslerCCD/1")
    tango_energymeter = DeviceProxy("FE_EM_1/energymeter/1")
    tango_camera = DeviceProxy("FE_CAMERA_1/ImgBeamAnalyzer/1")
    tango_temperature1 = DeviceProxy("thermo_1/thermometer/1")
    tango_temperature2 = DeviceProxy("thermo_2/thermometer/1")
    print("Done")

    ###############################################
    #               INITALISE FILES               #
    ###############################################
    print("starting acquisition loop")
    current_timestamp = time.time()
    print(current_timestamp)

    wavelength_1 = tango_spectrometer1.read_attribute("lambda").value
    wavelength_1 = np.insert(wavelength_1, 0, current_timestamp)

    wavelength_1_save = np.transpose(wavelength_1[:, None])
    np.savetxt('spectrum1.csv', wavelength_1_save, delimiter=',')

    wavelength_2 = tango_spectrometer2.read_attribute("lambda").value
    wavelength_2 = np.insert(wavelength_2, 0, current_timestamp)

    wavelength_2_save = np.transpose(wavelength_2[:, None])
    np.savetxt('spectrum2.csv', wavelength_2_save, delimiter=',')

    ###############################################
    #         POLL DATA AND APPEND TO FILE        #
    ###############################################

    for loop in range(0, nb_loops):
        print("looping")
        old_timestamp = current_timestamp
        current_timestamp = time.time()
        print(current_timestamp)
        spectrum_1 = np.asarray(tango_spectrometer1.read_attribute("intensity").value)
        spectrum_1 = np.insert(spectrum_1, 0, current_timestamp)
        spectrum_1_save = np.transpose(spectrum_1[:, None])

        spectrum_2 = np.asarray(tango_spectrometer2.read_attribute("intensity").value)
        spectrum_2 = np.insert(spectrum_2, 0, current_timestamp)
        spectrum_2_save = np.transpose(spectrum_2[:, None])

        energy = tango_energymeter.read_attribute("energy_1").value
        camera_centroidX = tango_camera.read_attribute("CentroidX").value
        camera_centroidY = tango_camera.read_attribute("CentroidY").value

        temperature1 = tango_temperature1.read_attribute("Temperature").value
        temperature2 = tango_temperature2.read_attribute("Temperature").value

        L = [current_timestamp, current_timestamp-old_timestamp, temperature1, temperature2, energy,
             camera_centroidX, camera_centroidY]

        with open('spectrum1.csv', 'ab') as f:
            np.savetxt(f, spectrum_1_save, delimiter=',')
        f.close()
        with open('spectrum2.csv', 'ab') as f:
            np.savetxt(f, spectrum_2_save, delimiter=',')
        f.close()
        with open("test.txt", 'a') as f:
            f.write(', '.join(map(str, L)) + '\n')
        f.close()

        time.sleep(polling_period)
        print(str(nb_loops - loop) + " loops to go !")


else:
    print("Operation cancelled by user")
