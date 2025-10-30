#!/usr/bin/sh

set -x
set -e
SMSD_PID=0

SERVICE="$1"
SMSD_CMD="$2"
SMSD_INJECT_CMD="$3"
SMSD_MONITOR_CMD="$4"

TEST_MATCH=";999999999999999;994299429942994;4;10;0;100;42"
INCOMING_USSD=1

if [ "x1" = x1 ] ; then
    SMSD_EXTRA_PARAMS="-p /home/vincent/Gofood/gammu-1.42.0/build/smsd/smsd-test-$SERVICE/smsd.pid"
fi

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
EOT

# Add driver specific configuration
case $SERVICE in
    dbi-sqlite3)
        cat >> .smsdrc <<EOT
service = sql
driver = sqlite3
database = smsd.db
dbdir = /home/vincent/Gofood/gammu-1.42.0/build/smsd/smsd-test-$SERVICE/
EOT
        ;;
    dbi-pgsql)
        cat >> .smsdrc <<EOT
service = sql
driver = pgsql
pc = 127.0.0.1
database = smsd
user = smsd
password = smsd
EOT
        ;;
    pgsql)
        cat >> .smsdrc <<EOT
service = sql
driver = native_pgsql
pc = 127.0.0.1
database = smsd
user = smsd
password = smsd
EOT
        ;;
    dbi-mysql)
        cat >> .smsdrc <<EOT
service = sql
driver = mysql
pc = 127.0.0.1
database = smsd
user = smsd
password = smsd
EOT
        ;;
    mysql)
        cat >> .smsdrc <<EOT
service = sql
driver = native_mysql
pc = 127.0.0.1
database = smsd
user = smsd
password = smsd
EOT
        ;;
    odbc)
        cat >> .smsdrc <<EOT
service = sql
driver = odbc
pc = smsd
user = smsd
password = smsd
sql = mysql
EOT
        ;;
    null)
        TEST_MATCH=";999999999999999;994299429942994;0;9;0;100;42"
        INCOMING_USSD=0
        cat >> .smsdrc <<EOT
service = null
EOT
        ;;
    files*)
        INBOXF=`echo $SERVICE | sed 's/.*-//'`
        cat >> .smsdrc <<EOT
service = files
inboxpath = /home/vincent/Gofood/gammu-1.42.0/build/smsd/smsd-test-$SERVICE/inbox/
outboxpath = /home/vincent/Gofood/gammu-1.42.0/build/smsd/smsd-test-$SERVICE/outbox/
sentsmspath = /home/vincent/Gofood/gammu-1.42.0/build/smsd/smsd-test-$SERVICE/sent/
errorsmspath = /home/vincent/Gofood/gammu-1.42.0/build/smsd/smsd-test-$SERVICE/error/
inboxformat = $INBOXF
transmitformat = auto
EOT
        ;;
esac

# Create database structures
case $SERVICE in
    *sqlite3)
        "SQLITE_BIN-NOTFOUND" smsd.db < /home/vincent/Gofood/gammu-1.42.0/smsd/../docs/sql/sqlite.sql
        ;;
    *pgsql)
        echo "DROP TABLE IF EXISTS gammu, inbox, outbox, outbox_multipart, phones, sentitems;" | PGPASSWORD="smsd" "PSQL_BIN-NOTFOUND" -h "127.0.0.1" -U "smsd" "smsd"
        PGPASSWORD="smsd" "PSQL_BIN-NOTFOUND" -h "127.0.0.1" -U "smsd" "smsd" < "/home/vincent/Gofood/gammu-1.42.0/smsd/../docs/sql/pgsql.sql" 2>&1 | grep -v 'ERROR.*language "plpgsql" already exists'
        ;;
    *mysql|odbc)
        echo "DROP TABLE IF EXISTS gammu, inbox, outbox, outbox_multipart, phones, sentitems;" | "MYSQL_BIN-NOTFOUND" "-usmsd" "-h127.0.0.1" "-psmsd" "smsd"
        "MYSQL_BIN-NOTFOUND" "-h127.0.0.1" "-usmsd" "-psmsd" "smsd" < "/home/vincent/Gofood/gammu-1.42.0/smsd/../docs/sql/mysql.sql"
        ;;
    files*)
        mkdir -p "/home/vincent/Gofood/gammu-1.42.0/build/smsd/smsd-test-$SERVICE/inbox/"
        mkdir -p "/home/vincent/Gofood/gammu-1.42.0/build/smsd/smsd-test-$SERVICE/outbox/"
        mkdir -p "/home/vincent/Gofood/gammu-1.42.0/build/smsd/smsd-test-$SERVICE/sent/"
        mkdir -p "/home/vincent/Gofood/gammu-1.42.0/build/smsd/smsd-test-$SERVICE/error/"
        ;;
esac

