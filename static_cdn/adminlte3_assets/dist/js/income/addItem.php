<?php

header('Access-Control-Allow-Origin: *');
if ($_SERVER['REQUEST_METHOD'] == 'OPTIONS') {
    $headers=getallheaders();
    @$ACRH=$headers["Access-Control-Request-Headers"];
    header("Access-Control-Allow-Headers: $ACRH");
}

header("Access-Control-Allow-Methods: GET, POST, OPTIONS, PUT, DELETE");

// Get the new user data and JSON file name from the request
$newUserData = $_POST['jsonData'];
$jsonFileName = $_POST['jsonFile'];
// Read the existing JSON file
$data = file_get_contents($jsonFileName);
$users = json_decode($data, JSON_NUMERIC_CHECK);

$users[] = $newUserData;

// Encode the data back to JSON
$jsonString = json_encode($users, JSON_NUMERIC_CHECK);

// Write the JSON string to the file
file_put_contents($jsonFileName, $jsonString);

// Return the updated JSON data
echo $jsonString;
?>