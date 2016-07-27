#!/bin/bash

BASEDIR="$(cd "$(dirname "$0")" && pwd)"

# PYTHON
PYTHON_BIN=$(which python)
# PIP
PIP_URL=https://bootstrap.pypa.io/get-pip.py

# App prefixes
UNSIGNED_PREFIX=unsigned
SIGNED_PREFIX=signed
ZIPPED_PREFIX=zipped

# Workspace
SETUP_FILE=setup.properties
DW_PATH=~/Downloads
WORKSPACE_PATH=$DW_PATH/workspace
META_INFO_FILE=meta.info
AUTHOR=$(whoami)

# Signing
KEY_STORE=$WORKSPACE_PATH/MyAndroid.keystore
KEY_PASS=keyp@ss
STORE_PASS=p@ssw@rd
KEY_ALIAS=MyAndroidKey

# SDK
SDK_URL=https://dl.google.com/android/android-sdk_r24.4.1-macosx.zip

# Check if ANDROID_HOME env is set
if [ -z $ANDROID_HOME ]; then
    ANDROID_HOME=~/Library/Android/sdk
fi

# Android emulator
EMULATORS=0
EMU_NAME=MyEmulator
EMU_SDCARD=1024M
EMU_ABI=default/x86_64
EMU_ABI_PACKAGE=sys-img-x86_64-android
EMU_PROC_NAME=emulator64-x86
ACTIVITY_NAME=MainActivity

echo 'Running setup'

# Check if PIP is installed
if ! which pip > /dev/null; then
    echo '--> Install PIP and python packages needed'
    # Download get-pip.py
    curl -o $DW_PATH/get-pip.py $PIP_URL &> /dev/null
    # Install pip
    python $DW_PATH/get-pip.py &> /dev/null
    # Update pip
    pip install --upgrade pip &> /dev/null
fi

# Install python dependencies
# argparse
if ! pip show argparse > /dev/null; then
    pip install --upgrade argparse &> /dev/null
    echo '        PIP: Install python argparse'
fi

# Check if workspace is set
if [ ! -d $WORKSPACE_PATH ]; then
    echo '--> Creating workspace'
    mkdir -p $WORKSPACE_PATH
fi

echo '--> Searching for Java'
# Find java version, javac and JAVA_HOME
if which java > /dev/null; then
    JAVA_HOME=$(/usr/libexec/java_home)
    JAVA_VER=$(java -version 2>&1 | sed 's/java version "\(.*\)\.\(.*\)\..*"/\1\2/; 1q')
    JAVAC_BIN=$(find $JAVA_HOME -type f  -name 'javac' | head -1)
    KEYTOOL_BIN=$(find $JAVA_HOME -type f  -name 'keytool' | head -1)
    JARSIGNER_BIN=$(find $JAVA_HOME -type f -name 'jarsigner' | head -1)
fi

# Hack: force to use java 1.7
if [ ! $JAVA_VER -eq 17 ];then
    # Default path
    JAVA_HOME_17=$(find /Library/Java -name 'Home' | grep 1.7)
    if [ -n $JAVA_HOME_17 ];then
        JAVAC_BIN_17=$(find $JAVA_HOME_17 -type f -name 'javac' | head -1)
        KEYTOOL_BIN_17=$(find $JAVA_HOME_17 -type f  -name 'keytool' | head -1)
        JARSIGNER_BIN_17=$(find $JAVA_HOME_17 -type f -name 'jarsigner' | head -1)
    fi
    # Setting java 1.7
    if  [ -n $JAVA_HOME_17 ] &&
        [ -n $JAVAC_BIN_17 ] &&
        [ -n $KEYTOOL_BIN_17 ] &&
        [ -n $JARSIGNER_BIN_17 ];then
        JAVA_VER=17
        JAVA_HOME=$JAVA_HOME_17
        JAVAC_BIN=$JAVAC_BIN_17
        KEYTOOL_BIN=$KEYTOOL_BIN_17
        JARSIGNER_BIN=$JARSIGNER_BIN_17
    fi
fi

