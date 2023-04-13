# pi-comic-scanner
Raspberry Pi comic book barcode scanner and lookup

# 1. What you'll need:
1. Raspberry Pi 3
2. Raspberry Pi Imager -- Raspberry Pi Imager is an app available on MacOS, Linux, and Windows (https://www.raspberrypi.com/software/) from Raspberry Pi that allows you to quickly install Raspberry Pi OS and other operating systems to a microSD card.
3. A 16+ GB microSD card
4. 5.1V / 2.5 A DC micro USB output connector (https://www.raspberrypi.com/products/micro-usb-power-supply/)
5. Barcode HAT from sb Components (https://shop.sb-components.co.uk/products/barcode-hat-for-raspberry-pi) or any DE2120 Scanner Module

# 1. Set Up Raspberry Pi

### 1. Open Raspberry Pi Imager ![](readme_images/open_rpi_imager.png)
### 2. "Choose OS" -> "Raspberry Pi OS (Other)" -> Raspberry Pi OS (64-bit) ![](readme_images/choose_os.png)

### 3. Choose Storage 
* In my case, I'm using an SD Card Reader plugged into a USB-C port on my laptop. Make sure you choose the correct volume and nothing is stored on the microSD card as the imager will completely wipe the microSD card before writing the OS image. 
![](readme_images/choose_storage.png)
### 4. Configure the Raspberry Pi before writing:
1. set the hostname:
   1. I give mine a unique hostname so I can tell my numerous Raspberry Pi projects apart. 
   ![](readme_images/sethostname.png)
2. Enable SSH (Optional):
   1. Enabling SSH allows you to connect to the Raspberry Pi without a monitor through the command line on another computer.
   ![](readme_images/enable_ssh.png)
3. Set a username and password for the Raspberry Pi:
   1. The default username and password on a Raspberry Pi is not secure so I configure my own here. 
   ![](readme_images/setusername_password.png)
4. Configure wireless LAN
   1. This allows the Raspberry Pi to boot with the preconfigured network name and password for headless operation.
   ![](readme_images/configure_lan.png)
### 5. Write the image to the microSD Card
1. Reminder: the imager will erase all existing data on the microSD card so make sure you've selected the correct write destination.
![](readme_images/write_os.png)
### 6. After completion you should see a success response.
1. Its now safe to eject the microSD card
![](readme_images/write_success.png)


# 2. Connect Barcode HAT to Raspberry Pi
![](readme_images/barcodeHATsetup.png)
1. The HAT connects directly to the 40 GPIO pins on the Raspberry Pi
   - Im using some M2.5 x 16mm standoffs to support the HAT

# 3. Start up the Raspberry Pi
1. Insert the SD card into the microSD card slot on the Raspberry Pi and plug it in.
   - You should hear the scanner module beep during the power on cycle.
2. After the Pi has had a moment or two to power up, we're going to head over to the command terminal on our local computer and finish setting up the Raspberry Pi.

# 4. Configuring Raspberry Pi to work with scanner
1. From your local command line, SSH into the Raspberry Pi
   - Your username and hostname might be different. In my case piscanner is both the hostname and username.
   - If this is the first time connecting the Pi via the command line you may be prompted to add the Pi to the list of known hosts. Type yes.
   >    ssh username@hostname.local

   ![](readme_images/ssh_first.png)

2. Update the Raspberry Pi package list
   > sudo apt update

   ![](readme_images/sudo_update.png)
  
3. Upgrade all the installed packages to their latest versions. 
   - "full-upgrade" is preferred over the simple "upgrade", as it also picks up any dependency changes that may have been made.
   - If prompted to continue, type Y
   - This will take a minute!
   > sudo apt full-upgrade

   ![](readme_images/full_upgrade.png)

4. Install DE2120 Barcode Scanner Python module 
   - https://de2120-py.readthedocs.io/en/latest/apiref.html#de2120-barcode-scanner
   > sudo pip install de2120-barcode-scanner

   ![](readme_images/pipinstall_de2120.png)
5. Update the DE2120 Barcode Scanner module to read from ttyS0 serial interface
   > sudo nano /usr/local/lib/python3.9/dist-packages/de2120_barcode_scanner.py
   1. On line 178 replace "/dev/ttyACM0, 115200" with "/dev/ttyS0, 9600" 
   ![](readme_images/de2120_source_original.png)
   ![](readme_images/update_de2120_ttyS0.png)
   2. Write and Exit

6. Restart the Raspberry Pi
   > sudo reboot

# 5. Configure the Scanner
1. Restore the factory default settings on my scanner if this is the first time setting it up. 
   - Reading the "Restore default settings" barcode will restore all barcode reader property settings to the factory state.  
   - You can find additional documentation on the DE2120 Scanner and its functionality here:
     - https://cdn.sparkfun.com/assets/b/5/0/e/e/DY_Scan_Setting_Manual-DE2120___19.4.6___.pdf
   <br>
   
   ![](readme_images/restore_defaults_barcode.png)
   
2. We're going to use the Barcode HAT with the TTL/RS232 serial communication interface.
![](readme_images/ttl_rs232.png)
3. And set the baud rate to (9600)  
![](readme_images/baudrate.png)

4. Update the Raspberry Pi config settings
   1. Open the Raspberry Pi configuration UI
       > sudo raspi-config
   2. Select "Interface Options"
   ![](readme_images/interface_options.png)
   3. Select "Serial Port"
   ![](readme_images/serial1.png)
   4. "Would you like a login shell to be accessible over serial?" NO
   ![](readme_images/serial2.png)
   5. "Would you like the serial port hardware to be enabled?" YES
   ![](readme_images/serial3.png)
   6. Confirm OK
   ![](readme_images/serial4.png)
   7. Select Finish 
   ![](readme_images/raspiconfigfinish.png)
   8. Reboot YES
   ![](readme_images/raspiconfigreboot.png)

# 6. Test scanner with a sample program
1.  Download the example [qde2120_ex1_serial_scan.py](https://github.com/zanemmiller2/pi-comic-scanner/blob/59ec5604171b4c444cbe6549371fa168d4c4c61d/examples/qde2120_ex1_serial_scan.py) program. 
2. Run the example program from the command line:
   > python qde2120_ex1_serial_scan.py

   ![](/Users/zanemiller/pi-comic-scanner/readme_images/run_example.png)
3. Test it out by scanning some barcodes
![](/Users/zanemiller/pi-comic-scanner/readme_images/scan_barcode_example.png)






   
      
      
   

