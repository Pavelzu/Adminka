<?php
/*
$file = fopen('theLastLogFile', 'r');
$pth = fgets($file);
fclose($file);
*/

$lines = file('PYlogs.txt');
$last_20 = array_slice($lines , -10);

$i = 0;
for (; $i < 10; $i++) {
    echo $last_20[$i];
    echo '<br>';
}

?>