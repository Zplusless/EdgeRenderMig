pid=`netstat -anp|grep python|awk '{print $7}'|awk -F/ '{print $1}'`
kill -9 $pid