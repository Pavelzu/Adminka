<?php

$fio = $_POST['fio'];

if ($fio=="")
{
	echo "Empty request";
	exit();
}


$fd = fopen("./stuff/pc-owner.txt", 'r') or die("не удалось открыть файл");
while(!feof($fd))
{
    $str = fgets($fd);
	if (strripos($str,$fio))
		{
		echo(explode(' ', $str )[0]);
		fclose($fd);
		exit (0);
		} 

}
fclose($fd);
echo("Not Found");





?>
