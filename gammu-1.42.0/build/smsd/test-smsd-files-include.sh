#!/usr/bin/sh

set -x
set -e
SMSD_PID=0

INBOXF="$1"
SMSD_CMD="$2"
SMSD_INJECT_CMD="$3"
SMSD_MONITOR_CMD="$4"

SERVICE="files-include-$INBOXF"

echo "NOTICE: This test is quite tricky about timing, if you run it on really slow platform, it might fail."
echo "NOTICE: Testing service $SERVICE"

cleanup() {
    if [ $SMSD_PID -ne 0 ] ; then
        kill $SMSD_PID
        sleep 1
    fi
}

trap cleanup INT QUIT EXIT

cd /home/vincent/Gofood/gammu-1.42.0/build/smsd

rm -rf smsd-test-$SERVICE
mkdir smsd-test-$SERVICE
cd smsd-test-$SERVICE

# Dummy backend storage
mkdir gammu-dummy
# Create config file
cat > .smsdrc <<EOT
[gammu]
model = dummy
connection = none
port = /home/vincent/Gofood/gammu-1.42.0/build/smsd/smsd-test-$SERVICE/gammu-dummy
gammuloc = /dev/null
loglevel = textall

[smsd]
commtimeout = 5
multiparttimeout = 5
ReceiveFrequency = 5
debuglevel = 255
logfile = stderr
runonreceive = /usr/bin/sh /home/vincent/Gofood/gammu-1.42.0/build/smsd/smsd-test-$SERVICE/received.sh
service = files
inboxpath = /home/vincent/Gofood/gammu-1.42.0/build/smsd/smsd-test-$SERVICE/inbox/
outboxpath = /home/vincent/Gofood/gammu-1.42.0/build/smsd/smsd-test-$SERVICE/outbox/
sentsmspath = /home/vincent/Gofood/gammu-1.42.0/build/smsd/smsd-test-$SERVICE/sent/
errorsmspath = /home/vincent/Gofood/gammu-1.42.0/build/smsd/smsd-test-$SERVICE/error/
inboxformat = $INBOXF
transmitformat = auto
includenumbersfile = /home/vincent/Gofood/gammu-1.42.0/build/smsd/smsd-test-$SERVICE/include.lst
EOT
cat > include.lst <<EOT
800123456
EOT
mkdir -p /home/vincent/Gofood/gammu-1.42.0/build/smsd/smsd-test-$SERVICE/inbox/
mkdir -p /home/vincent/Gofood/gammu-1.42.0/build/smsd/smsd-test-$SERVICE/outbox/
mkdir -p /home/vincent/Gofood/gammu-1.42.0/build/smsd/smsd-test-$SERVICE/sent/
mkdir -p /home/vincent/Gofood/gammu-1.42.0/build/smsd/smsd-test-$SERVICE/error/

cat > /home/vincent/Gofood/gammu-1.42.0/build/smsd/smsd-test-$SERVICE/received.sh << EOT
#!/usr/bin/sh
echo "\$@" >> /home/vincent/Gofood/gammu-1.42.0/build/smsd/smsd-test-$SERVICE/received.log
EOT
chmod +x /home/vincent/Gofood/gammu-1.42.0/build/smsd/smsd-test-$SERVICE/received.sh

CONFIG_PATH="/home/vincent/Gofood/gammu-1.42.0/build/smsd/smsd-test-$SERVICE/.smsdrc"
DUMMY_PATH="/home/vincent/Gofood/gammu-1.42.0/build/smsd/smsd-test-$SERVICE/gammu-dummy"

mkdir -p $sms $DUMMY_PATH/sms/1
mkdir -p $sms $DUMMY_PATH/sms/2
mkdir -p $sms $DUMMY_PATH/sms/3
mkdir -p $sms $DUMMY_PATH/sms/4
mkdir -p $sms $DUMMY_PATH/sms/5

$SMSD_CMD -c "$CONFIG_PATH" &
SMSD_PID=$!

sleep 5

for sms in 62 68 74 ; do
    cp /home/vincent/Gofood/gammu-1.42.0/smsd/../tests/at-sms-encode/$sms.backup $DUMMY_PATH/sms/1/$sms
done

# Inject messages
cp /home/vincent/Gofood/gammu-1.42.0/smsd/tests/OUT* /home/vincent/Gofood/gammu-1.42.0/build/smsd/smsd-test-$SERVICE/outbox/
$SMSD_INJECT_CMD -c "$CONFIG_PATH" TEXT 123465 -text "Lorem ipsum."

sleep 5

# Incoming messages
for sms in 10 16 26 ; do
    cp /home/vincent/Gofood/gammu-1.42.0/smsd/../tests/at-sms-encode/$sms.backup $DUMMY_PATH/sms/3/$sms
done

TIMEOUT=0
while ! $SMSD_MONITOR_CMD -C -c "$CONFIG_PATH" -n 1 -d 0 | grep -q ";999999999999999;994299429942994;4;3;0;100;42" ; do
    $SMSD_MONITOR_CMD -C -c "$CONFIG_PATH" -n 1 -d 0
    sleep 1
    TIMEOUT=$(($TIMEOUT + 1))
    if [ $TIMEOUT -gt 60 ] ; then
        echo "ERROR: Wrong timeout!"
        exit 1
    fi
done

sleep 5

$SMSD_MONITOR_CMD -C -c "$CONFIG_PATH" -n 1 -d 0

if [ `wc -l < /home/vincent/Gofood/gammu-1.42.0/build/smsd/smsd-test-$SERVICE/received.log` -ne 3 ] ; then
    echo "ERROR: Wrong number of messages received!"
    exit 1
fi

