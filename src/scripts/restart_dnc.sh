pid=`netstat -anp|grep 8000|awk '{print $7}'|awk -F/ '{print $1}'`
kill -9 $pid
python start_dnc.py