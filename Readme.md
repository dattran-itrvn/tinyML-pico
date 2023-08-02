- Record to file Hex
To download the recorded data to a host computer over USB, use the minicom terminal application. Start it in a command line window on Linux as follows:
run cmd: 
+ minicom -b 115200 -o -D /dev/ttyUSB0 (with UART)
or
+ minicom -b 115200 -o -D /dev/ttyACM0 (with USB)
Then log the output to a file, ensure the file does not exist first as the data will be concatenated to the end of an existing file. Press CTRL+A then press L to start logging. Then press the third key switch on the Pico project. The data for the audio will be sent to the terminal. After the complete data has been received, press CTRL+A then then press L to close the log file. The data downloaded is an ASCII HEX dump of the captured audio. An example of the start and end of data can be seen below. Pass this file into the HexDumpToWav application to produce a binary WAV file.
+ Press CTRL+A then press Q to stop logging

- Convert Hexa File to Wave File 
run cmd: 
./HexDumpToWav [FILENAME]

The result will be a file named [FILENAME].WAV
