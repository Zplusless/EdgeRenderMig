echo "%CPU,%MEM" > cpu_test.csv
pid=1    #Can be change by yourself
while true              
    do
        cpu_user=`top -b -n 1 | grep Cpu | awk '{print $2}' | cut -f 1 -d "%"`
        cpu_system=`top -b -n 1 | grep Cpu | awk '{print $4}' | cut -f 1 -d "%"`
        mem_sys_used=`free | grep Mem | awk '{print $3}'`
        echo $cpu_user,$cpu_system,$mem_sys_used >> cpu_test.csv
        sleep 0.1    #delay time
done