# Create Keystore
if  [ -n $KEYTOOL_BIN ] &&
    [ ! -f $KEY_STORE ]; then
    echo '--> Create Keystore'
    $KEYTOOL_BIN -genkeypair -validity 10000 \
                -dname "CN=my company, C=SE" -keystore $KEY_STORE \
                -storepass $STORE_PASS -keypass $KEY_PASS \
                -alias $KEY_ALIAS -keyalg RSA
fi

# Downloading and extracting the SDK
if [ ! -d $ANDROID_HOME ]; then
    echo '--> Setting up Android SDK'
    # Download SDK
    if [ ! -f $DW_PATH/sdk.zip ]; then
        echo '        Downloading Android SDK'
        curl -o $DW_PATH/sdk.zip $SDK_URL &> /dev/null
    fi
    # Extract SDK
    if [ -f $DW_PATH/sdk.zip ]; then
        echo '        Extracting Android SDK'
        mkdir -p $ANDROID_HOME
        unzip -qq -o $DW_PATH/sdk.zip -d $ANDROID_HOME
    fi
fi

# Find android binary
if [ -d $ANDROID_HOME ]; then
    ANDROID_BIN=$(find $ANDROID_HOME -type f  -name 'android' | head -1)
fi

# Installing Android platform tools
if [ -f $ANDROID_BIN ];then
    ADB_BIN=$(find $ANDROID_HOME -type f  -name 'adb' | head -1)
    if [ -z $ADB_BIN ]; then
        echo '        Installing Android platform tools'
        #  3 - Android SDK Platform-tools, revision 24.0.1
        echo 'y' | $ANDROID_BIN update sdk --force --no-ui --all --filter 3 &>/dev/null
        ADB_BIN=$(find $ANDROID_HOME -type f  -name 'adb' | head -1)
    fi
fi

# Installing Android build tools, SDK and system image for emulator
if [ -f $ANDROID_BIN ];then
    if [ $JAVA_VER -ge '18' ]; then
        # 29 - SDK Platform Android 7.0, API 24, revision 2
        #  4 - Android SDK Build-tools, revision 24.0.1
        API_VER=24
        SDK_PLATFORM=29
        SDK_BUILD_TOOLS=4
    else
        # 30 - SDK Platform Android 6.0, API 23, revision 3
        #  6 - Android SDK Build-tools, revision 23.0.3
        # 67 - Google APIs Intel x86 Atom System Image, Android API 23, revision 15
        API_VER=23
        SDK_PLATFORM=30
        SDK_BUILD_TOOLS=6
    fi
    # 156 - Intel x86 Emulator Accelerator (HAXM installer), revision 6.0.3
    EMU_ACCELERATOR=156
    # Check if already installed
    if ! $ANDROID_BIN list target | grep android-$API_VER &> /dev/null ;then
        echo '        Installing Android build tools, SDK and system image for emulator'
        echo 'y' | $ANDROID_BIN update sdk --force --no-ui --all --filter $SDK_PLATFORM &>/dev/null
        echo 'y' | $ANDROID_BIN update sdk --force --no-ui --all --filter $SDK_BUILD_TOOLS &>/dev/null
        echo 'y' | $ANDROID_BIN update sdk --force --no-ui --all --filter $EMU_ABI_PACKAGE-$API_VER &>/dev/null
        echo 'y' | $ANDROID_BIN update sdk --force --no-ui --all --filter $EMU_ACCELERATOR &>/dev/null
    fi
fi

# Find android platform & build tools binaries
if  [ -d $ANDROID_HOME ] &&
    [ $API_VER -gt 0 ]; then
    ANDROID_JAR=$(find $ANDROID_HOME -type f  -name 'android.jar' | grep $API_VER | head -1)
    AAPT_BIN=$(find $ANDROID_HOME -type f  -name 'aapt' | grep $API_VER | head -1)
    DX_BIN=$(find $ANDROID_HOME -type f  -name 'dx' | grep $API_VER | head -1)
    ZIPALIGN_BIN=$(find $ANDROID_HOME -type f  -name 'zipalign' | grep $API_VER | head -1)
    EMULATOR_BIN=$(find $ANDROID_HOME -type f  -name 'emulator' | head -1)
