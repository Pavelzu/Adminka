<?php


$email = $_POST['email'];

if ($email=="")
{
	echo "Empty request";
	exit();
}

if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    echo $email." is invalid address";
	exit();
}

if ($email=="galsync@domen.ru")
{
	echo "Are you jobnutiy?!";
	exit();
}

$s = 'python3 ./stuff/SendGalaSynchv2.py -e '.strval($email).' 2>&1';

$last_line = exec( $s , $return_var);




$outputMessage = "";
for ($i = 0; $i < count($return_var); $i++) {
 $outputMessage = $outputMessage."\n".$return_var[$i];
}

if (stripos($outputMessage,"_XForm_query_display"))
{
	echo "Please, try again";
}
else
{
 echo $outputMessage;
}

?>
