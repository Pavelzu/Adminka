<?php

//echo "Just wait";
$s = 'python3 ./stuff/WatchDog.py';
$last_line = exec( $s , $return_var);
//sleep(5);
header("Location: http://adminka.domen.ru/remotenotebooks/");
//echo '<br><a href="http://adminka.domen.ru/remotenotebooks"> OK </a>'
?>