fi

# Check available emulators
if [ -n $ANDROID_BIN ]; then
    echo '--> Setting up the android emulator'
    EMULATORS=$($ANDROID_BIN list avd | grep "Name\: $EMU_NAME" | wc -l)
fi

# Create android emulator, if needed
if  [  -n $ANDROID_BIN ] &&
    [ $EMULATORS -eq 0 ] ;then
    # Clean-up
    $ANDROID_BIN delete avd --name $EMU_NAME
    echo '        Creating a new android emulator'
    echo 'no' | $ANDROID_BIN create avd --target android-$API_VER --name $EMU_NAME --sdcard $EMU_SDCARD --abi $EMU_ABI
    # Check available emulators, again
    EMULATORS=$($ANDROID_BIN list avd | grep 'Name\:' | wc -l)
fi

# Start emulator
if  [  -n $EMULATOR_BIN ] &&
    [ $EMULATORS -gt 0 ] ;then
    NUM_PROCS=$(ps | grep $EMU_PROC_NAME | wc -l)
    if [ $NUM_PROCS -eq 1 ];then
        echo '        Starting the android emulator'
        nohup $EMULATOR_BIN -wipe-data -avd $EMU_NAME &>/dev/null &
    fi
fi

# In case emulator didn't start, maybe emulator accelerator needs to be installed manually
if  [  -n $EMULATOR_BIN ]; then
    sleep 2s
    NUM_PROCS=$(ps | grep $EMU_PROC_NAME | wc -l)
    HAXM_FILE=$(find $ANDROID_HOME -name 'IntelHAXM*.dmg'| head -1)
    if  [ $NUM_PROCS -eq 1 ] &&
        [ -f $HAXM_FILE ];then
        echo '        ERROR: FAILED TO START EMULATOR!'
        echo '        ERROR: EMULATION REQUIRES HW ACCELERATION'
        echo '        ERROR: Please install manually following package' $HAXM_FILE
        echo '        ERROR: Once package installed, rerun ./setup.sh'
    fi
fi

# Writing to file all the settings
echo '--> Writing to file all the settings'
cat > $SETUP_FILE <<EOF
# Setup properties
workspace_path=$WORKSPACE_PATH
meta_info_file=$META_INFO_FILE
author=$AUTHOR
java_home=$JAVA_HOME
java_ver=$JAVA_VER
javac_bin=$JAVAC_BIN
keytool_bin=$KEYTOOL_BIN
jarsigner_bin=$JARSIGNER_BIN
key_store=$KEY_STORE
key_pass=$KEY_PASS
store_pass=$STORE_PASS
key_alias=$KEY_ALIAS
api_ver=$API_VER
android_home=$ANDROID_HOME
android_bin=$ANDROID_BIN
android_jar=$ANDROID_JAR
adb_bin=$ADB_BIN
aapt_bin=$AAPT_BIN
dx_bin=$DX_BIN
emulator_bin=$EMULATOR_BIN
zipalign_bin=$ZIPALIGN_BIN
unsigned_prefix=$UNSIGNED_PREFIX
signed_prefix=$SIGNED_PREFIX
zipped_prefix=$ZIPPED_PREFIX
emu_name=$EMU_NAME
emu_proc_name=$EMU_PROC_NAME
activity_name=$ACTIVITY_NAME
EOF

if [ -z $PYTHON_BIN ];then
    echo 'ERROR: PYTHON IS NOT FOUND! Please install Python 2.7 manually'
fi
if  [ -z $JAVA_HOME ] ||
    [ ! $JAVA_VER -eq 17 ];then
    echo 'ERROR: JAVA IS NOT FOUND! Please install JDK 1.7 manually and set JAVA_HOME'
fi
if [ -z $ANDROID_HOME ];then
    echo 'ERROR: UNABLE TO DOWNLOAD ANDROID SDK! Please download it manually and set ANDROID_HOME'
fi