cat > /home/vincent/Gofood/gammu-1.42.0/build/smsd/smsd-test-$SERVICE/received.sh << EOT
#!/usr/bin/sh
echo "\$@" >> /home/vincent/Gofood/gammu-1.42.0/build/smsd/smsd-test-$SERVICE/received.log
env >> /home/vincent/Gofood/gammu-1.42.0/build/smsd/smsd-test-$SERVICE/env.log
echo "Executed script!"
exit 4
EOT
chmod +x /home/vincent/Gofood/gammu-1.42.0/build/smsd/smsd-test-$SERVICE/received.sh

CONFIG_PATH="/home/vincent/Gofood/gammu-1.42.0/build/smsd/smsd-test-$SERVICE/.smsdrc"
DUMMY_PATH="/home/vincent/Gofood/gammu-1.42.0/build/smsd/smsd-test-$SERVICE/gammu-dummy"

mkdir -p $sms $DUMMY_PATH/sms/1
mkdir -p $sms $DUMMY_PATH/sms/2
mkdir -p $sms $DUMMY_PATH/sms/3
mkdir -p $sms $DUMMY_PATH/sms/4
mkdir -p $sms $DUMMY_PATH/sms/5

for sms in 62 68 74 ; do
    cp /home/vincent/Gofood/gammu-1.42.0/smsd/../tests/at-sms-encode/$sms.backup $DUMMY_PATH/sms/1/$sms
done
cp /home/vincent/Gofood/gammu-1.42.0/smsd/../tests/smsbackups/mms.smsbackup $DUMMY_PATH/sms/1/42

# Insert message manually
case $SERVICE in
    *sqlite3)
        echo "INSERT INTO outbox(DestinationNumber,TextDecoded,CreatorID,Coding) VALUES('800123465', 'This is a SQL test message', 'T3st', 'Default_No_Compression');" | SQLITE_BIN-NOTFOUND smsd.db
        ;;
    *pgsql)
        echo "INSERT INTO outbox(\"DestinationNumber\",\"TextDecoded\",\"CreatorID\",\"Coding\") VALUES('800123465', 'This is a SQL test message', 'T3st', 'Default_No_Compression');" | PGPASSWORD="smsd" "PSQL_BIN-NOTFOUND" -h "127.0.0.1" -U "smsd" "smsd"
        ;;
    *mysql|odbc)
        echo "INSERT INTO outbox(DestinationNumber,TextDecoded,CreatorID,Coding) VALUES('800123465', 'This is a SQL test message', 'T3st', 'Default_No_Compression');" | "MYSQL_BIN-NOTFOUND" "-usmsd" "-h127.0.0.1" "-psmsd" "smsd"
        ;;
    files*)
        cp /home/vincent/Gofood/gammu-1.42.0/smsd/tests/OUT+4201234567890.txt /home/vincent/Gofood/gammu-1.42.0/build/smsd/smsd-test-$SERVICE/outbox/
        ;;
esac

$SMSD_INJECT_CMD -c "$CONFIG_PATH" TEXT 123465 -text "Lorem ipsum." &
$SMSD_INJECT_CMD -c "$CONFIG_PATH" TEXT 123465 -text "Lorem ipsum." &
$SMSD_INJECT_CMD -c "$CONFIG_PATH" USSD "*127*1#"

$SMSD_CMD -c "$CONFIG_PATH" $SMSD_EXTRA_PARAMS &
SMSD_PID=$!

sleep 5

# Incoming messages
for sms in 10 16 26 ; do
    cp /home/vincent/Gofood/gammu-1.42.0/smsd/../tests/at-sms-encode/$sms.backup $DUMMY_PATH/sms/3/$sms
done
cp /home/vincent/Gofood/gammu-1.42.0/smsd/../tests/smsbackups/mms-part.smsbackup $DUMMY_PATH/sms/1/666

TIMEOUT=0
while ! $SMSD_MONITOR_CMD -C -c "$CONFIG_PATH" -n 1 -d 0 | grep -q "$TEST_MATCH" ; do
    $SMSD_MONITOR_CMD -C -c "$CONFIG_PATH" -n 1 -d 0
    sleep 5
    TIMEOUT=$(($TIMEOUT + 1))
    if [ $TIMEOUT -gt 60 ] ; then
        echo "ERROR: Wrong timeout!"
        exit 1
    fi
done

sleep 5

$SMSD_MONITOR_CMD -C -c "$CONFIG_PATH" -n 1 -d 0

if [ `wc -l < /home/vincent/Gofood/gammu-1.42.0/build/smsd/smsd-test-$SERVICE/received.log` -ne $((8 + $INCOMING_USSD)) ] ; then
    echo "ERROR: Wrong number of messages received!"
    exit 1
fi

if ! grep -q -F 'MMS_ADDRESS=http://mmscz/?m=m5da5a9jn210ma56q20' /home/vincent/Gofood/gammu-1.42.0/build/smsd/smsd-test-$SERVICE/env.log ; then
    echo "ERROR: Wrong MMS message received!"
    exit 1
fi

if [ $INCOMING_USSD -gt 0 ] && ! grep -q -F 'Reply for *127*1#' /home/vincent/Gofood/gammu-1.42.0/build/smsd/smsd-test-$SERVICE/env.log ; then
    echo "ERROR: Got no correct USSD reply!"
    exit 1
fi
