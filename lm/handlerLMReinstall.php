<?php


$host = $_POST['host'];

if ($host=="")
{
	echo "Empty request";
	exit();
}


$s = 'python3 ./stuff/LMReinstaller.py -t '.strval($host).' 2>&1';
//echo $s;

//$s = 'python3 main.py "'.strval($result).'" > /dev/null 2>&1 & echo $!; ';
$last_line = exec( $s , $return_var);

$outputMessage = "";
for ($i = 0; $i < count($return_var); $i++) {
 $outputMessage = $outputMessage."\n".$return_var[$i];
}
 echo $outputMessage;


?>
