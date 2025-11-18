<?php


$ip = $_POST['ip'];
$login = $_POST['login'];
$dst = $_POST['dst'];
$mask = $_POST['mask'];
$comment = $_POST['comment'];
$time = $_POST['time'];
$date = $_POST['date'];

if ($ip == "" || $login == "" || $dst == "" )
{
	echo "Empty request";
	exit();
}

$last_line = exec("host ".$dst.".domen.ru" , $return_var);
if (str_contains($last_line, "not found"))
{
	echo "Remote Host not found in DNS";
	exit();
}
echo $date;
if ($date)
	if (preg_match("/\d\.0\d/", $date))
	{		
		echo "No zero in mounth, please";
		exit();
	}
	if (preg_match("/[^0-9,-;]/", $date))
	{		
		echo "Only numeric and , and - and ;  please";
		exit();
	}
	if (!preg_match("/(?:(\d+,)+\d+\.\d{1,2})|(?:\d+-\d+\.\d{1,2})|(?:\d+\.\d{1,2})/", $date) && $date != "")
	{		
		echo "Sims like wrong date/dates";
		exit();
	}
	
	
	
	

$pattern = "/\d+\.\d+\.\d+\.\d+/";
$op = preg_match($pattern, $last_line, $matches);
$resolv =  $matches[0];
#echo $last_line 

$fix = "false";
if ($mask == "32")
	$fix = "true";

$comment = $comment." sc{time:|".$time."|";
if ($date == "")
{
	$comment = $comment."}";
}
else 
{
	$comment = $comment.",date:|".$date."|}";
}

$s = 'python3 ./stuff/WG.py -d '.$dst.'.domen.ru -r '.$resolv.' -a '.$ip.' -l '.$login.' -c "'.$comment.'" -f '.$fix.' 2>&1';
//echo $s;

$last_line = exec( $s , $return_var);

$outputMessage = "";
for ($i = 0; $i < count($return_var); $i++) {
 $outputMessage = $outputMessage."\n".$return_var[$i];
}
 echo $outputMessage;


?>
