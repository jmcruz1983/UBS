## Uber Build System (UBS)

### WHAT IT IS:

This it a simple build system to create basic android project, compile, package, install and
launch it on an Android emulator.

### REQUIREMENTS:

UBS requires:
* Mac-OSx
* Python2.7
* Java 1.7
* Curl library to download SDK from Google and PIP

#### WHY?
This packages need to be installed manually as they need user consent and admin priviledges

### HOW TO USE IT:
1. FIRST,  clone the sources
2. SECOND, Run ./setup.sh to run all the initial setup:
	* Setup Workspace
	* Install necessary python dependencies using PIP
	* Search for valid java
	* Generate signing key
	* Search for valid SDK and install needed tools and emulator
	* Start the emulator in background
	* Save all settings to file
3. THIRD, Run “./ubs.py —-help” in command-line to learn about usage

### OBSERVATIONS:
* It strictly requires Java1.7 due to some incompatibility using Java 1.8 and newer ANDROID SDK
* Setup.sh needs to be run at least once at the beginning
* Setup.sh is smart enough to setup needed stuff only once
* Fetching SDK from Google might fail due to connectivity issues or missing curl executable
* UBS only re-compiles the new added or modified files
* Have a look to UBS.mp4 video to see some examples of usage 

### EXAMPLES OF USAGE:
``` bash
-> ./setup.sh 
Running setup
--> Searching for Java
--> Setting up the android emulator
--> Writing to file all the settings
Setup Done

-> ./ubs.py --help
usage: ubs.py [-h] [--create CREATE] [--compile COMPILE] [--package PACKAGE]
              [--launch LAUNCH]

optional arguments:
  -h, --help         show this help message and exit
  --create CREATE    Creates an Android project with given name
  --compile COMPILE  Compiles a specific Android project
  --package PACKAGE  Generates an Android application for the given project
  --launch LAUNCH    Launches an Android application on an active simulator

-> ./ubs.py --create Test
22:49:15 INFO    : create: Creating "Test" project
22:49:16 INFO    : create: Project "Test" is created in "/Users/<user>/Downloads/workspace/Test"

-> ./ubs.py --compile Test
22:50:15 WARNING : utils: JAVA_HOME is not defined! Using "/Library/Java/JavaVirtualMachines/jdk1.7.0_79.jdk/Contents/Home"
22:50:15 WARNING : utils: ANDROID_HOME is not defined! Using "/Users/<user>/Library/Android/sdk"
22:50:15 INFO    : compile: Generating R.java
22:50:15 INFO    : utils: Following files are (A)dded or (M)odified:
22:50:15 INFO    : utils: 	A	main.xml
22:50:15 INFO    : utils: 	A	strings.xml
22:50:15 INFO    : compile: Generated R.java
22:50:15 INFO    : compile: Compiling java source
22:50:15 INFO    : utils: Following files are (A)dded or (M)odified:
22:50:15 INFO    : utils: 	A	MainActivity.java
22:50:15 INFO    : utils: 	A	R.java
22:50:16 INFO    : compile: Compiled sources
22:50:16 INFO    : compile: Generating DEX executable
22:50:16 INFO    : utils: Following files are (A)dded or (M)odified:
22:50:16 INFO    : utils: 	A	MainActivity.class
22:50:16 INFO    : utils: 	A	R$attr.class
22:50:16 INFO    : utils: 	A	R$drawable.class
22:50:16 INFO    : utils: 	A	R$layout.class
22:50:16 INFO    : utils: 	A	R$string.class
22:50:16 INFO    : utils: 	A	R.class
22:50:16 INFO    : compile: Generated DEX executable

—> ./ubs.py --package Test
22:51:49 WARNING : utils: JAVA_HOME is not defined! Using "/Library/Java/JavaVirtualMachines/jdk1.7.0_79.jdk/Contents/Home"
22:51:49 WARNING : utils: ANDROID_HOME is not defined! Using "/Users/jmcruz/Library/Android/sdk"
22:51:49 INFO    : package: Creating application package
22:51:49 INFO    : utils: Following files are (A)dded or (M)odified:
22:51:49 INFO    : utils: 	A	classes.dex
22:51:49 INFO    : package: Created Test.unsigned.apk
22:51:49 INFO    : package: Signing application package
22:51:49 INFO    : utils: Following files are (A)dded or (M)odified:
22:51:49 INFO    : utils: 	A	Test.unsigned.apk
22:51:50 INFO    : package: Signed application "Test.signed.apk"
22:51:50 INFO    : package: zip aligning application package
22:51:50 INFO    : utils: Following files are (A)dded or (M)odified:
22:51:50 INFO    : utils: 	A	Test.signed.apk
22:51:50 INFO    : package: Zip aligned application "Test.zipped.apk"

—> ./ubs.py --launch Test
22:53:38 INFO    : launch: Installing application into the emulator
22:53:39 INFO    : launch: Installed application "Test.zipped.apk" to emulator
22:53:39 INFO    : launch: Launching the application in the emulator
22:53:39 INFO    : launch: Launched the application in the emulator
```
