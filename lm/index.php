<?php
echo ('
<title>Adminka</title>
<style>p {
  ;
 } .label{margin-left: 30px;}</style>
<script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
  <meta charset="UTF-8">

   <br>
	
	<form id="checkform">
	<h1 class="label">Check LM service status by hostname or IP <br> </h1>
	<table width="500" border =0 >
		<colgroup>
		<col style="width: 40%;">
		<col style="width: 60%;">
	 	 </colgroup>
		<tr>
		  <td> <label class="label">Hostname/IP</label></td>
		  <td><input type="text" name="host" value="" size= 30></td>
	      <td><input type="submit" name="sendbtn0" value="Check" ></td>
		</tr>
	</table>
		<br>
	</form>
	
	<br>
	<form id="restartform">
	<h1 class="label"> Restart LM service by hostname or IP <br> </h1>
	<table width="500" border =0 >
		<colgroup>
		<col style="width: 40%;">
		<col style="width: 60%;">
	 	 </colgroup>
		<tr>
		  <td><label class="label">Hostname/IP</label></td>
		  <td><input type="text" name="host" value="" size= 30></td>
	      <td><input type="submit" name="sendbtn1" value="Restart" ></td>
		</tr>

		
	</table>
		<br>
		
	</form>
	<form id="reinstallform">
	<h1 class="label"> <br>Reinstall LM by hostname or IP <br> </h1>
	<table width="500" border =0 >
		<colgroup>
		<col style="width: 40%;">
		<col style="width: 60%;">
	 	 </colgroup>
		<tr>
		  <td><label class="label">Hostname/IP</label></td>
		  <td><input type="text" name="host" value="" size= 30></td>
	      <td><input type="submit" name="sendbtn2" value="Reinstall" ></td>
		</tr>

		
	</table>
		<br>


	</form>

');

$fios = array();
$fd = fopen("./stuff/pc-owner.txt", 'r') or die("не удалось открыть файл");
while(!feof($fd))
{
    $str = fgets($fd);
	explode( ' ', $str );
   array_push($fios,explode(' ', $str )[1],explode(' ', $str )[2]);

}
fclose($fd);

/*
foreach ($fios as $row) {
	echo $row ;
}
*/
//echo(var_dump($fios));



echo ('
	<form id="searchform">
		<h1 class="label"> <br>Find PC by User <br> </h1>
		<table width="500" border =0 >
			<colgroup>
			<col style="width: 40%;">
			<col style="width: 60%;">
			 </colgroup>
			<tr>
			  <td><label class="label">Part of Surname (En/Ru)</label></td>
			  <td><input type="text" name="fio" value="" size= 30 list="niggers"></td>
			  <datalist id="niggers">
			  ');
				foreach ($fios as $row)
				{
					echo ('<option value="'.$row.'">'.$row.'</option>');
				}
echo ('
			  </datalist>
			  <td><input type="submit" name="sendbtn3" value="Find" ></td>
			</tr>


		</table>
			<br>
		</form>


');

echo ('
<script>
$("#checkform").on("submit", function(){
	var myButton = document.getElementsByName("sendbtn0")[0];
	myButton.setAttribute("disabled", "");
	
	$.ajax({

		url: "handlerLMServiceCheck.php",
		method: "post",
		dataType: "html",
		data: $(this).serialize(),
		success: function(data){
			alert(data);
			myButton.removeAttribute("disabled");
			

		}

	});

	return false;

});
</script>



<script>
$("#restartform").on("submit", function(){
	var myButton = document.getElementsByName("sendbtn1")[0];
	myButton.setAttribute("disabled", "");
	
	$.ajax({

		url: "handlerLMServiceRestart.php",
		method: "post",
		dataType: "html",
		data: $(this).serialize(),
		success: function(data){
			alert(data);
			myButton.removeAttribute("disabled");
			

		}

	});

	return false;

});
</script>

<script>
$("#reinstallform").on("submit", function(){
	
	const result = confirm("Are you shure?");
	
	var myButton = document.getElementsByName("sendbtn2")[0];
	myButton.setAttribute("disabled", "");
	if (result) {
	$.ajax({

		url: "handlerLMReinstall.php",
		method: "post",
		dataType: "html",
		data: $(this).serialize(),
		success: function(data){
			alert(data);
			myButton.removeAttribute("disabled");
		}

	});
	}
	return false;

});
</script>


<script>
$("#searchform").on("submit", function(){
	var myButton = document.getElementsByName("sendbtn3")[0];
	myButton.setAttribute("disabled", "");
	
	$.ajax({

		url: "handlerSearch.php",
		method: "post",
		dataType: "html",
		data: $(this).serialize(),
		success: function(data){
			alert(data);
			myButton.removeAttribute("disabled");
			

		}

	});

	return false;

});
</script>

	
	');
?>